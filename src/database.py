import os
import pickle
from os import path
from typing import List
import midi

from src.constants import InstrumentCategory, Instrument, category_from_program, instrument_from_program
from src.file_handling import FilePath, recursive_scanner
from src.midi import read_midi
from src.conditions import ConditionManager


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
                program = event.get_value()
                if program > 127 or program < 0:
                    program = 0
                self.category = category_from_program(program)
                self.instrument = instrument_from_program(program)

            if isinstance(event, midi.TimeSignatureEvent):
                self.numerator = event.numerator
                self.denominator = event.denominator
                print("%i/%i" % (self.numerator, self.denominator))
                self.metronome = event.metronome
                self.thirties  = event.thirtyseconds

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

        # explicitely store track
        self.track = kwargs['track']

    def store_track_as_file(self, base_path : str):

        pattern = midi.Pattern()

        pattern.resolution = self.resolutuion
        # ticks need to be relative for export
        self.track.make_ticks_rel()
        pattern.append(self.track)

        # create folder if it does not exist
        folder_path = base_path + self.relative_file_path
        if not path.exists(folder_path):
            os.makedirs(folder_path)

        # build filename
        if self.is_drum:
            export_filename = self.file_name[:-4] + "-" + str(self.file_id) + "-drum.mid"
        else:
            export_filename = self.file_name[:-4] + "-" + str(self.file_id) + "-" + self.category.name + "-" + self.instrument.name + ".mid"

        midi.write_midifile(midifile=folder_path + export_filename, pattern=pattern)


def get_container_list_from_file(filepath : FilePath, with_track=False):
    Container = TrackContainer if with_track else DatabaseContainer
    container_list = []

    try:
        instruments, drums, resolution = read_midi(filepath.get_absolute_file())
    except:
        return []

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
    """
    Database object storing all track info, can be pickled into a file
    """
    def __init__(self, relative_base_path : str):

        # get absoulte path to db folder and set this as base path for any file path
        self.base_path = path.abspath(relative_base_path) + "/"
        FilePath.base_path = self.base_path

        print("Scanning Folders...")
        # scan the folder and return all midi paths (FilePath objects)
        file_paths = recursive_scanner(self.base_path, "")

        n_files = len(file_paths)
        print("Found %i midi files" % n_files)

        print("Creating Database...")
        print("0%", end='')

        # open all midi files and create database
        self.track_db = []
        for i, fp in enumerate(file_paths):
            if i % 100:
                print("\r%.2f %%" % ((i*100.0)/n_files), end='')
            container_list = get_container_list_from_file(fp, with_track=False)
            self.track_db.extend(container_list)

    def export(self, filename : str):
        print("Export database to %s" % filename)
        pickle.dump(self, open(filename, "wb"))

    def export_files(self, condition_manager : ConditionManager, output_path : str):
        marked_tracks = []
        needed_files = {}

        print("Read database...")
        # check database to find all files that need to be touched
        for track_head in self.track_db:
            if condition_manager.validate(track_head):
                marked_tracks.append(track_head)
                needed_files[self.base_path + track_head.relative_file_path + track_head.file_name] = FilePath(track_head.relative_file_path,
                                                                                                             track_head.file_name,
                                                                                                             self.base_path)
        n_files = len(needed_files.values())
        print("Load files and export tracks...")
        # open the files and export selected tracks
        for i,fp in enumerate(needed_files.values()):
            if i % 100:
                print("\r%.2f %%" % ((i*100.0)/n_files), end='')
            container_list = get_container_list_from_file(fp, with_track=True)
            for track_container in container_list:
                if condition_manager.validate(track_container):
                    track_container.store_track_as_file(output_path + "/")