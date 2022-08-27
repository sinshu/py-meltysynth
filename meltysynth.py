import array
import io
import itertools
import math
from enum import IntEnum



class BinaryReaderEx:

    @staticmethod
    def read_int32(reader: io.BytesIO) -> int:
        return int.from_bytes(reader.read(4), byteorder="little", signed=True)

    @staticmethod
    def read_uint32(reader: io.BytesIO) -> int:
        return int.from_bytes(reader.read(4), byteorder="little", signed=False)

    @staticmethod
    def read_int16(reader: io.BytesIO) -> int:
        return int.from_bytes(reader.read(2), byteorder="little", signed=True)

    @staticmethod
    def read_uint16(reader: io.BytesIO) -> int:
        return int.from_bytes(reader.read(2), byteorder="little", signed=False)

    @staticmethod
    def read_int8(reader: io.BytesIO) -> int:
        return int.from_bytes(reader.read(1), byteorder="little", signed=True)

    @staticmethod
    def read_uint8(reader: io.BytesIO) -> int:
        return int.from_bytes(reader.read(1), byteorder="little", signed=False)

    @staticmethod
    def read_four_cc(reader: io.BytesIO) -> str:

        data = reader.read(4)

        for i, value in enumerate(data):
            if not (32 <= value and value <= 126):
                data[i] = 63 # '?'

        return data.decode("ascii")

    @staticmethod
    def read_fixed_length_string(reader: io.BytesIO, length: int) -> str:

        data = reader.read(length)

        actualLength = 0
        for value in data:
            if value == 0:
                break
            actualLength += 1
        
        return data[0:actualLength].decode("ascii")
    
    @staticmethod
    def read_int16_array(reader: io.BytesIO, size: int) -> array.array:

        count = int(size / 2)
        result = array.array("h", itertools.repeat(0, count))

        for i in range(count):
            result[i] = BinaryReaderEx.read_int16(reader)
        
        return result



class SoundFontMath:

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
        return SoundFontMath.timecents_to_seconds(cents * (60 - key))
    
    @staticmethod
    def exp_cutoff(x: float) -> float:
        if x < SoundFontMath.log_non_audible():
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
    def Major(self) -> int:
        return self._major

    @property
    def Minor(self) -> int:
        return self._minor



class SoundFontInfo:
    
    _version: SoundFontVersion = SoundFontVersion(0, 0)
    _target_sound_engine: str = ""
    _bank_name: str = ""
    _rom_name: str = ""
    _rom_version: SoundFontVersion = SoundFontVersion(0, 0)
    _creation_date: str = ""
    _auther: str = ""
    _target_product: str = ""
    _copyright: str = ""
    _comments: str = ""
    _tools: str = ""

    def __init__(self, reader: io.BytesIO) -> None:

        chunk_id = BinaryReaderEx.read_four_cc(reader)
        if chunk_id != "LIST":
            raise Exception("The LIST chunk was not found.")

        end = reader.tell() + BinaryReaderEx.read_uint32(reader)

        list_type = BinaryReaderEx.read_four_cc(reader)
        if list_type != "INFO":
            raise Exception("The type of the LIST chunk must be 'INFO', but was '" + list_type + "'.")
        
        while reader.tell() < end:

            id = BinaryReaderEx.read_four_cc(reader)
            size = BinaryReaderEx.read_uint32(reader)

            match id:

                case "ifil":
                    self._version = SoundFontVersion(BinaryReaderEx.read_uint16(reader), BinaryReaderEx.read_uint16(reader))

                case "isng":
                    self._target_sound_engine = BinaryReaderEx.read_fixed_length_string(reader, size)

                case "INAM":
                    self._bank_name = BinaryReaderEx.read_fixed_length_string(reader, size)

                case "irom":
                    self._rom_name = BinaryReaderEx.read_fixed_length_string(reader, size)

                case "iver":
                    self._rom_version = SoundFontVersion(BinaryReaderEx.read_uint16(reader), BinaryReaderEx.read_uint16(reader))

                case "ICRD":
                    self._creation_date = BinaryReaderEx.read_fixed_length_string(reader, size)

                case "IENG":
                    self._author = BinaryReaderEx.read_fixed_length_string(reader, size)

                case "IPRD":
                    self._target_product = BinaryReaderEx.read_fixed_length_string(reader, size)

                case "ICOP":
                    self._copyright = BinaryReaderEx.read_fixed_length_string(reader, size)

                case "ICMT":
                    self._comments = BinaryReaderEx.read_fixed_length_string(reader, size)

                case "ISFT":
                    self._tools = BinaryReaderEx.read_fixed_length_string(reader, size)

                case _:
                    raise Exception("The INFO list contains an unknown ID '" + id + "'.")

    @property
    def sound_font_version(self) -> SoundFontVersion:
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
    def auther(self) -> str:
        return self._auther
    
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



