import io
import itertools
import math

from array import array
from collections.abc import MutableSequence
from collections.abc import Sequence
from enum import IntEnum
from io import BufferedReader
from typing import Optional



class _BinaryReaderEx:

    @staticmethod
    def read_int32(reader: BufferedReader) -> int:
        return int.from_bytes(reader.read(4), byteorder="little", signed=True)

    @staticmethod
    def read_uint32(reader: BufferedReader) -> int:
        return int.from_bytes(reader.read(4), byteorder="little", signed=False)

    @staticmethod
    def read_int16(reader: BufferedReader) -> int:
        return int.from_bytes(reader.read(2), byteorder="little", signed=True)

    @staticmethod
    def read_uint16(reader: BufferedReader) -> int:
        return int.from_bytes(reader.read(2), byteorder="little", signed=False)

    @staticmethod
    def read_int8(reader: BufferedReader) -> int:
        return int.from_bytes(reader.read(1), byteorder="little", signed=True)

    @staticmethod
    def read_uint8(reader: BufferedReader) -> int:
        return int.from_bytes(reader.read(1), byteorder="little", signed=False)

    @staticmethod
    def read_four_cc(reader: BufferedReader) -> str:

        data = bytearray(reader.read(4))

        for i, value in enumerate(data):
            if not (32 <= value and value <= 126):
                data[i] = 63 # '?'

        return data.decode("ascii")

    @staticmethod
    def read_fixed_length_string(reader: BufferedReader, length: int) -> str:

        data = reader.read(length)

        actualLength = 0
        for value in data:
            if value == 0:
                break
            actualLength += 1
        
        return data[0:actualLength].decode("ascii")
    
    @staticmethod
    def read_int16_array(reader: BufferedReader, size: int) -> Sequence[int]:

        count = int(size / 2)
        result = array("h")
        result.fromfile(reader, count)
        
        return result



class _SoundFontMath:

    @staticmethod
    def half_pi() -> float:
        return math.pi / 2
    
    @staticmethod
    def non_audible() -> float:
        return 1.0E-3
    
    @staticmethod
    def log_non_audible() -> float:
        return math.log(1.0E-3)
    
    @staticmethod
    def timecents_to_seconds(x: float) -> float:
        return math.pow(2.0, (1.0 / 1200.0) * x)
    
    @staticmethod
    def cents_to_hertz(x: float) -> float:
        return 8.176 * math.pow(2.0, (1.0 / 1200.0) * x)
    
    @staticmethod
    def cents_to_multiplying_factor(x: float) -> float:
        return math.pow(2.0, (1.0 / 1200.0) * x)
    
    @staticmethod
    def decibels_to_linear(x: float) -> float:
        return math.pow(10.0, 0.05 * x)
    
    @staticmethod
    def linear_to_decibels(x: float) -> float:
        return 20.0 * math.log10(x)
    
    @staticmethod
    def key_number_to_multiplying_factor(cents: int, key: int) -> float:
        return _SoundFontMath.timecents_to_seconds(cents * (60 - key))
    
    @staticmethod
    def exp_cutoff(x: float) -> float:
        if x < _SoundFontMath.log_non_audible():
            return 0.0
        else:
            return math.exp(x)
    
    @staticmethod
    def clamp(value: float, min: float, max: float) -> float:
        if value < min:
            return min
        elif value > max:
            return max
        else:
            return value



class SoundFontVersion:

    _major: int
    _minor: int

    def __init__(self, major: int, minor: int) -> None:

        self._major = major
        self._minor = minor

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor



class SoundFontInfo:
    
    _version: SoundFontVersion = SoundFontVersion(0, 0)
    _target_sound_engine: str = ""
    _bank_name: str = ""
    _rom_name: str = ""
    _rom_version: SoundFontVersion = SoundFontVersion(0, 0)
    _creation_date: str = ""
    _author: str = ""
    _target_product: str = ""
    _copyright: str = ""
    _comments: str = ""
    _tools: str = ""

    def __init__(self, reader: BufferedReader) -> None:

        chunk_id = _BinaryReaderEx.read_four_cc(reader)
        if chunk_id != "LIST":
            raise Exception("The LIST chunk was not found.")

        end = reader.tell() + _BinaryReaderEx.read_uint32(reader)

        list_type = _BinaryReaderEx.read_four_cc(reader)
        if list_type != "INFO":
            raise Exception("The type of the LIST chunk must be 'INFO', but was '" + list_type + "'.")
        
        while reader.tell() < end:

            id = _BinaryReaderEx.read_four_cc(reader)
            size = _BinaryReaderEx.read_uint32(reader)

            match id:

                case "ifil":
                    self._version = SoundFontVersion(_BinaryReaderEx.read_uint16(reader), _BinaryReaderEx.read_uint16(reader))

                case "isng":
                    self._target_sound_engine = _BinaryReaderEx.read_fixed_length_string(reader, size)

                case "INAM":
                    self._bank_name = _BinaryReaderEx.read_fixed_length_string(reader, size)

                case "irom":
                    self._rom_name = _BinaryReaderEx.read_fixed_length_string(reader, size)

                case "iver":
                    self._rom_version = SoundFontVersion(_BinaryReaderEx.read_uint16(reader), _BinaryReaderEx.read_uint16(reader))

                case "ICRD":
                    self._creation_date = _BinaryReaderEx.read_fixed_length_string(reader, size)

                case "IENG":
                    self._author = _BinaryReaderEx.read_fixed_length_string(reader, size)

                case "IPRD":
                    self._target_product = _BinaryReaderEx.read_fixed_length_string(reader, size)

                case "ICOP":
                    self._copyright = _BinaryReaderEx.read_fixed_length_string(reader, size)

                case "ICMT":
                    self._comments = _BinaryReaderEx.read_fixed_length_string(reader, size)

                case "ISFT":
                    self._tools = _BinaryReaderEx.read_fixed_length_string(reader, size)

                case _:
                    raise Exception("The INFO list contains an unknown ID '" + id + "'.")

    @property
    def version(self) -> SoundFontVersion:
        return self._version
    
    @property
    def target_sound_engine(self) -> str:
        return self._target_sound_engine
    
    @property
    def bank_name(self) -> str:
        return self._bank_name
    
    @property
    def rom_name(self) -> str:
        return self._rom_name
    
    @property
    def rom_version(self) -> SoundFontVersion:
        return self._rom_version
    
    @property
    def creation_date(self) -> str:
        return self._creation_date
    
    @property
    def author(self) -> str:
        return self._author
    
    @property
    def target_product(self) -> str:
        return self._target_product
    
    @property
    def copyright(self) -> str:
        return self._copyright
    
    @property
    def comments(self) -> str:
        return self._comments
    
    @property
    def tools(self) -> str:
        return self._tools



class _SoundFontSampleData:

    _bits_per_sample: int
    _samples: Sequence[int]

    def __init__(self, reader: BufferedReader) -> None:
        
        chunk_id = _BinaryReaderEx.read_four_cc(reader)
        if chunk_id != "LIST":
            raise Exception("The LIST chunk was not found.")
        
        end = reader.tell() + _BinaryReaderEx.read_uint32(reader)

        list_type = _BinaryReaderEx.read_four_cc(reader)
        if list_type != "sdta":
            raise Exception("The type of the LIST chunk must be 'sdta', but was '" + list_type + "'.")
        
        while reader.tell() < end:

            id = _BinaryReaderEx.read_four_cc(reader)
            size = _BinaryReaderEx.read_uint32(reader)

            match id:

                case "smpl":
                    self._bits_per_sample = 16
                    self._samples = _BinaryReaderEx.read_int16_array(reader, size)

                case "sm24":
                    reader.seek(size, io.SEEK_CUR)

                case _:
                    raise Exception("The INFO list contains an unknown ID '" + id + "'.")
        
        if self._samples is None:
            raise Exception("No valid sample data was found.")
        
    @property
    def bits_per_sample(self) -> int:
        return self._bits_per_sample

    @property
    def samples(self) -> Sequence[int]:
        return self._samples



