import math
import unittest

import meltysynth as ms

class RegionUtils:

    @staticmethod
    def are_equal(x: float, y: float) -> bool:

        if math.floor(x) == math.ceil(x) and math.floor(y) == math.ceil(y):
            return x == y
        
        m = max(abs(x), abs(y))
        limit = m / 1000
        delta = abs(x - y)
        if delta > limit:
            return False
        
        return True
    
    @staticmethod
    def check_instrument_region(test_case: unittest.TestCase, instrument: ms.Instrument, region: ms.InstrumentRegion, values: list):

        test_case.assertTrue(RegionUtils.are_equal(region.sample_start, values[0]), instrument.name + "_sample_start")
        test_case.assertTrue(RegionUtils.are_equal(region.sample_end, values[1]), instrument.name + "_sample_end")
        test_case.assertTrue(RegionUtils.are_equal(region.sample_start_loop, values[2]), instrument.name + "_sample_start_loop")
        test_case.assertTrue(RegionUtils.are_equal(region.sample_end_loop, values[3]), instrument.name + "_sample_end_loop")
        test_case.assertTrue(RegionUtils.are_equal(region.start_address_offset, values[4]), instrument.name + "_start_address_offset")
        test_case.assertTrue(RegionUtils.are_equal(region.end_address_offset, values[5]), instrument.name + "_end_address_offset")
        test_case.assertTrue(RegionUtils.are_equal(region.start_loop_address_offset, values[6]), instrument.name + "_start_loop_address_offset")
        test_case.assertTrue(RegionUtils.are_equal(region.end_loop_address_offset, values[7]), instrument.name + "_end_loop_address_offset")
        test_case.assertTrue(RegionUtils.are_equal(region.modulation_lfo_to_pitch, values[8]), instrument.name + "_modulation_lfo_to_pitch")
        test_case.assertTrue(RegionUtils.are_equal(region.vibrato_lfo_to_pitch, values[9]), instrument.name + "_vibrato_lfo_to_pitch")
        test_case.assertTrue(RegionUtils.are_equal(region.modulation_envelope_to_pitch, values[10]), instrument.name + "_modulation_envelope_to_pitch")
        test_case.assertTrue(RegionUtils.are_equal(region.initial_filter_cutoff_frequency, values[11]), instrument.name + "_initial_filter_cutoff_frequency")
        test_case.assertTrue(RegionUtils.are_equal(region.initial_filter_q, values[12]), instrument.name + "_initial_filter_q")
        test_case.assertTrue(RegionUtils.are_equal(region.modulation_lfo_to_filter_cutoff_frequency, values[13]), instrument.name + "_modulation_lfo_to_filter_cutoff_frequency")
        test_case.assertTrue(RegionUtils.are_equal(region.modulation_envelope_to_filter_cutoff_frequency, values[14]), instrument.name + "_modulation_envelope_to_filter_cutoff_frequency")
        test_case.assertTrue(RegionUtils.are_equal(region.modulation_lfo_to_volume, values[15]), instrument.name + "_modulation_lfo_to_volume")
        test_case.assertTrue(RegionUtils.are_equal(region.chorus_effects_send, values[16]), instrument.name + "_chorus_effects_send")
        test_case.assertTrue(RegionUtils.are_equal(region.reverb_effects_send, values[17]), instrument.name + "_reverb_effects_send")
        test_case.assertTrue(RegionUtils.are_equal(region.pan, values[18]), instrument.name + "_pan")
        test_case.assertTrue(RegionUtils.are_equal(region.delay_modulation_lfo, values[19]), instrument.name + "_delay_modulation_lfo")
        test_case.assertTrue(RegionUtils.are_equal(region.frequency_modulation_lfo, values[20]), instrument.name + "_frequency_modulation_lfo")
        test_case.assertTrue(RegionUtils.are_equal(region.delay_vibrato_lfo, values[21]), instrument.name + "_delay_vibrato_lfo")
        test_case.assertTrue(RegionUtils.are_equal(region.frequency_vibrato_lfo, values[22]), instrument.name + "_frequency_vibrato_lfo")
        test_case.assertTrue(RegionUtils.are_equal(region.delay_modulation_envelope, values[23]), instrument.name + "_delay_modulation_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.attack_modulation_envelope, values[24]), instrument.name + "_attack_modulation_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.hold_modulation_envelope, values[25]), instrument.name + "_hold_modulation_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.decay_modulation_envelope, values[26]), instrument.name + "_decay_modulation_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.sustain_modulation_envelope, values[27]), instrument.name + "_sustain_modulation_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.release_modulation_envelope, values[28]), instrument.name + "_release_modulation_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.key_number_to_modulation_envelope_hold, values[29]), instrument.name + "_key_number_to_modulation_envelope_hold")
        test_case.assertTrue(RegionUtils.are_equal(region.key_number_to_modulation_envelope_decay, values[30]), instrument.name + "_key_number_to_modulation_envelope_decay")
        test_case.assertTrue(RegionUtils.are_equal(region.delay_volume_envelope, values[31]), instrument.name + "_delay_volume_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.attack_volume_envelope, values[32]), instrument.name + "_attack_volume_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.hold_volume_envelope, values[33]), instrument.name + "_hold_volume_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.decay_volume_envelope, values[34]), instrument.name + "_decay_volume_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.sustain_volume_envelope, values[35]), instrument.name + "_sustain_volume_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.release_volume_envelope, values[36]), instrument.name + "_release_volume_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.key_number_to_volume_envelope_hold, values[37]), instrument.name + "_key_number_to_volume_envelope_hold")
        test_case.assertTrue(RegionUtils.are_equal(region.key_number_to_volume_envelope_decay, values[38]), instrument.name + "_key_number_to_volume_envelope_decay")
        test_case.assertTrue(RegionUtils.are_equal(region.key_range_start, values[39]), instrument.name + "_key_range_start")
        test_case.assertTrue(RegionUtils.are_equal(region.key_range_end, values[40]), instrument.name + "_key_range_end")
        test_case.assertTrue(RegionUtils.are_equal(region.velocity_range_start, values[41]), instrument.name + "_velocity_range_start")
        test_case.assertTrue(RegionUtils.are_equal(region.velocity_range_end, values[42]), instrument.name + "_velocity_range_end")
        test_case.assertTrue(RegionUtils.are_equal(region.initial_attenuation, values[43]), instrument.name + "_initial_attenuation")
        test_case.assertTrue(RegionUtils.are_equal(region.coarse_tune, values[44]), instrument.name + "_coarse_tune")
        test_case.assertTrue(RegionUtils.are_equal(region.fine_tune, values[45]), instrument.name + "_fine_tune")
        test_case.assertTrue(RegionUtils.are_equal(region.sample_modes, values[46]), instrument.name + "_sample_modes")
        test_case.assertTrue(RegionUtils.are_equal(region.scale_tuning, values[47]), instrument.name + "_scale_tuning")
        test_case.assertTrue(RegionUtils.are_equal(region.exclusive_class, values[48]), instrument.name + "_exclusive_class")
        test_case.assertTrue(RegionUtils.are_equal(region.root_key, values[49]), instrument.name + "_root_key")

    @staticmethod
    def check_preset_region(test_case: unittest.TestCase, preset: ms.Preset, region: ms.PresetRegion, values: list):

        test_case.assertTrue(RegionUtils.are_equal(region.modulation_lfo_to_pitch, values[0]), preset.name + "_modulation_lfo_to_pitch")
        test_case.assertTrue(RegionUtils.are_equal(region.vibrato_lfo_to_pitch, values[1]), preset.name + "_vibrato_lfo_to_pitch")
        test_case.assertTrue(RegionUtils.are_equal(region.modulation_envelope_to_pitch, values[2]), preset.name + "_modulation_envelope_to_pitch")
        test_case.assertTrue(RegionUtils.are_equal(region.initial_filter_cutoff_frequency, values[3]), preset.name + "_initial_filter_cutoff_frequency")
        test_case.assertTrue(RegionUtils.are_equal(region.initial_filter_q, values[4]), preset.name + "_initial_filter_q")
        test_case.assertTrue(RegionUtils.are_equal(region.modulation_lfo_to_filter_cutoff_frequency, values[5]), preset.name + "_modulation_lfo_to_filter_cutoff_frequency")
        test_case.assertTrue(RegionUtils.are_equal(region.modulation_envelope_to_filter_cutoff_frequency, values[6]), preset.name + "_modulation_envelope_to_filter_cutoff_frequency")
        test_case.assertTrue(RegionUtils.are_equal(region.modulation_lfo_to_volume, values[7]), preset.name + "_modulation_lfo_to_volume")
        test_case.assertTrue(RegionUtils.are_equal(region.chorus_effects_send, values[8]), preset.name + "_chorus_effects_send")
        test_case.assertTrue(RegionUtils.are_equal(region.reverb_effects_send, values[9]), preset.name + "_reverb_effects_send")
        test_case.assertTrue(RegionUtils.are_equal(region.pan, values[10]), preset.name + "_pan")
        test_case.assertTrue(RegionUtils.are_equal(region.delay_modulation_lfo, values[11]), preset.name + "_delay_modulation_lfo")
        test_case.assertTrue(RegionUtils.are_equal(region.frequency_modulation_lfo, values[12]), preset.name + "_frequency_modulation_lfo")
        test_case.assertTrue(RegionUtils.are_equal(region.delay_vibrato_lfo, values[13]), preset.name + "_delay_vibrato_lfo")
        test_case.assertTrue(RegionUtils.are_equal(region.frequency_vibrato_lfo, values[14]), preset.name + "_frequency_vibrato_lfo")
        test_case.assertTrue(RegionUtils.are_equal(region.delay_modulation_envelope, values[15]), preset.name + "_delay_modulation_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.attack_modulation_envelope, values[16]), preset.name + "_attack_modulation_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.hold_modulation_envelope, values[17]), preset.name + "_hold_modulation_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.decay_modulation_envelope, values[18]), preset.name + "_decay_modulation_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.sustain_modulation_envelope, values[19]), preset.name + "_sustain_modulation_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.release_modulation_envelope, values[20]), preset.name + "_release_modulation_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.key_number_to_modulation_envelope_hold, values[21]), preset.name + "_key_number_to_modulation_envelope_hold")
        test_case.assertTrue(RegionUtils.are_equal(region.key_number_to_modulation_envelope_decay, values[22]), preset.name + "_key_number_to_modulation_envelope_decay")
        test_case.assertTrue(RegionUtils.are_equal(region.delay_volume_envelope, values[23]), preset.name + "_delay_volume_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.attack_volume_envelope, values[24]), preset.name + "_attack_volume_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.hold_volume_envelope, values[25]), preset.name + "_hold_volume_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.decay_volume_envelope, values[26]), preset.name + "_decay_volume_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.sustain_volume_envelope, values[27]), preset.name + "_sustain_volume_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.release_volume_envelope, values[28]), preset.name + "_release_volume_envelope")
        test_case.assertTrue(RegionUtils.are_equal(region.key_number_to_volume_envelope_hold, values[29]), preset.name + "_key_number_to_volume_envelope_hold")
        test_case.assertTrue(RegionUtils.are_equal(region.key_number_to_volume_envelope_decay, values[30]), preset.name + "_key_number_to_volume_envelope_decay")
        test_case.assertTrue(RegionUtils.are_equal(region.key_range_start, values[31]), preset.name + "_key_range_start")
        test_case.assertTrue(RegionUtils.are_equal(region.key_range_end, values[32]), preset.name + "_key_range_end")
        test_case.assertTrue(RegionUtils.are_equal(region.velocity_range_start, values[33]), preset.name + "_velocity_range_start")
        test_case.assertTrue(RegionUtils.are_equal(region.velocity_range_end, values[34]), preset.name + "_velocity_range_end")
        test_case.assertTrue(RegionUtils.are_equal(region.initial_attenuation, values[35]), preset.name + "_initial_attenuation")
        test_case.assertTrue(RegionUtils.are_equal(region.coarse_tune, values[36]), preset.name + "_coarse_tune")
        test_case.assertTrue(RegionUtils.are_equal(region.fine_tune, values[37]), preset.name + "_fine_tune")
        test_case.assertTrue(RegionUtils.are_equal(region.scale_tuning, values[38]), preset.name + "_scale_tuning")
