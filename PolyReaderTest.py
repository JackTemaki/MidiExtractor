import midi
import re
import os
from os import walk, path

from constants import *
from typing import List

import pickle

class FilePath(object):
    """
    Descriptor for simplifying file path operations
    """

    base_path = ""

    def __init__(self, relative_path : str, filename : str, base_path : str = None):
        self.relative_path = relative_path
        self.filename = filename
        if base_path:
            self.base_path = base_path

    def get_relative_file(self):
        return self.relative_path + self.filename

    def get_absolute_file(self):
        return self.base_path + self.relative_path + self.filename


class DatabaseContainer(object):
    """
    Database Entry without the actual track data
    """

    def __init__(self, track : midi.Track,
                 is_drum : bool,
                 file_id : int,
                 relative_file_path : str,
                 file_name : str,
                 resolution : int):

        self.is_drum = is_drum
        self.file_id = file_id
        self.relative_file_path = relative_file_path
        self.file_name = file_name
        self.resolutuion = resolution

        self.category = InstrumentCategory.UNKNOWN
        self.instrument = Instrument.UNKNOWN
        self.name = "Unknown"
        self.channel = -1
        self.duration = -1

        #extract track meta information
        for event in track:
            if isinstance(event, midi.EndOfTrackEvent):
                self.duration = event.tick
            if isinstance(event, midi.TrackNameEvent):
                self.name = event.text
            if isinstance(event, midi.ProgramChangeEvent):
                self.category = category_from_program(event.get_value())
                self.instrument = instrument_from_program(event.get_value())

            # first note is never before meta, we also assume single channel tracks
            if isinstance(event, midi.NoteOnEvent):
                self.channel = event.channel + 1
                break



class TrackContainer(DatabaseContainer):
    """
    Database entry with actual track data
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.track = kwargs['track']

    def store_track_as_file(self, base_path):
        pattern = midi.Pattern()
        self.track.make_ticks_rel()
        pattern.append(self.track)
        folder_path = base_path + self.relative_file_path
        if not path.exists(folder_path):
            os.makedirs(folder_path)

        if self.is_drum:
            export_filename = self.file_name[:-4] + "-" + str(self.file_id) + "-drum.mid"
        else:
            export_filename = self.file_name[:-4] + "-" + str(self.file_id) + "-" + self.category.name + "-" + self.instrument.name + ".mid"

        midi.write_midifile(midifile=folder_path + export_filename, pattern=pattern)


def print_track_info(track):
    print("Track information:")
    for event in track:
        if isinstance(event, midi.EndOfTrackEvent):
            print("Eot: %i" % event.tick)
        if isinstance(event, midi.TrackNameEvent):
            print("Name: %s" % event.text)
        if isinstance(event, midi.ProgramChangeEvent):
            print("Program Category: %s" % category_from_program(event.get_value()))
            print("Program Instrument: %s" % instrument_from_program(event.get_value()))
        if isinstance(event, midi.NoteOnEvent):
            print("Channel (1-based): %i" % (event.channel+1))
            break
    print()


def extract_valid_tracks(midi_content):
    instrument_tracks = []
    drum_tracks = []

    for track in midi_content:
        track.make_ticks_abs()
        for event in track:
            if isinstance(event, midi.EndOfTrackEvent):
                if event.tick == 0:
                    break
            if isinstance(event, midi.NoteOnEvent):
                # channel #10 (9 for 0-base) is drum-channel
                if event.channel == 9:
                    drum_tracks.append(track)
                else:
                    instrument_tracks.append(track)
                break

    return instrument_tracks, drum_tracks

def read_midi(file):

    midi_content = midi.read_midifile(file)
    resolution = midi_content.resolution

    instrument_tracks, drum_tracks = extract_valid_tracks(midi_content)

    """
    print("number of valid instrument-tracks: %i" % len(instrument_tracks))
    for track in instrument_tracks:
        print_track_info(track)

    print("number of valid drum-tracks: %i" % len(drum_tracks))
    for track in drum_tracks:
        print_track_info(track)
    """

    return instrument_tracks, drum_tracks, resolution

def scan_library(relative_base_path : str):

    base_path = path.abspath(relative_base_path) + "/"
    FilePath.base_path = base_path

    def recursive_scanner(base_path : str, short_path : str):
        files = []
        f = []
        d = []
        for (dirpath, dirnames, filenames) in walk(base_path + short_path):
            f.extend(filenames)
            d.extend(dirnames)
            break

        for file in f:
            if (re.match('(.*).mid', file) != None):
                files = files + [FilePath(short_path, file)]

        for directory in d:
            files.extend(recursive_scanner(
                base_path, short_path + directory + "/"))

        return files

    file_paths = recursive_scanner(base_path, "")
    return file_paths, base_path


def get_container_list_from_file(filepath : FilePath, with_track=False):
    Container = TrackContainer if with_track else DatabaseContainer
    container_list = []
    instruments, drums, resolution = read_midi(filepath.get_absolute_file())
    for i, instrument_track in enumerate(instruments):
        container = Container(track=instrument_track,
                                      is_drum=False,
                                      file_id=i,
                                      relative_file_path=filepath.relative_path,
                                      file_name=filepath.filename,
                                      resolution=resolution)

        container_list.append(container)
    for i, drum_track in enumerate(drums):
        container = Container(track=drum_track,
                                      is_drum=True,
                                      file_id=i,
                                      relative_file_path=filepath.relative_path,
                                      file_name=filepath.filename,
                                      resolution=resolution)
        container_list.append(container)

    return container_list

class Database(object):
    def __init__(self, base_path, file_paths : List[FilePath]):
        self.base_path = base_path
        self.track_db = []
        for fp in file_paths:
            container_list = get_container_list_from_file(fp, with_track=False)
            self.track_db.extend(container_list)

    def export(self, filename):
        pickle.dump(self, open(filename, "wb"))

#read_midi("mz_311_1.mid")
#read_midi("Enter_Sandman_1.mid")
#file_paths, base_path = scan_library("data/Metal_Rock_rock.freemidis.net_MIDIRip/midi/m/metallica/")

#db = Database(base_path, file_paths)
#db.export("metallica.db")
db = pickle.load(open("metallica.db", "rb"))

if isinstance(db, Database):
    marked_tracks = []
    needed_files = {}
    for track_head in db.track_db:
        # match track requirements
        if track_head.category == InstrumentCategory.GUITAR and track_head.is_drum == False:
            marked_tracks.append(track_head)
            needed_files[db.base_path + track_head.relative_file_path + track_head.file_name] = FilePath(track_head.relative_file_path,
                                                                                                         track_head.file_name,
                                                                                                         db.base_path)

    for fp in needed_files.values():
        container_list = get_container_list_from_file(fp, with_track=True)
        for track_container in container_list:
            if track_container.category == InstrumentCategory.GUITAR and track_container.is_drum == False:
                track_container.store_track_as_file("metallica_guitars/")