class _GeneratorType(IntEnum):

    START_ADDRESS_OFFSET = 0
    END_ADDRESS_OFFSET = 1
    START_LOOP_ADDRESS_OFFSET = 2
    END_LOOP_ADDRESS_OFFSET = 3
    START_ADDRESS_COARSE_OFFSET = 4
    MODULATION_LFO_TO_PITCH = 5
    VIBRATO_LFO_TO_PITCH = 6
    MODULATION_ENVELOPE_TO_PITCH = 7
    INITIAL_FILTER_CUTOFF_FREQUENCY = 8
    INITIAL_FILTER_Q = 9
    MODULATION_LFO_TO_FILTER_CUTOFF_FREQUENCY = 10
    MODULATION_ENVELOPE_TO_FILTER_CUTOFF_FREQUENCY = 11
    END_ADDRESS_COARSE_OFFSET = 12
    MODULATION_LFO_TO_VOLUME = 13
    UNUSED_1 = 14
    CHORUS_EFFECTS_SEND = 15
    REVERB_EFFECTS_SEND = 16
    PAN = 17
    UNUSED_2 = 18
    UNUSED_3 = 19
    UNUSED_4 = 20
    DELAY_MODULATION_LFO = 21
    FREQUENCY_MODULATION_LFO = 22
    DELAY_VIBRATO_LFO = 23
    FREQUENCY_VIBRATO_LFO = 24
    DELAY_MODULATION_ENVELOPE = 25
    ATTACK_MODULATION_ENVELOPE = 26
    HOLD_MODULATION_ENVELOPE = 27
    DECAY_MODULATION_ENVELOPE = 28
    SUSTAIN_MODULATION_ENVELOPE = 29
    RELEASE_MODULATION_ENVELOPE = 30
    KEY_NUMBER_TO_MODULATION_ENVELOPE_HOLD = 31
    KEY_NUMBER_TO_MODULATION_ENVELOPE_DECAY = 32
    DELAY_VOLUME_ENVELOPE = 33
    ATTACK_VOLUME_ENVELOPE = 34
    HOLD_VOLUME_ENVELOPE = 35
    DECAY_VOLUME_ENVELOPE = 36
    SUSTAIN_VOLUME_ENVELOPE = 37
    RELEASE_VOLUME_ENVELOPE = 38
    KEY_NUMBER_TO_VOLUME_ENVELOPE_HOLD = 39
    KEY_NUMBER_TO_VOLUME_ENVELOPE_DECAY = 40
    INSTRUMENT = 41
    RESERVED_1 = 42
    KEY_RANGE = 43
    VELOCITY_RANGE = 44
    START_LOOP_ADDRESS_COARSE_OFFSET = 45
    KEY_NUMBER = 46
    VELOCITY = 47
    INITIAL_ATTENUATION = 48
    RESERVED_2 = 49
    END_LOOP_ADDRESS_COARSE_OFFSET = 50
    COARSE_TUNE = 51
    FINE_TUNE = 52
    SAMPLE_ID = 53
    SAMPLE_MODES = 54
    RESERVED_3 = 55
    SCALE_TUNING = 56
    EXCLUSIVE_CLASS = 57
    OVERRIDING_ROOT_KEY = 58
    UNUSED_5 = 59
    UNUSED_END = 60



class _Generator:

    _generator_type: _GeneratorType
    _value: int

    def __init__(self, reader: BufferedReader) -> None:
        
        self._generator_type = _GeneratorType(_BinaryReaderEx.read_uint16(reader))
        self._value = _BinaryReaderEx.read_int16(reader)

    @staticmethod
    def read_from_chunk(reader: BufferedReader, size: int) -> Sequence["_Generator"]:

        if int(size % 4) != 0:
            raise Exception("The generator list is invalid.")

        count = int(size / 4) - 1
        generators = list[_Generator]()

        for _ in range(count):
            generators.append(_Generator(reader))

        # The last one is the terminator.
        _Generator(reader)

        return generators
    
    @property
    def generator_type(self) -> _GeneratorType:
        return self._generator_type
    
    @property
    def value(self) -> int:
        return self._value



class _Modulator:

    @staticmethod
    def discard_data(reader: BufferedReader, size: int) -> None:

        if int(size % 10) != 0:
            raise Exception("The modulator list is invalid.")
        
        reader.seek(size, io.SEEK_CUR)



class _SampleType(IntEnum):

    NONE = 0
    MONO = 1
    RIGHT = 2
    LEFT = 4
    LINKED = 8
    ROM_MONO = 0x8001
    ROM_RIGHT = 0x8002
    ROM_LEFT = 0x8004
    ROM_LINKED = 0x8008



class SampleHeader:

    _name: str
    _start: int
    _end: int
    _start_loop: int
    _end_loop: int
    _sample_rate: int
    _original_pitch: int
    _pitch_correction: int
    _link: int
    _sample_type: _SampleType

    def __init__(self, reader: BufferedReader) -> None:
        
        self._name = _BinaryReaderEx.read_fixed_length_string(reader, 20)
        self._start = _BinaryReaderEx.read_int32(reader)
        self._end = _BinaryReaderEx.read_int32(reader)
        self._start_loop = _BinaryReaderEx.read_int32(reader)
        self._end_loop = _BinaryReaderEx.read_int32(reader)
        self._sample_rate = _BinaryReaderEx.read_int32(reader)
        self._original_pitch = _BinaryReaderEx.read_uint8(reader)
        self._pitch_correction = _BinaryReaderEx.read_int8(reader)
        self._link = _BinaryReaderEx.read_uint16(reader)
        self._sample_type = _SampleType(_BinaryReaderEx.read_uint16(reader))
    
    @staticmethod
    def _read_from_chunk(reader: BufferedReader, size: int) -> Sequence["SampleHeader"]:

        if int(size % 46) != 0:
            raise Exception("The sample header list is invalid.")
        
        count = int(size / 46) - 1
        headers = list[SampleHeader]()

        for _ in range(count):
            headers.append(SampleHeader(reader))
        
        # The last one is the terminator.
        SampleHeader(reader)

        return headers
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def start(self) -> int:
        return self._start
    
    @property
    def end(self) -> int:
        return self._end
    
    @property
    def start_loop(self) -> int:
        return self._start_loop
    
    @property
    def end_loop(self) -> int:
        return self._end_loop
    
    @property
    def sample_rate(self) -> int:
        return self._sample_rate
    
    @property
    def original_pitch(self) -> int:
        return self._original_pitch
    
    @property
    def pitch_correction(self) -> int:
        return self._pitch_correction



class _ZoneInfo:

    _generator_index: int
    _modulator_index: int
    _generator_count: int
    _modulator_count: int

    def __init__(self) -> None:
        pass

    @staticmethod
    def read_from_chunk(reader: BufferedReader, size: int) -> Sequence["_ZoneInfo"]:

        if int(size % 4) != 0:
            raise Exception("The zone list is invalid.")
        
        count = int(size / 4)
        zones = list[_ZoneInfo]()

        for i in range(count):

            zone = _ZoneInfo()
            zone._generator_index = _BinaryReaderEx.read_uint16(reader)
            zone._modulator_index = _BinaryReaderEx.read_uint16(reader)
            zones.append(zone)
        
        for i in range(count - 1):

            zones[i]._generator_count = zones[i + 1]._generator_index - zones[i]._generator_index
            zones[i]._modulator_count = zones[i + 1]._modulator_index - zones[i]._modulator_index
        
        return zones
    
    @property
    def generator_index(self) -> int:
        return self._generator_index
    
    @property
    def modulator_index(self) -> int:
        return self._modulator_index
    
    @property
    def generator_count(self) -> int:
        return self._generator_count

    @property
    def modulator_count(self) -> int:
        return self._modulator_count



class _Zone:

    _generators: Sequence[_Generator]

    def __init__(self) -> None:
        pass

    @staticmethod
    def create(infos: Sequence[_ZoneInfo], generators: Sequence[_Generator]) -> Sequence["_Zone"]:

        if len(infos) <= 1:
            raise Exception("No valid zone was found.")
        
        # The last one is the terminator.
        count = len(infos) - 1
        zones = list[_Zone]()

        for i in range(count):

            info: _ZoneInfo = infos[i]

            zone = _Zone()
            zone._generators = list[_Generator]()
            for j in range(info.generator_count):
                zone._generators.append(generators[info.generator_index + j])
            
            zones.append(zone)
        
        return zones
    
    @property
    def generators(self) -> Sequence[_Generator]:
        return self._generators