class SoundFontSampleData:

    _bits_per_sample: int
    _samples: array.array

    def __init__(self, reader: io.BytesIO) -> None:
        
        chunk_id = BinaryReaderEx.read_four_cc(reader)
        if chunk_id != "LIST":
            raise Exception("The LIST chunk was not found.")
        
        end = reader.tell() + BinaryReaderEx.read_uint32(reader)

        list_type = BinaryReaderEx.read_four_cc(reader)
        if list_type != "sdta":
            raise Exception("The type of the LIST chunk must be 'sdta', but was '" + list_type + "'.")
        
        while reader.tell() < end:

            id = BinaryReaderEx.read_four_cc(reader)
            size = BinaryReaderEx.read_uint32(reader)

            match id:

                case "smpl":
                    self._bits_per_sample = 16
                    self._samples = BinaryReaderEx.read_int16_array(reader, size)

                case "sm24":
                    reader.seek(size, io.SEEK_CUR)

                case _:
                    raise Exception("The INFO list contains an unknown ID '" + id + "'.")
        
        if self._samples == None:
            raise Exception("No valid sample data was found.")
        
    @property
    def bits_per_sample(self) -> int:
        return self._bits_per_sample

    @property
    def samples(self) -> array.array:
        return self._samples



class GeneratorType(IntEnum):

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



class Generator:

    _generator_type: GeneratorType
    _value: int

    def __init__(self, reader: io.BytesIO) -> None:
        
        self._generator_type = GeneratorType(BinaryReaderEx.read_uint16(reader))
        self._value = BinaryReaderEx.read_int16(reader)

    @staticmethod
    def read_from_chunk(reader: io.BytesIO, size: int) -> list:

        if int(size % 4) != 0:
            raise Exception("The generator list is invalid.")

        count = int(size / 4) - 1
        generators = list()

        for i in range(count):
            generators.append(Generator(reader))

        # The last one is the terminator.
        Generator(reader)

        return generators
    
    @property
    def generator_type(self) -> list:
        return self._generator_type
    
    @property
    def value(self) -> int:
        return self._value



class Modulator:

    @staticmethod
    def discard_data(reader: io.BytesIO, size: int) -> None:

        if int(size % 10) != 0:
            raise Exception("The modulator list is invalid.")
        
        reader.seek(size, io.SEEK_CUR)



