import midi



def read_midi(file):

    midi_content = midi.read_midifile(file)
    resolution = midi_content.resolution

    for track in midi_content:
        track.make_ticks_abs()

        for event in track:
            if isinstance(event, midi.SmpteOffsetEvent):
                print("OFFSET")
                print("Tick: " + str(event.tick))
                print("Data: " + str(event.data))
            if isinstance(event, midi.EndOfTrackEvent):
                if event.tick == 0:
                    break
                print("EOT")
                print("Tick: " + str(event.tick))
                print("Data: " + str(event.data))

            if isinstance(event, midi.TrackNameEvent):
                print("NAME")
                print(event.text)





read_midi("../../data/mz_311_1.mid")