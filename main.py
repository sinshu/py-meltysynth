import array
import io
import itertools
import math

import meltysynth as ms

file = open("TimGM6mb.sf2", "rb")
sf2 = ms.SoundFont(file)
file.close()

print(sf2.info.bank_name)