class SampleType(IntEnum):

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
    _sample_type: SampleType

    def __init__(self, reader: io.BytesIO) -> None:
        
        self._name = BinaryReaderEx.read_fixed_length_string(reader, 20)
        self._start = BinaryReaderEx.read_int32(reader)
        self._end = BinaryReaderEx.read_int32(reader)
        self._start_loop = BinaryReaderEx.read_int32(reader)
        self._end_loop = BinaryReaderEx.read_int32(reader)
        self._sample_rate = BinaryReaderEx.read_int32(reader)
        self._original_pitch = BinaryReaderEx.read_uint8(reader)
        self._pitch_correction = BinaryReaderEx.read_int8(reader)
        self._link = BinaryReaderEx.read_uint16(reader)
        self._sample_type = BinaryReaderEx.read_uint16(reader)
    
    @staticmethod
    def read_from_chunk(reader: io.BytesIO, size: int) -> list:

        if int(size % 46) != 0:
            raise Exception("The sample header list is invalid.")
        
        count = int(size / 46) - 1
        headers = list()

        for i in range(count):
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
    
    @property
    def link(self) -> int:
        return self._link
    
    @property
    def sample_type(self) -> SampleType:
        return self._sample_type



class ZoneInfo:

    _generator_index: int
    _modulator_index: int
    _generator_count: int
    _modulator_count: int

    def __init__(self) -> None:
        pass

    @staticmethod
    def read_from_chunk(reader: io.BytesIO, size: int) -> list:

        if int(size % 4) != 0:
            raise Exception("The zone list is invalid.")
        
        count = int(size / 4)
        zones = list()

        for i in range(count):

            zone = ZoneInfo()
            zone._generator_index = BinaryReaderEx.read_uint16(reader)
            zone._modulator_index = BinaryReaderEx.read_uint16(reader)
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



class Zone:

    _generators: list

    def __init__(self) -> None:
        pass

    @staticmethod
    def create(infos: list, generators: list) -> list:

        if len(infos) <= 1:
            raise Exception("No valid zone was found.")
        
        # The last one is the terminator.
        count = len(infos) - 1
        zones = list()

        for i in range(count):

            info: ZoneInfo = infos[i]

            zone = Zone()
            zone._generators = list()
            for j in range(info.generator_count):
                zone._generators.append(generators[info.generator_index + j])
            
            zones.append(zone)
        
        return zones
    
    @property
    def generators(self) -> list:
        return self._generators



class PresetInfo:

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
    def read_from_chunk(reader: io.BytesIO, size: int) -> list:

        if int(size % 38) != 0:
            raise Exception("The preset list is invalid.")
    
        count = int(size / 38)
        presets = list()

        for i in range(count):

            preset = PresetInfo()
            preset._name = BinaryReaderEx.read_fixed_length_string(reader, 20)
            preset._patch_number = BinaryReaderEx.read_uint16(reader)
            preset._bank_number = BinaryReaderEx.read_uint16(reader)
            preset._zone_start_index = BinaryReaderEx.read_uint16(reader)
            preset._library = BinaryReaderEx.read_int32(reader)
            preset._genre = BinaryReaderEx.read_int32(reader)
            preset._morphology = BinaryReaderEx.read_int32(reader)
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



class InstrumentInfo:

    _name: str
    _zone_start_index: int
    _zone_end_index: int

    def __init__(self) -> None:
        pass

    @staticmethod
    def read_from_chunk(reader: io.BytesIO, size: int) -> list:

        if int(size % 22) != 0:
            raise Exception("The instrument list is invalid.")
    
        count = int(size / 22)
        instruments = list()

        for i in range(count):

            instrument = InstrumentInfo()
            instrument._name = BinaryReaderEx.read_fixed_length_string(reader, 20)
            instrument._zone_start_index = BinaryReaderEx.read_uint16(reader)
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
    _regions: list

    def __init__(self, info: InstrumentInfo, zones: list, samples: list) -> None:
        
        self._name = info.name

        zone_count = info.zone_end_index - info.zone_start_index + 1
        if zone_count <= 0:
            raise Exception("The instrument '" + info.name + "' has no zone.")
        
        zone_span = zones[info.zone_start_index:info.zone_start_index + zone_count]

        self._regions = InstrumentRegion.create(self, zone_span, samples)

    @staticmethod
    def create(infos: list, zones: list, samples: list):

        if len(infos) <= 1:
            raise Exception("No valid instrument was found.")
        
        # The last one is the terminator.
        count = len(infos) - 1
        instruments = list()

        for i in range(count):
            instruments.append(Instrument(infos[i], zones, samples))
        
        return instruments

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def regions(self) -> list:
        return self._regions



