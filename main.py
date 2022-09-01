from array import array
from collections.abc import Sequence

import meltysynth as ms



def write_pcm_interleaved_int16(left: Sequence[float], right: Sequence[float], path: str) -> None:

    max_value = 0.0

    for t in range(len(left)):

        if abs(left[t]) > max_value:
            max_value = abs(left[t])
        
        if abs(right[t]) > max_value:
            max_value = abs(right[t])
    
    a = 0.99 / max_value

    data = array("h")

    for t in range(len(left)):

        sample_left = int(32768 * a * left[t])
        sample_right = int(32768 * a * right[t])

        data.append(sample_left)
        data.append(sample_right)

    pcm = open(path, "wb")
    pcm.write(data)
    pcm.close()



def simple_chord() -> None:

    # Load the SoundFont.
    sf2 = open("TimGM6mb.sf2", "rb")
    sound_font = ms.SoundFont(sf2)
    sf2.close()

    # Create the synthesizer.
    settings = ms.SynthesizerSettings(44100)
    synthesizer = ms.Synthesizer(sound_font, settings)

    # Play some notes (middle C, E, G).
    synthesizer.note_on(0, 60, 100)
    synthesizer.note_on(0, 64, 100)
    synthesizer.note_on(0, 67, 100)

    # The output buffer (3 seconds).
    left = ms.create_buffer(3 * settings.sample_rate)
    right = ms.create_buffer(3 * settings.sample_rate)

    # Render the waveform.
    synthesizer.render(left, right)

    # Save the waveform as a raw PCM file.
    write_pcm_interleaved_int16(left, right, "out.pcm")



def main() -> None:
    simple_chord()



if __name__ == "__main__":
    main()
