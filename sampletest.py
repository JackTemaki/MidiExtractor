import tensorflow
import numpy
from src.midi_player import MidiPlayer

RESOLUTION = 16
BARS = 32

l = RESOLUTION*BARS*4
w = 127
prob_matrix = numpy.zeros((l, w))

vertical_energy = numpy.zeros((w))

def moll(vertical_energy):
    vertical_energy[72:85] = numpy.asarray([7, 0, 2, 3, 0, 5, 0, 4, 2, 0, 3, 0, 4]) * 0.5
    vertical_energy[60:72] = numpy.asarray([7, 0, 2, 3, 0, 5, 0, 4, 2, 0, 3, 0])
    vertical_energy[48:60] = numpy.asarray([7, 0, 2, 3, 0, 5, 0, 4, 2, 0, 3, 0]) * 0.5
    return vertical_energy

def dur(vertical_energy):
    vertical_energy[72:85] = numpy.asarray([7, 0, 2, 0, 3, 5, 0, 4, 0, 3, 0, 2, 4]) * 0.5
    vertical_energy[60:72] = numpy.asarray([7, 0, 2, 0, 3, 5, 0, 4, 0, 3, 0, 2])
    vertical_energy[48:60] = numpy.asarray([7, 0, 2, 0, 3, 5, 0, 4, 0, 3, 0, 2]) * 0.5
    return vertical_energy

vertical_energy = moll(vertical_energy)
#vertical_energy = dur(vertical_energy)
vertical_energy = vertical_energy / numpy.sum(vertical_energy)

results = numpy.random.uniform(0,1,(l))

horizontal_probs = numpy.zeros((RESOLUTION*4))
horizontal_probs[0] = 1
horizontal_probs[[16, 32, 48]] = 0.8
horizontal_probs[[8, 24, 40, 56]] = 0.5
horizontal_probs[[4, 12, 20, 28, 36, 44, 52, 60]] = 0.25
horizontal_probs[[i+2 for i in range(0,60,4)]] = 0.1

horizontal_probs = numpy.tile(horizontal_probs, BARS)

hits = numpy.where(results < horizontal_probs, 1, 0)

print(horizontal_probs)

print(prob_matrix.shape)
print(results.shape)

for i in range(l):
    if hits[i] == 1:
        res = numpy.argmax(numpy.random.multinomial(1, vertical_energy))
        prob_matrix[i,res] = 1

midi_player = MidiPlayer()

midi_player.play_matrix(prob_matrix, 16)

import time
time.sleep(100)
