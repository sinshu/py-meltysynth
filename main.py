from collections.abc import Sequence

import meltysynth as ms



def write_pcm(left: Sequence[float], right: Sequence[float], path: str) -> None:

    max_value = 0.0

    for t in range(len(left)):

        if abs(left[t]) > max_value:
            max_value = abs(left[t])
        
        if abs(right[t]) > max_value:
            max_value = abs(right[t])
    
    a = 0.99 / max_value

    pcm = open(path, "wb")

    for t in range(len(left)):

        sample_left = int(32768 * a * left[t])
        sample_right = int(32768 * a * right[t])
        pcm.write(sample_left.to_bytes(2, byteorder="little", signed=True))
        pcm.write(sample_right.to_bytes(2, byteorder="little", signed=True))

    pcm.close()



sf2 = open("TimGM6mb.sf2", "rb")
sound_font = ms.SoundFont(sf2)
sf2.close()

settings = ms.SynthesizerSettings(44100)

synthesizer = ms.Synthesizer(sound_font, settings)

left = ms.create_buffer(3 * settings.sample_rate)
right = ms.create_buffer(3 * settings.sample_rate)

synthesizer.note_on(0, 60, 100)
synthesizer.note_on(0, 64, 100)
synthesizer.note_on(0, 67, 100)

synthesizer.render(left, right)

write_pcm(left, right, "out.pcm")