class _PresetInfo:

    _name: str
    _patch_number: int
    _bank_number: int
    _zone_start_index: int
    _zone_end_index: int
    _library: int
    _genre: int
    _morphology: int

    def __init__(self) -> None:
        pass

    @staticmethod
    def read_from_chunk(reader: BufferedReader, size: int) -> Sequence["_PresetInfo"]:

        if int(size % 38) != 0:
            raise Exception("The preset list is invalid.")
    
        count = int(size / 38)
        presets = list[_PresetInfo]()

        for i in range(count):

            preset = _PresetInfo()
            preset._name = _BinaryReaderEx.read_fixed_length_string(reader, 20)
            preset._patch_number = _BinaryReaderEx.read_uint16(reader)
            preset._bank_number = _BinaryReaderEx.read_uint16(reader)
            preset._zone_start_index = _BinaryReaderEx.read_uint16(reader)
            preset._library = _BinaryReaderEx.read_int32(reader)
            preset._genre = _BinaryReaderEx.read_int32(reader)
            preset._morphology = _BinaryReaderEx.read_int32(reader)
            presets.append(preset)

        for i in range(count - 1):
            presets[i]._zone_end_index = presets[i + 1].zone_start_index - 1
        
        return presets
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def patch_number(self) -> int:
        return self._patch_number
    
    @property
    def bank_number(self) -> int:
        return self._bank_number

    @property
    def zone_start_index(self) -> int:
        return self._zone_start_index
    
    @property
    def zone_end_index(self) -> int:
        return self._zone_end_index
    
    @property
    def library(self) -> int:
        return self._library
    
    @property
    def genre(self) -> int:
        return self._genre
    
    @property
    def morphology(self) -> int:
        return self._morphology



class _InstrumentInfo:

    _name: str
    _zone_start_index: int
    _zone_end_index: int

    def __init__(self) -> None:
        pass

    @staticmethod
    def read_from_chunk(reader: BufferedReader, size: int) -> Sequence["_InstrumentInfo"]:

        if int(size % 22) != 0:
            raise Exception("The instrument list is invalid.")
    
        count = int(size / 22)
        instruments = list[_InstrumentInfo]()

        for i in range(count):

            instrument = _InstrumentInfo()
            instrument._name = _BinaryReaderEx.read_fixed_length_string(reader, 20)
            instrument._zone_start_index = _BinaryReaderEx.read_uint16(reader)
            instruments.append(instrument)

        for i in range(count - 1):
            instruments[i]._zone_end_index = instruments[i + 1]._zone_start_index - 1
        
        return instruments

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def zone_start_index(self) -> int:
        return self._zone_start_index
    
    @property
    def zone_end_index(self) -> int:
        return self._zone_end_index



class Instrument:

    _name: str
    _regions: Sequence["InstrumentRegion"]

    def __init__(self, info: _InstrumentInfo, zones: Sequence[_Zone], samples: Sequence[SampleHeader]) -> None:
        
        self._name = info.name

        zone_count = info.zone_end_index - info.zone_start_index + 1
        if zone_count <= 0:
            raise Exception("The instrument '" + info.name + "' has no zone.")
        
        zone_span = zones[info.zone_start_index:info.zone_start_index + zone_count]

        self._regions = InstrumentRegion._create(self, zone_span, samples)

    @staticmethod
    def _create(infos: Sequence[_InstrumentInfo], zones: Sequence[_Zone], samples: Sequence[SampleHeader]) -> Sequence["Instrument"]:

        if len(infos) <= 1:
            raise Exception("No valid instrument was found.")
        
        # The last one is the terminator.
        count = len(infos) - 1
        instruments = list[Instrument]()

        for i in range(count):
            instruments.append(Instrument(infos[i], zones, samples))
        
        return instruments

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def regions(self) -> Sequence["InstrumentRegion"]:
        return self._regions



class LoopMode(IntEnum):

    NO_LOOP = 0
    CONTINUOUS = 1
    LOOP_UNTIL_NOTE_OFF = 3



