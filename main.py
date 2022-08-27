import io
import meltysynth as ms

file = open("TimGM6mb.sf2", "rb")

a = ms.SoundFont(file)

print(len(a.aaaa.samples))