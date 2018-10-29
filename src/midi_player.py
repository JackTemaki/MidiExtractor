from midi import NoteOnEvent, NoteOffEvent

from src.database import TrackContainer
from src.fluidsynth import Synth, Sequencer


class MidiPlayer():

    def __init__(self, driver='alsa'):
        self.fsynth = Synth(gain=0.4)
        self.fsynth.start(driver=driver)
        sfid = self.fsynth.sfload("/usr/share/soundfonts/FluidR3_GM.sf2")
        self.fsynth.program_select(0, sfid, 0, 0)

    def play_track(self, track_header : TrackContainer):
        seq = Sequencer(time_scale=track_header.resolutuion)
        synthID = seq.register_fluidsynth(self.fsynth)
        track = track_header.track
        current = seq.get_tick()
        for event in track:
            if isinstance(event, NoteOnEvent):
                seq.note_on(current + event.tick, 0, event.pitch, event.velocity, dest=synthID)
            if isinstance(event, NoteOffEvent):
                seq.note_off(current + event.tick, 0, event.pitch)

    def play_matrix(self, matrix, resolution):
        seq = Sequencer(time_scale=resolution)
        synthID = seq.register_fluidsynth(self.fsynth)
        current = seq.get_tick()
        for j, column in enumerate(matrix):
            for i,note in enumerate(column):
                if note >= 1.0:
                    seq.note(current+j,0,i,90, 2, dest=synthID)