class InstrumentRegion:

    _sample: SampleHeader
    _gs: MutableSequence[int]

    def __init__(self, instrument: Instrument, global_generators: Optional[Sequence[_Generator]], local_generators: Optional[Sequence[_Generator]], samples: Sequence[SampleHeader]) -> None:
        
        self._gs = array("h", itertools.repeat(0, 61))
        self._gs[_GeneratorType.INITIAL_FILTER_CUTOFF_FREQUENCY] = 13500
        self._gs[_GeneratorType.DELAY_MODULATION_LFO] = -12000
        self._gs[_GeneratorType.DELAY_VIBRATO_LFO] = -12000
        self._gs[_GeneratorType.DELAY_MODULATION_ENVELOPE] = -12000
        self._gs[_GeneratorType.ATTACK_MODULATION_ENVELOPE] = -12000
        self._gs[_GeneratorType.HOLD_MODULATION_ENVELOPE] = -12000
        self._gs[_GeneratorType.DECAY_MODULATION_ENVELOPE] = -12000
        self._gs[_GeneratorType.RELEASE_MODULATION_ENVELOPE] = -12000
        self._gs[_GeneratorType.DELAY_VOLUME_ENVELOPE] = -12000
        self._gs[_GeneratorType.ATTACK_VOLUME_ENVELOPE] = -12000
        self._gs[_GeneratorType.HOLD_VOLUME_ENVELOPE] = -12000
        self._gs[_GeneratorType.DECAY_VOLUME_ENVELOPE] = -12000
        self._gs[_GeneratorType.RELEASE_VOLUME_ENVELOPE] = -12000
        self._gs[_GeneratorType.KEY_RANGE] = 0x7F00
        self._gs[_GeneratorType.VELOCITY_RANGE] = 0x7F00
        self._gs[_GeneratorType.KEY_NUMBER] = -1
        self._gs[_GeneratorType.VELOCITY] = -1
        self._gs[_GeneratorType.SCALE_TUNING] = 100
        self._gs[_GeneratorType.OVERRIDING_ROOT_KEY] = -1

        if global_generators is not None:
            for parameter in global_generators:
                self._set_parameter(parameter)
        
        if local_generators is not None:
            for parameter in local_generators:
                self._set_parameter(parameter)
        
        id = self._gs[_GeneratorType.SAMPLE_ID]
        if not (0 <= id and id < len(samples)):
            raise Exception("The instrument '" + instrument.name + "' contains an invalid sample ID '" + str(id) + "'.")
        self._sample = samples[id]
    
    @staticmethod
    def _create(instrument: Instrument, zones: Sequence[_Zone], samples: Sequence[SampleHeader]) -> Sequence["InstrumentRegion"]:

        global_zone: Optional[_Zone] = None

        # Is the first one the global zone?
        if len(zones[0].generators) == 0 or zones[0].generators[-1].generator_type != _GeneratorType.SAMPLE_ID:
            # The first one is the global zone.
            global_zone = zones[0]
        
        if global_zone is not None:
            # The global zone is regarded as the base setting of subsequent zones.
            count = len(zones) - 1
            regions = list[InstrumentRegion]()
            for i in range(count):
                regions.append(InstrumentRegion(instrument, global_zone.generators, zones[i + 1].generators, samples))
            return regions
        else:
            # No global zone.
            count = len(zones)
            regions = list[InstrumentRegion]()
            for i in range(count):
                regions.append(InstrumentRegion(instrument, None, zones[i].generators, samples))
            return regions

    def _set_parameter(self, parameter: _Generator) -> None:

        index = int(parameter.generator_type)

        # Unknown generators should be ignored.
        if 0 <= index and index < len(self._gs):
            self._gs[index] = parameter.value
    
    def contains(self, key: int, velocity: int) -> bool:
        contains_key = self.key_range_start <= key and key <= self.key_range_end
        contains_velocity = self.velocity_range_start <= velocity and velocity <= self.velocity_range_end
        return contains_key and contains_velocity
    
    @property
    def sample(self) -> SampleHeader:
        return self._sample

    @property
    def sample_start(self) -> int:
        return self._sample.start + self.start_address_offset

    @property
    def sample_end(self) -> int:
        return self._sample.end + self.end_address_offset

    @property
    def sample_start_loop(self) -> int:
        return self._sample.start_loop + self.start_loop_address_offset

    @property
    def sample_end_loop(self) -> int:
        return self._sample.end_loop + self.end_loop_address_offset

    @property
    def start_address_offset(self) -> int:
        return 32768 * self._gs[_GeneratorType.START_ADDRESS_COARSE_OFFSET] + self._gs[_GeneratorType.START_ADDRESS_OFFSET]

    @property
    def end_address_offset(self) -> int:
        return 32768 * self._gs[_GeneratorType.END_ADDRESS_COARSE_OFFSET] + self._gs[_GeneratorType.END_ADDRESS_OFFSET]

    @property
    def start_loop_address_offset(self) -> int:
        return 32768 * self._gs[_GeneratorType.START_LOOP_ADDRESS_COARSE_OFFSET] + self._gs[_GeneratorType.START_LOOP_ADDRESS_OFFSET]

    @property
    def end_loop_address_offset(self) -> int:
        return 32768 * self._gs[_GeneratorType.END_LOOP_ADDRESS_COARSE_OFFSET] + self._gs[_GeneratorType.END_LOOP_ADDRESS_OFFSET]

    @property
    def modulation_lfo_to_pitch(self) -> int:
        return self._gs[_GeneratorType.MODULATION_LFO_TO_PITCH]

    @property
    def vibrato_lfo_to_pitch(self) -> int:
        return self._gs[_GeneratorType.VIBRATO_LFO_TO_PITCH]

    @property
    def modulation_envelope_to_pitch(self) -> int:
        return self._gs[_GeneratorType.MODULATION_ENVELOPE_TO_PITCH]

    @property
    def initial_filter_cutoff_frequency(self) -> float:
        return _SoundFontMath.cents_to_hertz(self._gs[_GeneratorType.INITIAL_FILTER_CUTOFF_FREQUENCY])

    @property
    def initial_filter_q(self) -> float:
        return 0.1 * self._gs[_GeneratorType.INITIAL_FILTER_Q]

    @property
    def modulation_lfo_to_filter_cutoff_frequency(self) -> int:
        return self._gs[_GeneratorType.MODULATION_LFO_TO_FILTER_CUTOFF_FREQUENCY]

    @property
    def modulation_envelope_to_filter_cutoff_frequency(self) -> int:
        return self._gs[_GeneratorType.MODULATION_ENVELOPE_TO_FILTER_CUTOFF_FREQUENCY]

    @property
    def modulation_lfo_to_volume(self) -> float:
        return 0.1 * self._gs[_GeneratorType.MODULATION_LFO_TO_VOLUME]

    @property
    def chorus_effects_send(self) -> float:
        return 0.1 * self._gs[_GeneratorType.CHORUS_EFFECTS_SEND]

    @property
    def reverb_effects_send(self) -> float:
        return 0.1 * self._gs[_GeneratorType.REVERB_EFFECTS_SEND]

    @property
    def pan(self) -> float:
        return 0.1 * self._gs[_GeneratorType.PAN]

    @property
    def delay_modulation_lfo(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self._gs[_GeneratorType.DELAY_MODULATION_LFO])

    @property
    def frequency_modulation_lfo(self) -> float:
        return _SoundFontMath.cents_to_hertz(self._gs[_GeneratorType.FREQUENCY_MODULATION_LFO])

    @property
    def delay_vibrato_lfo(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self._gs[_GeneratorType.DELAY_VIBRATO_LFO])

    @property
    def frequency_vibrato_lfo(self) -> float:
        return _SoundFontMath.cents_to_hertz(self._gs[_GeneratorType.FREQUENCY_VIBRATO_LFO])

    @property
    def delay_modulation_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self._gs[_GeneratorType.DELAY_MODULATION_ENVELOPE])

    @property
    def attack_modulation_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self._gs[_GeneratorType.ATTACK_MODULATION_ENVELOPE])

    @property
    def hold_modulation_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self._gs[_GeneratorType.HOLD_MODULATION_ENVELOPE])

    @property
    def decay_modulation_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self._gs[_GeneratorType.DECAY_MODULATION_ENVELOPE])

    @property
    def sustain_modulation_envelope(self) -> float:
        return 0.1 * self._gs[_GeneratorType.SUSTAIN_MODULATION_ENVELOPE]

    @property
    def release_modulation_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self._gs[_GeneratorType.RELEASE_MODULATION_ENVELOPE])

    @property
    def key_number_to_modulation_envelope_hold(self) -> int:
        return self._gs[_GeneratorType.KEY_NUMBER_TO_MODULATION_ENVELOPE_HOLD]

    @property
    def key_number_to_modulation_envelope_decay(self) -> int:
        return self._gs[_GeneratorType.KEY_NUMBER_TO_MODULATION_ENVELOPE_DECAY]

    @property
    def delay_volume_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self._gs[_GeneratorType.DELAY_VOLUME_ENVELOPE])

    @property
    def attack_volume_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self._gs[_GeneratorType.ATTACK_VOLUME_ENVELOPE])

    @property
    def hold_volume_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self._gs[_GeneratorType.HOLD_VOLUME_ENVELOPE])

    @property
    def decay_volume_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self._gs[_GeneratorType.DECAY_VOLUME_ENVELOPE])

    @property
    def sustain_volume_envelope(self) -> float:
        return 0.1 * self._gs[_GeneratorType.SUSTAIN_VOLUME_ENVELOPE]

    @property
    def release_volume_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self._gs[_GeneratorType.RELEASE_VOLUME_ENVELOPE])

    @property
    def key_number_to_volume_envelope_hold(self) -> int:
        return self._gs[_GeneratorType.KEY_NUMBER_TO_VOLUME_ENVELOPE_HOLD]

    @property
    def key_number_to_volume_envelope_decay(self) -> int:
        return self._gs[_GeneratorType.KEY_NUMBER_TO_VOLUME_ENVELOPE_DECAY]

    @property
    def key_range_start(self) -> int:
        return self._gs[_GeneratorType.KEY_RANGE] & 0xFF

    @property
    def key_range_end(self) -> int:
        return (self._gs[_GeneratorType.KEY_RANGE] >> 8) & 0xFF

    @property
    def velocity_range_start(self) -> int:
        return self._gs[_GeneratorType.VELOCITY_RANGE] & 0xFF

    @property
    def velocity_range_end(self) -> int:
        return (self._gs[_GeneratorType.VELOCITY_RANGE] >> 8) & 0xFF

    @property
    def initial_attenuation(self) -> float:
        return 0.1 * self._gs[_GeneratorType.INITIAL_ATTENUATION]

    @property
    def coarse_tune(self) -> int:
        return self._gs[_GeneratorType.COARSE_TUNE]

    @property
    def fine_tune(self) -> int:
        return self._gs[_GeneratorType.FINE_TUNE] + self._sample.pitch_correction

    @property
    def sample_modes(self) -> LoopMode:
        return LoopMode(self._gs[_GeneratorType.SAMPLE_MODES]) if self._gs[_GeneratorType.SAMPLE_MODES] != 2 else LoopMode.NO_LOOP

    @property
    def scale_tuning(self) -> int:
        return self._gs[_GeneratorType.SCALE_TUNING]

    @property
    def exclusive_class(self) -> int:
        return self._gs[_GeneratorType.EXCLUSIVE_CLASS]

    @property
    def root_key(self) -> int:
        return self._gs[_GeneratorType.OVERRIDING_ROOT_KEY] if self._gs[_GeneratorType.OVERRIDING_ROOT_KEY] != -1 else self._sample.original_pitch



class Preset:

    _name: str
    _patch_number: int
    _bank_number: int
    _library: int
    _genre: int
    _morphology: int
    _regions: Sequence["PresetRegion"]

    def __init__(self, info: _PresetInfo, zones: Sequence[_Zone], instruments: Sequence[Instrument]) -> None:
        
        self._name = info.name
        self._patch_number = info.patch_number
        self._bank_number = info.bank_number
        self._library = info.library
        self._genre = info.genre
        self._morphology = info.morphology

        zone_count = info.zone_end_index - info.zone_start_index + 1
        if zone_count <= 0:
            raise Exception("The preset '" + info.name + "' has no zone.")
        
        zone_span = zones[info.zone_start_index:info.zone_start_index + zone_count]

        self._regions = PresetRegion._create(self, zone_span, instruments)

    @staticmethod
    def _create(infos: Sequence[_PresetInfo], zones: Sequence[_Zone], instruments: Sequence[Instrument]) -> Sequence["Preset"]:

        if len(infos) <= 1:
            raise Exception("No valid preset was found.")
        
        # The last one is the terminator.
        count = len(infos) - 1
        presets = list[Preset]()

        for i in range(count):
            presets.append(Preset(infos[i], zones, instruments))
        
        return presets
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def patch_number(self) -> int:
        return self._patch_number
    
    @property
    def bank_number(self) -> int:
        return self._bank_number
    
    @property
    def library(self) -> int:
        return self._library
    
    @property
    def genre(self) -> int:
        return self._genre
    
    @property
    def morphology(self) -> int:
        return self._morphology
    
    @property
    def regions(self) -> Sequence["PresetRegion"]:
        return self._regions



