# Py-MeltySynth

Py-MeltySynth is a SoundFont MIDI synthesizer written in pure Python, ported from [MeltySynth for C#](https://github.com/sinshu/meltysynth).



## Demo

https://www.youtube.com/watch?v=Pheb0pSzQP8  

[![Demo video](https://img.youtube.com/vi/Pheb0pSzQP8/0.jpg)](https://www.youtube.com/watch?v=Pheb0pSzQP8)



## Development status

It works, but it's slow. Without external libraries, sample-by-sample audio processing seems tough for Python... To improve the performance, the core audio processing part should be rewritten with NumPy or something like that.



## Examples

An example code to synthesize a simple chord:

```python
import meltysynth as ms

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
```

Another example code to synthesize a MIDI file. It will take a long time 😉

```python
import meltysynth as ms

# Load the SoundFont.
sf2 = open("TimGM6mb.sf2", "rb")
sound_font = ms.SoundFont(sf2)
sf2.close()

# Create the synthesizer.
settings = ms.SynthesizerSettings(44100)
synthesizer = ms.Synthesizer(sound_font, settings)

# Load the MIDI file.
mid = open("flourish.mid", "rb")
midi_file = ms.MidiFile(mid)
mid.close()

# Create the MIDI sequencer.
sequencer = ms.MidiFileSequencer(synthesizer)
sequencer.play(midi_file, False)

# The output buffer.
left = ms.create_buffer(int(settings.sample_rate * midi_file.length))
right = ms.create_buffer(int(settings.sample_rate * midi_file.length))

# Render the waveform.
sequencer.render(left, right)
```



## Todo

* __Wave synthesis__
    - [x] SoundFont reader
    - [x] Waveform generator
    - [x] Envelope generator
    - [x] Low-pass filter
    - [x] Vibrato LFO
    - [x] Modulation LFO
* __MIDI message processing__
    - [x] Note on/off
    - [x] Bank selection
    - [x] Modulation
    - [x] Volume control
    - [x] Pan
    - [x] Expression
    - [x] Hold pedal
    - [x] Program change
    - [x] Pitch bend
    - [x] Tuning
* __Effects__
    - [ ] Reverb
    - [ ] Chorus
* __Other things__
    - [x] Standard MIDI file support
    - [ ] Loop extension support
    - [ ] Performace optimization



## License

Py-MeltySynth is available under [the MIT license](LICENSE.txt).