class LoopMode(IntEnum):

    NO_LOOP = 0
    CONTINUOUS = 1
    LOOP_UNTIL_NOTE_OFF = 3



class InstrumentRegion:

    _sample: SampleHeader
    _gs: array.array

    def __init__(self, instrument: Instrument, global_generators: list, local_generators: list, samples: list) -> None:
        
        self._gs = array.array("h", itertools.repeat(0, 64))
        self._gs[GeneratorType.INITIAL_FILTER_CUTOFF_FREQUENCY] = 13500
        self._gs[GeneratorType.DELAY_MODULATION_LFO] = -12000
        self._gs[GeneratorType.DELAY_VIBRATO_LFO] = -12000
        self._gs[GeneratorType.DELAY_MODULATION_ENVELOPE] = -12000
        self._gs[GeneratorType.ATTACK_MODULATION_ENVELOPE] = -12000
        self._gs[GeneratorType.HOLD_MODULATION_ENVELOPE] = -12000
        self._gs[GeneratorType.DECAY_MODULATION_ENVELOPE] = -12000
        self._gs[GeneratorType.RELEASE_MODULATION_ENVELOPE] = -12000
        self._gs[GeneratorType.DELAY_VOLUME_ENVELOPE] = -12000
        self._gs[GeneratorType.ATTACK_VOLUME_ENVELOPE] = -12000
        self._gs[GeneratorType.HOLD_VOLUME_ENVELOPE] = -12000
        self._gs[GeneratorType.DECAY_VOLUME_ENVELOPE] = -12000
        self._gs[GeneratorType.RELEASE_VOLUME_ENVELOPE] = -12000
        self._gs[GeneratorType.KEY_RANGE] = 0x7F00
        self._gs[GeneratorType.VELOCITY_RANGE] = 0x7F00
        self._gs[GeneratorType.KEY_NUMBER] = -1
        self._gs[GeneratorType.VELOCITY] = -1
        self._gs[GeneratorType.SCALE_TUNING] = 100
        self._gs[GeneratorType.OVERRIDING_ROOT_KEY] = -1

        if global_generators != None:
            for parameter in global_generators:
                self.set_parameter(parameter)
        
        if local_generators != None:
            for parameter in local_generators:
                self.set_parameter(parameter)
        
        id = self._gs[GeneratorType.SAMPLE_ID]
        if not (0 <= id and id < len(samples)):
            raise Exception("The instrument '" + instrument.name + "' contains an invalid sample ID '" + id + "'.")
        self._sample = samples[id]
    
    @staticmethod
    def create(instrument: Instrument, zones: list, samples: list):

        global_zone: Zone = None

        # Is the first one the global zone?
        if len(zones[0].generators) == 0 or zones[0].generators[-1].generator_type != GeneratorType.SAMPLE_ID:
            # The first one is the global zone.
            global_zone = zones[0]
        
        if global_zone != None:
            # The global zone is regarded as the base setting of subsequent zones.
            count = len(zones) - 1
            regions = list()
            for i in range(count):
                regions.append(InstrumentRegion(instrument, global_zone.generators, zones[i + 1].generators, samples))
            return regions
        else:
            # No global zone.
            count = len(zones)
            regions = list()
            for i in range(count):
                regions.append(InstrumentRegion(instrument, None, zones[i].generators, samples))
            return regions

    def set_parameter(self, parameter: Generator):

        index = int(parameter.generator_type)

        # Unknown generators should be ignored.
        if 0 <= index and index < len(self._gs):
            self._gs[index] = parameter.value
    
    def contains(self, key: int, velocity: int):
        contains_key = self.key_range_start <= key and key <= self.key_range_end
        contains_velocity = self.velocity_range_start <= velocity and velocity <= self.velocity_range_end
        return contains_key and contains_velocity

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
        return 32768 * self._gs[GeneratorType.START_ADDRESS_COARSE_OFFSET] + self._gs[GeneratorType.START_ADDRESS_OFFSET]

    @property
    def end_address_offset(self) -> int:
        return 32768 * self._gs[GeneratorType.END_ADDRESS_COARSE_OFFSET] + self._gs[GeneratorType.END_ADDRESS_OFFSET]

    @property
    def start_loop_address_offset(self) -> int:
        return 32768 * self._gs[GeneratorType.START_LOOP_ADDRESS_COARSE_OFFSET] + self._gs[GeneratorType.START_LOOP_ADDRESS_OFFSET]

    @property
    def end_loop_address_offset(self) -> int:
        return 32768 * self._gs[GeneratorType.END_LOOP_ADDRESS_COARSE_OFFSET] + self._gs[GeneratorType.END_LOOP_ADDRESS_OFFSET]

    @property
    def modulation_lfo_to_pitch(self) -> int:
        return self._gs[GeneratorType.MODULATION_LFO_TO_PITCH]

    @property
    def vibrato_lfo_to_pitch(self) -> int:
        return self._gs[GeneratorType.VIBRATO_LFO_TO_PITCH]

    @property
    def modulation_envelope_to_pitch(self) -> int:
        return self._gs[GeneratorType.MODULATION_ENVELOPE_TO_PITCH]

    @property
    def initial_filter_cutoff_frequency(self) -> float:
        return SoundFontMath.cents_to_hertz(self._gs[GeneratorType.INITIAL_FILTER_CUTOFF_FREQUENCY])

    @property
    def initial_filter_q(self) -> float:
        return 0.1 * self._gs[GeneratorType.INITIAL_FILTER_Q]

    @property
    def modulation_lfo_to_filter_cutoff_frequency(self) -> int:
        return self._gs[GeneratorType.MODULATION_LFO_TO_FILTER_CUTOFF_FREQUENCY]

    @property
    def modulation_envelope_to_filter_cutoff_frequency(self) -> int:
        return self._gs[GeneratorType.MODULATION_ENVELOPE_TO_FILTER_CUTOFF_FREQUENCY]

    @property
    def modulation_lfo_to_volume(self) -> float:
        return 0.1 * self._gs[GeneratorType.MODULATION_LFO_TO_VOLUME]

    @property
    def chorus_effects_send(self) -> float:
        return 0.1 * self._gs[GeneratorType.CHORUS_EFFECTS_SEND]

    @property
    def reverb_effects_send(self) -> float:
        return 0.1 * self._gs[GeneratorType.REVERB_EFFECTS_SEND]

    @property
    def pan(self) -> float:
        return 0.1 * self._gs[GeneratorType.PAN]

    @property
    def delay_modulation_lfo(self) -> float:
        return SoundFontMath.timecents_to_seconds(self._gs[GeneratorType.DELAY_MODULATION_LFO])

    @property
    def frequency_modulation_lfo(self) -> float:
        return SoundFontMath.cents_to_hertz(self._gs[GeneratorType.FREQUENCY_MODULATION_LFO])

    @property
    def delay_vibrato_lfo(self) -> float:
        return SoundFontMath.timecents_to_seconds(self._gs[GeneratorType.DELAY_VIBRATO_LFO])

    @property
    def frequency_vibrato_lfo(self) -> float:
        return SoundFontMath.cents_to_hertz(self._gs[GeneratorType.FREQUENCY_VIBRATO_LFO])

    @property
    def delay_modulation_envelope(self) -> float:
        return SoundFontMath.timecents_to_seconds(self._gs[GeneratorType.DELAY_MODULATION_ENVELOPE])

    @property
    def attack_modulation_envelope(self) -> float:
        return SoundFontMath.timecents_to_seconds(self._gs[GeneratorType.ATTACK_MODULATION_ENVELOPE])

    @property
    def hold_modulation_envelope(self) -> float:
        return SoundFontMath.timecents_to_seconds(self._gs[GeneratorType.HOLD_MODULATION_ENVELOPE])

    @property
    def decay_modulation_envelope(self) -> float:
        return SoundFontMath.timecents_to_seconds(self._gs[GeneratorType.DECAY_MODULATION_ENVELOPE])

    @property
    def sustain_modulation_envelope(self) -> float:
        return 0.1 * self._gs[GeneratorType.SUSTAIN_MODULATION_ENVELOPE]

    @property
    def release_modulation_envelope(self) -> float:
        return SoundFontMath.timecents_to_seconds(self._gs[GeneratorType.RELEASE_MODULATION_ENVELOPE])

    @property
    def key_number_to_modulation_envelope_hold(self) -> int:
        return self._gs[GeneratorType.KEY_NUMBER_TO_MODULATION_ENVELOPE_HOLD]

    @property
    def key_number_to_modulation_envelope_decay(self) -> int:
        return self._gs[GeneratorType.KEY_NUMBER_TO_MODULATION_ENVELOPE_DECAY]

    @property
    def delay_volume_envelope(self) -> float:
        return SoundFontMath.timecents_to_seconds(self._gs[GeneratorType.DELAY_VOLUME_ENVELOPE])

    @property
    def attack_volume_envelope(self) -> float:
        return SoundFontMath.timecents_to_seconds(self._gs[GeneratorType.ATTACK_VOLUME_ENVELOPE])

    @property
    def hold_volume_envelope(self) -> float:
        return SoundFontMath.timecents_to_seconds(self._gs[GeneratorType.HOLD_VOLUME_ENVELOPE])

    @property
    def decay_volume_envelope(self) -> float:
        return SoundFontMath.timecents_to_seconds(self._gs[GeneratorType.DECAY_VOLUME_ENVELOPE])

    @property
    def sustain_volume_envelope(self) -> float:
        return 0.1 * self._gs[GeneratorType.SUSTAIN_VOLUME_ENVELOPE]

    @property
    def release_volume_envelope(self) -> float:
        return SoundFontMath.timecents_to_seconds(self._gs[GeneratorType.RELEASE_VOLUME_ENVELOPE])

    @property
    def key_number_to_volume_envelope_hold(self) -> int:
        return self._gs[GeneratorType.KEY_NUMBER_TO_VOLUME_ENVELOPE_HOLD]

    @property
    def key_number_to_volume_envelope_decay(self) -> int:
        return self._gs[GeneratorType.KEY_NUMBER_TO_VOLUME_ENVELOPE_DECAY]

    @property
    def key_range_start(self) -> int:
        return self._gs[GeneratorType.KEY_RANGE] & 0xFF

    @property
    def key_range_end(self) -> int:
        return (self._gs[GeneratorType.KEY_RANGE] >> 8) & 0xFF

    @property
    def velocity_range_start(self) -> int:
        return self._gs[GeneratorType.VELOCITY_RANGE] & 0xFF

    @property
    def velocity_range_end(self) -> int:
        return (self._gs[GeneratorType.VELOCITY_RANGE] >> 8) & 0xFF

    @property
    def initial_attenuation(self) -> float:
        return 0.1 * self._gs[GeneratorType.INITIAL_ATTENUATION]

    @property
    def coarse_tune(self) -> int:
        return self._gs[GeneratorType.COARSE_TUNE]

    @property
    def fine_tune(self) -> int:
        return self._gs[GeneratorType.FINE_TUNE] + self._sample.pitch_correction

    @property
    def sample_modes(self) -> LoopMode:
        return LoopMode(self._gs[GeneratorType.SAMPLE_MODES]) if self._gs[GeneratorType.SAMPLE_MODES] != 2 else LoopMode.NO_LOOP

    @property
    def scale_tuning(self) -> int:
        return self._gs[GeneratorType.SCALE_TUNING]

    @property
    def exclusive_class(self) -> int:
        return self._gs[GeneratorType.EXCLUSIVE_CLASS]

    @property
    def root_key(self) -> int:
        return self._gs[GeneratorType.OVERRIDING_ROOT_KEY] if self._gs[GeneratorType.OVERRIDING_ROOT_KEY] != -1 else self._sample.original_pitch