class PresetRegion:

    _instrument: Instrument
    _gs: MutableSequence[int]

    def __init__(self, preset: Preset, global_generators: Optional[Sequence[_Generator]], local_generators: Optional[Sequence[_Generator]], instruments: Sequence[Instrument]) -> None:
        
        self._gs = array("h", itertools.repeat(0, 61))
        self._gs[_GeneratorType.KEY_RANGE] = 0x7F00
        self._gs[_GeneratorType.VELOCITY_RANGE] = 0x7F00

        if global_generators is not None:
            for parameter in global_generators:
                self._set_parameter(parameter)
        
        if local_generators is not None:
            for parameter in local_generators:
                self._set_parameter(parameter)
        
        id = self._gs[_GeneratorType.INSTRUMENT]
        if not (0 <= id and id < len(instruments)):
            raise Exception("The preset '" + preset.name + "' contains an invalid instrument ID '" + str(id) + "'.")
        self._instrument = instruments[id]
    
    @staticmethod
    def _create(preset: Preset, zones: Sequence[_Zone], instruments: Sequence[Instrument]) -> Sequence["PresetRegion"]:

        global_zone: Optional[_Zone] = None

        # Is the first one the global zone?
        if len(zones[0].generators) == 0 or zones[0].generators[-1].generator_type != _GeneratorType.INSTRUMENT:
            # The first one is the global zone.
            global_zone = zones[0]
        
        if global_zone is not None:
            # The global zone is regarded as the base setting of subsequent zones.
            count = len(zones) - 1
            regions = list[PresetRegion]()
            for i in range(count):
                regions.append(PresetRegion(preset, global_zone.generators, zones[i + 1].generators, instruments))
            return regions
        else:
            # No global zone.
            count = len(zones)
            regions = list[PresetRegion]()
            for i in range(count):
                regions.append(PresetRegion(preset, None, zones[i].generators, instruments))
            return regions

    def _set_parameter(self, parameter: _Generator) -> None:

        index = int(parameter.generator_type)

        # Unknown generators should be ignored.
        if 0 <= index and index < len(self._gs):
            self._gs[index] = parameter.value
    
    def contains(self, key: int, velocity: int) -> bool:
        contains_key = self.key_range_start <= key and key <= self.key_range_end
        contains_velocity = self.velocity_range_start <= velocity and velocity <= self.velocity_range_end
        return contains_key and contains_velocity
    
    @property
    def instrument(self) -> Instrument:
        return self._instrument

    @property
    def modulation_lfo_to_pitch(self) -> int:
        return self._gs[_GeneratorType.MODULATION_LFO_TO_PITCH]

    @property
    def vibrato_lfo_to_pitch(self) -> int:
        return self._gs[_GeneratorType.VIBRATO_LFO_TO_PITCH]

    @property
    def modulation_envelope_to_pitch(self) -> int:
        return self._gs[_GeneratorType.MODULATION_ENVELOPE_TO_PITCH]

    @property
    def initial_filter_cutoff_frequency(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.INITIAL_FILTER_CUTOFF_FREQUENCY])

    @property
    def initial_filter_q(self) -> float:
        return 0.1 * self._gs[_GeneratorType.INITIAL_FILTER_Q]

    @property
    def modulation_lfo_to_filter_cutoff_frequency(self) -> int:
        return self._gs[_GeneratorType.MODULATION_LFO_TO_FILTER_CUTOFF_FREQUENCY]

    @property
    def modulation_envelope_to_filter_cutoff_frequency(self) -> int:
        return self._gs[_GeneratorType.MODULATION_ENVELOPE_TO_FILTER_CUTOFF_FREQUENCY]

    @property
    def modulation_lfo_to_volume(self) -> float:
        return 0.1 * self._gs[_GeneratorType.MODULATION_LFO_TO_VOLUME]

    @property
    def chorus_effects_send(self) -> float:
        return 0.1 * self._gs[_GeneratorType.CHORUS_EFFECTS_SEND]

    @property
    def reverb_effects_send(self) -> float:
        return 0.1 * self._gs[_GeneratorType.REVERB_EFFECTS_SEND]

    @property
    def pan(self) -> float:
        return 0.1 * self._gs[_GeneratorType.PAN]

    @property
    def delay_modulation_lfo(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.DELAY_MODULATION_LFO])

    @property
    def frequency_modulation_lfo(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.FREQUENCY_MODULATION_LFO])

    @property
    def delay_vibrato_lfo(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.DELAY_VIBRATO_LFO])

    @property
    def frequency_vibrato_lfo(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.FREQUENCY_VIBRATO_LFO])

    @property
    def delay_modulation_envelope(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.DELAY_MODULATION_ENVELOPE])

    @property
    def attack_modulation_envelope(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.ATTACK_MODULATION_ENVELOPE])

    @property
    def hold_modulation_envelope(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.HOLD_MODULATION_ENVELOPE])

    @property
    def decay_modulation_envelope(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.DECAY_MODULATION_ENVELOPE])

    @property
    def sustain_modulation_envelope(self) -> float:
        return 0.1 * self._gs[_GeneratorType.SUSTAIN_MODULATION_ENVELOPE]

    @property
    def release_modulation_envelope(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.RELEASE_MODULATION_ENVELOPE])

    @property
    def key_number_to_modulation_envelope_hold(self) -> int:
        return self._gs[_GeneratorType.KEY_NUMBER_TO_MODULATION_ENVELOPE_HOLD]

    @property
    def key_number_to_modulation_envelope_decay(self) -> int:
        return self._gs[_GeneratorType.KEY_NUMBER_TO_MODULATION_ENVELOPE_DECAY]

    @property
    def delay_volume_envelope(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.DELAY_VOLUME_ENVELOPE])

    @property
    def attack_volume_envelope(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.ATTACK_VOLUME_ENVELOPE])

    @property
    def hold_volume_envelope(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.HOLD_VOLUME_ENVELOPE])

    @property
    def decay_volume_envelope(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.DECAY_VOLUME_ENVELOPE])

    @property
    def sustain_volume_envelope(self) -> float:
        return 0.1 * self._gs[_GeneratorType.SUSTAIN_VOLUME_ENVELOPE]

    @property
    def release_volume_envelope(self) -> float:
        return _SoundFontMath.cents_to_multiplying_factor(self._gs[_GeneratorType.RELEASE_VOLUME_ENVELOPE])

    @property
    def key_number_to_volume_envelope_hold(self) -> int:
        return self._gs[_GeneratorType.KEY_NUMBER_TO_VOLUME_ENVELOPE_HOLD]

    @property
    def key_number_to_volume_envelope_decay(self) -> int:
        return self._gs[_GeneratorType.KEY_NUMBER_TO_VOLUME_ENVELOPE_DECAY]

    @property
    def key_range_start(self) -> int:
        return self._gs[_GeneratorType.KEY_RANGE] & 0xFF

    @property
    def key_range_end(self) -> int:
        return (self._gs[_GeneratorType.KEY_RANGE] >> 8) & 0xFF

    @property
    def velocity_range_start(self) -> int:
        return self._gs[_GeneratorType.VELOCITY_RANGE] & 0xFF

    @property
    def velocity_range_end(self) -> int:
        return (self._gs[_GeneratorType.VELOCITY_RANGE] >> 8) & 0xFF

    @property
    def initial_attenuation(self) -> float:
        return 0.1 * self._gs[_GeneratorType.INITIAL_ATTENUATION]

    @property
    def coarse_tune(self) -> int:
        return self._gs[_GeneratorType.COARSE_TUNE]

    @property
    def fine_tune(self) -> int:
        return self._gs[_GeneratorType.FINE_TUNE]

    @property
    def scale_tuning(self) -> int:
        return self._gs[_GeneratorType.SCALE_TUNING]



