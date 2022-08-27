import array
import io
import itertools
import math

import meltysynth as ms

file = open("TimGM6mb.sf2", "rb")

a = ms.SoundFont(file)

print(len(a.aaaa.samples))
