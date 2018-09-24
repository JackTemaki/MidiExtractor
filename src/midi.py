import midi

from src.constants import category_from_program, instrument_from_program


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


def extract_valid_tracks(midi_content : midi.Pattern):
    """
    Extracts all midi tracks that actually contain notes,
    seperated for instruments and drums

    :param midi_content:
    :return:
    """
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


def read_midi(file : str):
    """
    Read midi file and return instrument tracks, drum tracks, and the resolution

    :param file:
    :return:
    """
    midi_content = midi.read_midifile(file)
    resolution = midi_content.resolution

    instrument_tracks, drum_tracks = extract_valid_tracks(midi_content)

    return instrument_tracks, drum_tracks, resolution