class _SoundFontParameters:

    _sample_headers: Sequence[SampleHeader]
    _presets: Sequence[Preset]
    _instruments: Sequence[Instrument]

    def __init__(self, reader: BufferedReader) -> None:
        
        chunk_id = _BinaryReaderEx.read_four_cc(reader)
        if chunk_id != "LIST":
            raise Exception("The LIST chunk was not found.")
        
        end = reader.tell() + _BinaryReaderEx.read_int32(reader)

        list_type = _BinaryReaderEx.read_four_cc(reader)
        if list_type != "pdta":
            raise Exception("The type of the LIST chunk must be 'pdta', but was '" + list_type + "'.")

        preset_infos: Optional[Sequence[_PresetInfo]] = None
        preset_bag: Optional[Sequence[_ZoneInfo]] = None
        preset_generators: Optional[Sequence[_Generator]] = None
        instrument_infos: Optional[Sequence[_InstrumentInfo]] = None
        instrument_bag: Optional[Sequence[_ZoneInfo]] = None
        instrument_generators: Optional[Sequence[_Generator]] = None
        sample_headers: Optional[Sequence[SampleHeader]] = None

        while reader.tell() < end:

            id = _BinaryReaderEx.read_four_cc(reader)
            size = _BinaryReaderEx.read_uint32(reader)

            match id:

                case "phdr":
                    preset_infos = _PresetInfo.read_from_chunk(reader, size)

                case "pbag":
                    preset_bag = _ZoneInfo.read_from_chunk(reader, size)

                case "pmod":
                    _Modulator.discard_data(reader, size)

                case "pgen":
                    preset_generators = _Generator.read_from_chunk(reader, size)

                case "inst":
                    instrument_infos = _InstrumentInfo.read_from_chunk(reader, size)

                case "ibag":
                    instrument_bag = _ZoneInfo.read_from_chunk(reader, size)

                case "imod":
                    _Modulator.discard_data(reader, size)

                case "igen":
                    instrument_generators = _Generator.read_from_chunk(reader, size)

                case "shdr":
                    sample_headers = SampleHeader._read_from_chunk(reader, size)

                case _:
                    raise Exception("The INFO list contains an unknown ID '" + id + "'.")

        if preset_infos is None:
            raise Exception("The PHDR sub-chunk was not found.")
        
        if preset_bag is None:
            raise Exception("The PBAG sub-chunk was not found.")
        
        if preset_generators is None:
            raise Exception("The PGEN sub-chunk was not found.")
        
        if instrument_infos is None:
            raise Exception("The INST sub-chunk was not found.")
        
        if instrument_bag is None:
            raise Exception("The IBAG sub-chunk was not found.")
        
        if instrument_generators is None:
            raise Exception("The IGEN sub-chunk was not found.")
        
        if sample_headers is None:
            raise Exception("The SHDR sub-chunk was not found.")

        self._sample_headers = sample_headers
        
        instrument_zones = _Zone.create(instrument_bag, instrument_generators)
        self._instruments = Instrument._create(instrument_infos, instrument_zones, sample_headers)

        preset_zones = _Zone.create(preset_bag, preset_generators)
        self._presets = Preset._create(preset_infos, preset_zones, self._instruments)

    @property
    def sample_headers(self) -> Sequence[SampleHeader]:
        return self._sample_headers
    
    @property
    def presets(self) -> Sequence[Preset]:
        return self._presets
    
    @property
    def instruments(self) -> Sequence[Instrument]:
        return self._instruments



class SoundFont:

    _info: SoundFontInfo
    _bits_per_sample: int
    _wave_data: Sequence[int]
    _sample_headers: Sequence[SampleHeader]
    _presets: Sequence[Preset]
    _instruments: Sequence[Instrument]

    def __init__(self, reader: BufferedReader) -> None:

        chunk_id = _BinaryReaderEx.read_four_cc(reader)
        if chunk_id != "RIFF":
            raise Exception("The RIFF chunk was not found.")

        _BinaryReaderEx.read_uint32(reader)

        form_type = _BinaryReaderEx.read_four_cc(reader)
        if form_type != "sfbk":
            raise Exception("The type of the RIFF chunk must be 'sfbk', but was '" + form_type + "'.")
        
        self._info = SoundFontInfo(reader)

        sample_data = _SoundFontSampleData(reader)
        self._bits_per_sample = sample_data.bits_per_sample
        self._wave_data = sample_data.samples

        parameters = _SoundFontParameters(reader)
        self._sample_headers = parameters.sample_headers
        self._presets = parameters.presets
        self._instruments = parameters.instruments

    @property
    def info(self) -> SoundFontInfo:
        return self._info
    
    @property
    def wave_data(self) -> Sequence[int]:
        return self._wave_data
    
    @property
    def sample_headers(self) -> Sequence[SampleHeader]:
        return self._sample_headers
    
    @property
    def presets(self) -> Sequence[Preset]:
        return self._presets
    
    @property
    def instruments(self) -> Sequence[Instrument]:
        return self._instruments



class _RegionPair:

    _preset: PresetRegion
    _instrument: InstrumentRegion

    def __init__(self, preset: PresetRegion, instrument: InstrumentRegion) -> None:

        self._preset = preset
        self._instrument = instrument
    
    def get_value(self, generator_type: _GeneratorType) -> int:
        return self._preset._gs[generator_type] + self._instrument._gs[generator_type]
    
    @property
    def preset(self) -> PresetRegion:
        return self._preset
    
    @property
    def instrument(self) -> InstrumentRegion:
        return self._instrument
    
    @property
    def sample_start(self) -> int:
        return self._instrument.sample_start

    @property
    def sample_end(self) -> int:
        return self._instrument.sample_end

    @property
    def sample_start_loop(self) -> int:
        return self._instrument.sample_start_loop

    @property
    def sample_end_loop(self) -> int:
        return self._instrument.sample_end_loop

    @property
    def start_address_offset(self) -> int:
        return self._instrument.start_address_offset

    @property
    def end_address_offset(self) -> int:
        return self._instrument.end_address_offset

    @property
    def start_loop_address_offset(self) -> int:
        return self._instrument.start_loop_address_offset

    @property
    def end_loop_address_offset(self) -> int:
        return self._instrument.end_loop_address_offset

    @property
    def modulation_lfo_to_pitch(self) -> int:
        return self.get_value(_GeneratorType.MODULATION_LFO_TO_PITCH)

    @property
    def vibrato_lfo_to_pitch(self) -> int:
        return self.get_value(_GeneratorType.VIBRATO_LFO_TO_PITCH)

    @property
    def modulation_envelope_to_pitch(self) -> int:
        return self.get_value(_GeneratorType.MODULATION_ENVELOPE_TO_PITCH)

    @property
    def initial_filter_cutoff_frequency(self) -> float:
        return _SoundFontMath.cents_to_hertz(self.get_value(_GeneratorType.INITIAL_FILTER_CUTOFF_FREQUENCY))

    @property
    def initial_filter_q(self) -> float:
        return 0.1 * self.get_value(_GeneratorType.INITIAL_FILTER_Q)

    @property
    def modulation_lfo_to_filter_cutoff_frequency(self) -> int:
        return self.get_value(_GeneratorType.MODULATION_LFO_TO_FILTER_CUTOFF_FREQUENCY)

    @property
    def modulation_envelope_to_filter_cutoff_frequency(self) -> int:
        return self.get_value(_GeneratorType.MODULATION_ENVELOPE_TO_FILTER_CUTOFF_FREQUENCY)

    @property
    def modulation_lfo_to_volume(self) -> float:
        return 0.1 * self.get_value(_GeneratorType.MODULATION_LFO_TO_VOLUME)

    @property
    def chorus_effects_send(self) -> float:
        return 0.1 * self.get_value(_GeneratorType.CHORUS_EFFECTS_SEND)

    @property
    def reverb_effects_send(self) -> float:
        return 0.1 * self.get_value(_GeneratorType.REVERB_EFFECTS_SEND)

    @property
    def pan(self) -> float:
        return 0.1 * self.get_value(_GeneratorType.PAN)

    @property
    def delay_modulation_lfo(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self.get_value(_GeneratorType.DELAY_MODULATION_LFO))

    @property
    def frequency_modulation_lfo(self) -> float:
        return _SoundFontMath.cents_to_hertz(self.get_value(_GeneratorType.FREQUENCY_MODULATION_LFO))

    @property
    def delay_vibrato_lfo(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self.get_value(_GeneratorType.DELAY_VIBRATO_LFO))

    @property
    def frequency_vibrato_lfo(self) -> float:
        return _SoundFontMath.cents_to_hertz(self.get_value(_GeneratorType.FREQUENCY_VIBRATO_LFO))

    @property
    def delay_modulation_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self.get_value(_GeneratorType.DELAY_MODULATION_ENVELOPE))

    @property
    def attack_modulation_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self.get_value(_GeneratorType.ATTACK_MODULATION_ENVELOPE))

    @property
    def hold_modulation_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self.get_value(_GeneratorType.HOLD_MODULATION_ENVELOPE))

    @property
    def decay_modulation_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self.get_value(_GeneratorType.DECAY_MODULATION_ENVELOPE))

    @property
    def sustain_modulation_envelope(self) -> float:
        return 0.1 * self.get_value(_GeneratorType.SUSTAIN_MODULATION_ENVELOPE)

    @property
    def release_modulation_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self.get_value(_GeneratorType.RELEASE_MODULATION_ENVELOPE))

    @property
    def key_number_to_modulation_envelope_hold(self) -> int:
        return self.get_value(_GeneratorType.KEY_NUMBER_TO_MODULATION_ENVELOPE_HOLD)

    @property
    def key_number_to_modulation_envelope_decay(self) -> int:
        return self.get_value(_GeneratorType.KEY_NUMBER_TO_MODULATION_ENVELOPE_DECAY)

    @property
    def delay_volume_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self.get_value(_GeneratorType.DELAY_VOLUME_ENVELOPE))

    @property
    def attack_volume_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self.get_value(_GeneratorType.ATTACK_VOLUME_ENVELOPE))

    @property
    def hold_volume_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self.get_value(_GeneratorType.HOLD_VOLUME_ENVELOPE))

    @property
    def decay_volume_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self.get_value(_GeneratorType.DECAY_VOLUME_ENVELOPE))

    @property
    def sustain_volume_envelope(self) -> float:
        return 0.1 * self.get_value(_GeneratorType.SUSTAIN_VOLUME_ENVELOPE)

    @property
    def release_volume_envelope(self) -> float:
        return _SoundFontMath.timecents_to_seconds(self.get_value(_GeneratorType.RELEASE_VOLUME_ENVELOPE))

    @property
    def key_number_to_volume_envelope_hold(self) -> int:
        return self.get_value(_GeneratorType.KEY_NUMBER_TO_VOLUME_ENVELOPE_HOLD)

    @property
    def key_number_to_volume_envelope_decay(self) -> int:
        return self.get_value(_GeneratorType.KEY_NUMBER_TO_VOLUME_ENVELOPE_DECAY)

    @property
    def initial_attenuation(self) -> float:
        return 0.1 * self.get_value(_GeneratorType.INITIAL_ATTENUATION)

    @property
    def coarse_tune(self) -> int:
        return self.get_value(_GeneratorType.COARSE_TUNE)

    @property
    def fine_tune(self) -> int:
        return self.get_value(_GeneratorType.FINE_TUNE) + self._instrument.sample.pitch_correction

    @property
    def sample_modes(self) -> LoopMode:
        return self._instrument.sample_modes

    @property
    def scale_tuning(self) -> int:
        return self.get_value(_GeneratorType.SCALE_TUNING)

    @property
    def exclusive_class(self) -> int:
        return self._instrument.exclusive_class

    @property
    def root_key(self) -> int:
        return self._instrument.root_key



