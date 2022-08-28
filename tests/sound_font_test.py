import io
import unittest

import meltysynth as ms



class TestTimGM6mb(unittest.TestCase):

    def test_sound_font_info(self):
        
        file = io.open("TimGM6mb.sf2", "rb")
        sf2 = ms.SoundFont(file)
        file.close()

        info = sf2.info
        self.assertEqual(info.version.major, 2)
        self.assertEqual(info.version.minor, 1)
        self.assertEqual(info.target_sound_engine, "EMU8000")
        self.assertEqual(info.bank_name, "TimGM6mb1.sf2")
        self.assertEqual(info.rom_name, "")
        self.assertEqual(info.rom_version.major, 0)
        self.assertEqual(info.rom_version.minor, 0)
        self.assertEqual(info.creation_date, "")
        self.assertEqual(info.author, "")
        self.assertEqual(info.target_product, "")
        self.assertEqual(info.copyright, "")
        self.assertEqual(info.comments, "")
        self.assertEqual(info.tools, "Awave Studio v8.5")



class TestGeneralUserGsMuseScore(unittest.TestCase):

    def test_sound_font_info(self):
        
        file = io.open("GeneralUser GS MuseScore v1.442.sf2", "rb")
        sf2 = ms.SoundFont(file)
        file.close()

        info = sf2.info
        self.assertEqual(info.version.major, 2)
        self.assertEqual(info.version.minor, 1)
        self.assertEqual(info.target_sound_engine, "E-mu 10K2")
        self.assertEqual(info.bank_name, "GeneralUser GS MuseScore version 1.442")
        self.assertEqual(info.rom_name, "")
        self.assertEqual(info.rom_version.major, 0)
        self.assertEqual(info.rom_version.minor, 0)
        self.assertEqual(info.creation_date, "")
        self.assertEqual(info.author, "S. Christian Collins")
        self.assertEqual(info.target_product, "")
        self.assertEqual(info.copyright, "2012 by S. Christian Collins")
        self.assertEqual(len(info.comments), 2207)
        self.assertEqual(info.tools, ":SFEDT v1.10:SFEDT v1.36:")