class SoundFontParameters:

    _sample_headers: list
    _presets: list
    _instruments: list

    def __init__(self, reader: io.BytesIO) -> None:
        
        chunk_id = BinaryReaderEx.read_four_cc(reader)
        if chunk_id != "LIST":
            raise Exception("The LIST chunk was not found.")
        
        end = reader.tell() + BinaryReaderEx.read_int32(reader)

        list_type = BinaryReaderEx.read_four_cc(reader)
        if list_type != "pdta":
            raise Exception("The type of the LIST chunk must be 'pdta', but was '" + list_type + "'.")

        preset_infos: list = None
        preset_bag: list = None
        preset_generators: list = None
        instrument_infos: list = None
        instrument_bag: list = None
        instrument_generators: list = None
        sample_headers: list = None

        while reader.tell() < end:

            id = BinaryReaderEx.read_four_cc(reader)
            size = BinaryReaderEx.read_uint32(reader)

            match id:

                case "phdr":
                    preset_infos = PresetInfo.read_from_chunk(reader, size)

                case "pbag":
                    preset_bag = ZoneInfo.read_from_chunk(reader, size)

                case "pmod":
                    Modulator.discard_data(reader, size)

                case "pgen":
                    preset_generators = Generator.read_from_chunk(reader, size)

                case "inst":
                    instrument_infos = InstrumentInfo.read_from_chunk(reader, size)

                case "ibag":
                    instrument_bag = ZoneInfo.read_from_chunk(reader, size)

                case "imod":
                    Modulator.discard_data(reader, size)

                case "igen":
                    instrument_generators = Generator.read_from_chunk(reader, size)

                case "shdr":
                    sample_headers = SampleHeader.read_from_chunk(reader, size)

                case _:
                    raise Exception("The INFO list contains an unknown ID '" + id + "'.")

        if preset_infos == None:
            raise Exception("The PHDR sub-chunk was not found.")
        
        if preset_bag == None:
            raise Exception("The PBAG sub-chunk was not found.")
        
        if preset_generators == None:
            raise Exception("The PGEN sub-chunk was not found.")
        
        if instrument_infos == None:
            raise Exception("The INST sub-chunk was not found.")
        
        if instrument_bag == None:
            raise Exception("The IBAG sub-chunk was not found.")
        
        if instrument_generators == None:
            raise Exception("The IGEN sub-chunk was not found.")
        
        if sample_headers == None:
            raise Exception("The SHDR sub-chunk was not found.")
        
        instrument_zones = Zone.create(instrument_bag, instrument_generators)
        self._instruments = Instrument.create(instrument_infos, instrument_zones, sample_headers)

        print("ok")





class SoundFont:

    info: SoundFontInfo
    aaaa: SoundFontSampleData

    def __init__(self, reader: io.BytesIO) -> None:

        chunk_id = BinaryReaderEx.read_four_cc(reader)
        if chunk_id != "RIFF":
            raise Exception("The RIFF chunk was not found.")

        size = BinaryReaderEx.read_uint32(reader)

        form_type = BinaryReaderEx.read_four_cc(reader)
        if form_type != "sfbk":
            raise Exception("The type of the RIFF chunk must be 'sfbk', but was '" + form_type + "'.")
        
        self.info = SoundFontInfo(reader)
        self.aaaa = SoundFontSampleData(reader)
        SoundFontParameters(reader)