class Synthesizer:
    sample_rate: int
    block_size: int



class _Oscillator:

    _synthesizer: Synthesizer

    _data: Sequence[int]
    _loop_mode: LoopMode
    _sample_rate: int
    _start: int
    _end: int
    _start_loop: int
    _end_loop: int
    _root_key: int

    _tune: float
    _pitch_change_scale: float
    _sample_rate_ratio: float

    _looping: bool

    _position: float

    def __init__(self, synthesizer: Synthesizer) -> None:
        self._synthesizer = synthesizer

    def start(self, data: Sequence[int], loop_mode: LoopMode, sample_rate: int, start: int, end: int, start_loop: int, end_loop: int, root_key: int, coarse_tune: int, fine_tune: int, scale_tuning: int) -> None:

        self._data = data
        self._loop_mode = loop_mode
        self._sample_rate = sample_rate
        self._start = start
        self._end = end
        self._start_loop = start_loop
        self._end_loop = end_loop
        self._root_key = root_key

        self._tune = coarse_tune + 0.01 * fine_tune
        self._pitch_change_scale = 0.01 * scale_tuning
        self._sample_rate_ratio = sample_rate / self._synthesizer.sample_rate

        if loop_mode == LoopMode.NO_LOOP:
            self._looping = False
        else:
            self._looping = True
        
        self._position = start
    
    def release(self) -> None:

        if self._loop_mode == LoopMode.LOOP_UNTIL_NOTE_OFF:
            self._looping = False
    
    def process(self, block: MutableSequence[float], pitch: float) -> bool:

        pitch_change = self._pitch_change_scale * (pitch - self._root_key) + self._tune
        pitch_ratio = self._sample_rate_ratio * math.pow(2.0, pitch_change / 12.0)
        return self.fill_block(block, pitch_ratio)
    
    def fill_block(self, block: MutableSequence[float], pitch_ratio: float) -> bool:

        if self._looping:
            return self.fill_block_continuous(block, pitch_ratio)
        else:
            return self.fill_block_no_loop(block, pitch_ratio)
    
    def fill_block_no_loop(self, block: MutableSequence[float], pitch_ratio: float) -> bool:

        for t in range(len(block)):

            index = int(self._position)

            if index >= self._end:
                if t > 0:
                    for u in range(t, len(block)):
                        block[u] = 0
                    return True
                else:
                    return False

            x1: int = self._data[index]
            x2: int = self._data[index + 1]
            a = self._position - index
            block[t] = (x1 + a * (x2 - x1)) / 32768

            self._position += pitch_ratio

        return True
    
    def fill_block_continuous(self, block: MutableSequence[float], pitch_ratio: float) -> bool:

        end_loop_position = float(self._end_loop)

        loop_length = self._end_loop - self._start_loop

        for t in range(len(block)):

            if self._position >= end_loop_position:
                self._position -= loop_length

            index1 = int(self._position)
            index2 = index1 + 1

            if index2 >= self._end_loop:
                index2 -= loop_length

            x1 = self._data[index1]
            x2 = self._data[index2]
            a = self._position - index1
            block[t] = ((x1 + a * (x2 - x1)) / 32768)

            self._position += pitch_ratio

        return True



class _EnvelopeStage(IntEnum):

    DELAY = 0
    ATTACK = 1
    HOLD = 2
    DECAY = 3
    RELEASE = 4



class _VolumeEnvelope:

    _synthesizer: Synthesizer

    _attack_slope: float
    _decay_slope: float
    _release_slope: float

    _attack_start_time: float
    _hold_start_time: float
    _decay_start_time: float
    _release_start_time: float

    _sustain_level: float
    _release_level: float

    _processed_sample_count: int
    _stage: _EnvelopeStage
    _value: float

    _priority: float

    def __init__(self, synthesizer: Synthesizer) -> None:
        self._synthesizer = synthesizer
    
    def start(self, delay: float, attack: float, hold: float, decay: float, sustain: float, release: float) -> None:

        self._attack_slope = 1 / attack
        self._decay_slope = -9.226 / decay
        self._release_slope = -9.226 / release

        self._attack_start_time = delay
        self._hold_start_time = self._attack_start_time + attack
        self._decay_start_time = self._hold_start_time + hold
        self._release_start_time = 0

        self._sustain_level = _SoundFontMath.clamp(sustain, 0, 1)
        self._release_level = 0

        self._processed_sample_count = 0
        self._stage = _EnvelopeStage.DELAY
        self._value = 0

        self.process(0)

    def release(self) -> None:

        self._stage = _EnvelopeStage.RELEASE
        self._release_start_time = float(self._processed_sample_count) / self._synthesizer.sample_rate
        self._release_level = self._value
    
    def process(self, sample_count: int) -> bool:

        self._processed_sample_count += sample_count

        current_time = float(self._processed_sample_count) / self._synthesizer.sample_rate

        while self._stage <= _EnvelopeStage.HOLD:

            end_time: float

            match self._stage:

                case _EnvelopeStage.DELAY:
                    end_time = self._attack_start_time

                case _EnvelopeStage.ATTACK:
                    end_time = self._hold_start_time

                case _EnvelopeStage.HOLD:
                    end_time = self._decay_start_time

                case _:
                    raise Exception("Invalid envelope stage.")

            if current_time < end_time:
                break
            else:
                self._stage = _EnvelopeStage(self._stage.value + 1)

        match self._stage:

            case _EnvelopeStage.DELAY:
                self._value = 0
                self._priority = 4 + self._value
                return True

            case _EnvelopeStage.ATTACK:
                self._value = self._attack_slope * (current_time - self._attack_start_time)
                self._priority = 3 + self._value
                return True

            case _EnvelopeStage.HOLD:
                self._value = 1
                self._priority = 2 + self._value
                return True

            case _EnvelopeStage.DECAY:
                self._value = max(_SoundFontMath.exp_cutoff(self._decay_slope * (current_time - self._decay_start_time)), self._sustain_level)
                self._priority = 1 + self._value
                return self._value > _SoundFontMath.non_audible()

            case _EnvelopeStage.RELEASE:
                self._value = self._release_level * _SoundFontMath.exp_cutoff(self._release_slope * (current_time - self._release_start_time))
                self._priority = self._value
                return self._value > _SoundFontMath.non_audible()

            case _:
                raise Exception("Invalid envelope stage.")

    @property
    def value(self) -> float:
        return self._value
    
    @property
    def priority(self) -> float:
        return self._priority



