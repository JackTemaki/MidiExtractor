import os
import pickle
from os import path
import midi

from src.constants import InstrumentCategory, Instrument, category_from_program, instrument_from_program
from src.file_handling import FilePath, recursive_scanner
from src.midi import read_midi


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

    def store_track_as_file(self, base_path : FilePath):

        pattern = midi.Pattern()

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

    def export(self, filename):
        print("Export database to %s" % filename)
        pickle.dump(self, open(filename, "wb"))