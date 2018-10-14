from src.database import get_container_list_from_file
from src.file_handling import FilePath
from src.midi_player import MidiPlayer

import time

path = FilePath("", "", "test.mid")
instruments = get_container_list_from_file(path,with_track=True)
track_header = instruments[0]

midi_player = MidiPlayer()
midi_player.play_track(track_header)


time.sleep(100)