class _ModulationEnvelope:

    _synthesizer: Synthesizer

    _attack_slope: float
    _decay_slope: float
    _release_slope: float

    _attack_start_time: float
    _hold_start_time: float
    _decay_start_time: float

    _decay_end_time: float
    _release_end_time: float

    _sustain_level: float
    _release_level: float

    _processed_sample_count: int
    _stage: _EnvelopeStage
    _value: float

    def __init__(self, synthesizer: Synthesizer) -> None:
        self._synthesizer = synthesizer
    
    def start(self, delay: float, attack: float, hold: float, decay: float, sustain: float, release: float) -> None:

        self._attack_slope = 1 / attack
        self._decay_slope = 1 / decay
        self._release_slope = 1 / release

        self._attack_start_time = delay
        self._hold_start_time = self._attack_start_time + attack
        self._decay_start_time = self._hold_start_time + hold

        self._decay_end_time = self._decay_start_time + decay
        self._release_end_time = release

        self._sustain_level = _SoundFontMath.clamp(sustain, 0, 1)
        self._release_level = 0

        self._processed_sample_count = 0
        self._stage = _EnvelopeStage.DELAY
        self._value = 0

        self.process(0)

    def release(self) -> None:

        self._stage = _EnvelopeStage.RELEASE
        self._release_end_time += float(self._processed_sample_count) / self._synthesizer.sample_rate
        self._release_level = self._value
    
    def process(self, sample_count: int) -> bool:

        self._processed_sample_count += sample_count

        current_time = float(self._processed_sample_count) / self._synthesizer.sample_rate

        while self._stage <= _EnvelopeStage.HOLD:

            end_time: float

            match self._stage:

                case _EnvelopeStage.DELAY:
                    end_time = self._attack_start_time

                case _EnvelopeStage.ATTACK:
                    end_time = self._hold_start_time

                case _EnvelopeStage.HOLD:
                    end_time = self._decay_start_time

                case _:
                    raise Exception("Invalid envelope stage.")

            if current_time < end_time:
                break
            else:
                self._stage = _EnvelopeStage(self._stage.value + 1)

        match self._stage:

            case _EnvelopeStage.DELAY:
                self._value = 0
                return True

            case _EnvelopeStage.ATTACK:
                self._value = self._attack_slope * (current_time - self._attack_start_time)
                return True

            case _EnvelopeStage.HOLD:
                self._value = 1
                return True

            case _EnvelopeStage.DECAY:
                self._value = max(self._decay_slope * (self._decay_end_time - current_time), self._sustain_level)
                return self._value > _SoundFontMath.non_audible()

            case _EnvelopeStage.RELEASE:
                self._value = max(self._release_level * self._release_slope * (self._release_end_time - current_time), 0)
                return self._value > _SoundFontMath.non_audible()

            case _:
                raise Exception("Invalid envelope stage.")
    
    @property
    def value(self) -> float:
        return self._value



class _Lfo:

    _synthesizer: Synthesizer

    _active: bool

    _delay: float
    _period: float

    _processed_sample_count: int
    _value: float

    def __init__(self, synthesizer: Synthesizer) -> None:
        self._synthesizer = synthesizer
    
    def start(self, delay: float, frequency: float) -> None:

        if frequency > 1.0E-3:

            self._active = True

            self._delay = delay
            self._period = 1.0 / frequency

            self._processed_sample_count = 0
            self._value = 0

        else:

            self._active = False
            self._value = 0
    
    def process(self) -> None:

        if not self._active:
            return

        self._processed_sample_count += self._synthesizer.block_size

        current_time = float(self._processed_sample_count) / self._synthesizer.sample_rate

        if current_time < self._delay:

            self._value = 0

        else:

            phase = ((current_time - self._delay) % self._period) / self._period
            if phase < 0.25:
                self._value = 4 * phase
            elif phase < 0.75:
                self._value = 4 * (0.5 - phase)
            else:
                self._value = 4 * (phase - 1.0)

    @property
    def value(self) -> float:
        return self._value



class _RegionEx:

    @staticmethod
    def start_oscillator(oscillator: _Oscillator, data: Sequence[int], region: _RegionPair) -> None:
        
        sample_rate = region.instrument.sample.sample_rate
        loop_mode = region.sample_modes
        start = region.sample_start
        end = region.sample_end
        start_loop = region.sample_start_loop
        end_Loop = region.sample_end_loop
        root_key = region.root_key
        coarse_tune = region.coarse_tune
        fine_tune = region.fine_tune
        scale_tuning = region.scale_tuning

        oscillator.start(data, loop_mode, sample_rate, start, end, start_loop, end_Loop, root_key, coarse_tune, fine_tune, scale_tuning)
    
    @staticmethod
    def start_volume_envelope(envelope: _VolumeEnvelope, region: _RegionPair, key: int, velocity: int) -> None:

        # If the release time is shorter than 10 ms, it will be clamped to 10 ms to avoid pop noise.

        delay = region.delay_volume_envelope
        attack = region.attack_volume_envelope
        hold = region.hold_volume_envelope * _SoundFontMath.key_number_to_multiplying_factor(region.key_number_to_volume_envelope_hold, key)
        decay = region.decay_volume_envelope * _SoundFontMath.key_number_to_multiplying_factor(region.key_number_to_volume_envelope_decay, key)
        sustain = _SoundFontMath.decibels_to_linear(-region.sustain_volume_envelope)
        release = max(region.release_volume_envelope, 0.01)

        envelope.start(delay, attack, hold, decay, sustain, release)
    
    @staticmethod
    def start_modulation_envelope(envelope: _ModulationEnvelope, region: _RegionPair, key: int, velocity: int) -> None:

        # According to the implementation of TinySoundFont, the attack time should be adjusted by the velocity.

        delay = region.delay_modulation_envelope
        attack = region.attack_modulation_envelope * ((145 - velocity) / 144.0)
        hold = region.hold_modulation_envelope * _SoundFontMath.key_number_to_multiplying_factor(region.key_number_to_modulation_envelope_hold, key)
        decay = region.decay_modulation_envelope * _SoundFontMath.key_number_to_multiplying_factor(region.key_number_to_modulation_envelope_decay, key)
        sustain = 1.0 - region.sustain_modulation_envelope / 100.0
        release = region.release_modulation_envelope

        envelope.start(delay, attack, hold, decay, sustain, release)
    
    @staticmethod
    def start_vibrato(lfo: _Lfo, region: _RegionPair, key: int, velocity: int) -> None:
        lfo.start(region.delay_vibrato_lfo, region.frequency_vibrato_lfo)
    
    @staticmethod
    def start_modulation(lfo: _Lfo, region: _RegionPair, key: int, velocity: int) -> None:
        lfo.start(region.delay_modulation_lfo, region.frequency_modulation_lfo)



class _BiQuadFilter:

    _synthesizer: Synthesizer

    _resonance_peak_offset: float

    _active: bool

    _a0: float
    _a1: float
    _a2: float
    _a3: float
    _a4: float

    _x1: float
    _x2: float
    _y1: float
    _y2: float

    def __init__(self, synthesizer: Synthesizer) -> None:
        self._synthesizer = synthesizer
        self._resonance_peak_offset = 1.0 - 1.0 / math.sqrt(2.0)

    def clear_buffer(self) -> None:

        self._x1 = 0
        self._x2 = 0
        self._y1 = 0
        self._y2 = 0
    
    def set_low_pass_filter(self, cutoff_frequency: float, resonance: float) -> None:

        if cutoff_frequency < 0.499 * self._synthesizer.sample_rate:

            self._active = True

            # This equation gives the Q value which makes the desired resonance peak.
            # The error of the resultant peak height is less than 3%.
            q = resonance - self._resonance_peak_offset / (1 + 6 * (resonance - 1))

            w = 2 * math.pi * cutoff_frequency / self._synthesizer.sample_rate
            cosw = math.cos(w)
            alpha = math.sin(w) / (2 * q)

            b0 = (1 - cosw) / 2
            b1 = 1 - cosw
            b2 = (1 - cosw) / 2
            a0 = 1 + alpha
            a1 = -2 * cosw
            a2 = 1 - alpha

            self.set_coefficients(a0, a1, a2, b0, b1, b2)

        else:
            self._active = False

    def process(self, block: MutableSequence[float]) -> None:

        if self._active:

            for t in range(len(block)):

                input = block[t]
                output = self._a0 * input + self._a1 * self._x1 + self._a2 * self._x2 - self._a3 * self._y1 - self._a4 * self._y2

                self._x2 = self._x1
                self._x1 = input
                self._y2 = self._y1
                self._y1 = output

                block[t] = output

        else:

            self._x2 = block[len(block) - 2]
            self._x1 = block[len(block) - 1]
            self._y2 = self._x2
            self._y1 = self._x1

    def set_coefficients(self, a0: float, a1: float, a2: float, b0: float, b1: float, b2: float) -> None:

        self._a0 = b0 / a0
        self._a1 = b1 / a0
        self._a2 = b2 / a0
        self._a3 = a1 / a0
        self._a4 = a2 / a0
