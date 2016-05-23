# -*- coding: utf-8 -*-
import codecs
from unittest import TestCase, skip
import pytest

from pyoracc.atf.atffile import AtfFile
from pyoracc.test.fixtures import belsunu, anzu, output_filepath

from ...atf.atflex import AtfLexer
from ...atf.atfyacc import AtfParser
from pyoracc.model.line import Line


class TestSerializer(TestCase):
    """A class that contains all tests of the ATF Serializer"""
    def setUp(self):
        """
        Initialize lexer and parser.
        """
        self.lexer = AtfLexer().lexer
        self.parser = AtfParser().parser

    @staticmethod
    def parse(any_str):
        """
        Parse input string, could be just a line or a whole file content.
        """
        parsed = AtfFile(any_str)
        return parsed

    def test_parse_anzu(self):
        parsed = AtfFile("""&X002001 = SB Anzu 1 
@composite
#project: cams/gkab
#atf: lang akk-x-stdbab



1.    bi#-in šar da-ad-mi šu-pa-a na-ram {d}ma#-mi

2.    gaš-ru lu-u-za-mur DINGIR bu-kur₂ {d#}[EN].LIL₂

3.    {d#}NIN.URTA šu-pa-a na-ram {d}ma-mi

4.    [gaš]-ru lu-ut-ta-aʾ-id DINGIR bu-kur₂ {d}EN.LIL₂

5.    i-lit-ti E₂.KUR a-ša₂-red {d}600 tu-kul-ti e₂-ninnu

54.    an-za-a-ma ta-ta-mar [x x x]

55.    li-iz-ziz ma-har-ka-ma a-a ip#-[par-šid-ka]

56.    lip#-tar-rik ina at-ma-ni šu-bat ki#-[iṣ-ṣi]
$ lines broken

60.    ta#-[mit] iq#-bu-šu DINGIR an-[na i-pu-ul]

61.    ma-ha-za i-ta-ha-az# [x x x x]

213.    ŠU.NIGIN# 3 UŠ 3#.03-AM₃



&Q002770 = SB Anzu 2
@composite
#project: cams/gkab
#atf: lang akk-x-stdbab



1.    bi-riq ur-ha šuk-na a-dan-na

2.    ana DINGIR-MEŠ šu-ut ab-nu-u na-mir-ta šu-uṣ-ṣi

153.    tam-ha-ru-šu i-[du-us-su i-qu-lu ziq-ziq-qu]

154.    ṭup-pi 2-KAM₂.MA [bi-in šar da-ad₂-me]

155.    ŠU.NIGIN# 2# UŠ# [53-AM₃]





&Q002771 = SB Anzu 3
@composite
#project: cams/gkab
#atf: lang akk-x-stdbab



1.    x x x [x x x x x x x x x x x]

2.    ša₂ ak# na x x ša₂# a#-na# x [x x x]

3.    ap-lu#-ha-nu de-ke-e x [x x]

75.    [x x x x]-ma# a-šak-kan# [x x x x x]

76.    [x x x] x pa-ni-ia# [x x x]
$ lines broken

113.    [x x x x x x x x] a#.a# ib-ba#-ni#

114.    [x x x x] x x x x an-zi-i ina E₂.KUR

115.    [x x] x-it-ta-šu₂ ša₂ qar-ra-di

168.    [x x x x x] ib-ba-nu-[u]

169.    [x x x x x] x x [x x]
$ lines broken

175.    [x x x x x x x x] x

176.    [x x x x x x x] ur-ha

$ single ruling

177.    [x x x x x] x ap#-lu#-ha#-nu-uš

178.    [x x x x] x x x x ba#

179.    [x x x x a]-ša₂?#-red qab-li

180.    [x x x x] x-ni-tu₂

181.    [x x x x] x-qa?-a-tu₂""")

    @staticmethod
    def serialize(any_object):
        """
        Serialize input object, from a simple lemma to a whole AtfFile object.
        """
        serialized = any_object.serialize()
        return serialized

    def parse_then_serialize(self, any_str):
        """
        Shorthand for testing serialization.
        """
        return self.serialize(self.parse(any_str))

    @staticmethod
    def open_file(filename):
        """
        Open serialized file and output contents
        """
        return codecs.open(filename, "r", "utf-8").read()

    @staticmethod
    def save_file(content, filename):
        """
        Write serialized file on disk
        """
        serialized_file = codecs.open(filename, "w", "utf-8")
        serialized_file.write(content)
        serialized_file.close()

    def test_belsunu_serializer(self):
        """
        Parse belsunu.atf, then serialize, parse again, serialize again,
        compare.
        Comparing serialized output with input file would bring up differences
        that might not be significant (white spaces, newlines, etc).
        The solution is to parse again the serialized file, serialize again,
        then compare the two serializations.
        """
        serialized_1 = self.parse_then_serialize(belsunu())
        self.save_file(serialized_1, output_filepath("belsunu.atf"))
        serialized_2 = self.parse_then_serialize(serialized_1)
        assert serialized_1 == serialized_2

    @pytest.mark.xfail
    @staticmethod
    def test_line_word():
        """
        Get a sample word with unicode chars and check serialization is
        correct.
        """
        line = Line("1")
        line.words.append(u"\u2086")
        line_ser = line.serialize()
        assert line_ser == "1.\t" + u"\u2086"

    def test_anzu_serializer(self):
        """
        Parse anzu.atf, then serialize, parse again, serialize again, compare. 
        Comparing serialized output with input file would bring up differences 
        that might not be significant (white spaces, newlines, etc).
        The solution is to parse again the serialized file, serialize again, 
        then compare the two serializations.
        """
        serialized_1 = self.parse_then_serialize(anzu())
        self.save_file(serialized_1, output_filepath("anzu.atf"))
        serialized_2 = self.parse_then_serialize(serialized_1)
        assert_equal(serialized_1, serialized_2)

    def test_line_words(self):
        """
        Get a sample line of words with unicode chars and test serialization.
        1. [MU] 1.03-KAM {iti}AB GE₆ U₄ 2-KAM
        """
        atf_file = AtfFile(belsunu())
        uline = atf_file.text.children[0].children[0].children[0]
        uwords = uline.words
        gold = [u'[MU]', u'1.03-KAM', u'{iti}AB', u'GE\u2086', u'U\u2084',
                u'2-KAM']
        assert uwords == gold

    @staticmethod
    def test_line_lemmas():
        """
        Get a sample line of lemmas with unicode chars and test serialization.
        šatti[year]N; n; Ṭebetu[1]MN; mūša[at night]AV; ūm[day]N; n
        """
        atf_file = AtfFile(belsunu())
        uline = atf_file.text.children[0].children[0].children[0]
        ulemmas = uline.lemmas
        gold = [u' \u0161atti[year]N', u'n', u'\u1e6cebetu[1]MN',
                u'm\u016b\u0161a[at night]AV', u'\u016bm[day]N', u'n']
        assert ulemmas == gold


# TODO: Build list of atf files for testing and make a test to go through the
# list of test and try serializing each of them.
    @pytest.mark.xfail
    def test_text_code_and_description(self):
        """
        Check if serializing works for the code/description case - first line
        of ATF texts.
        Note the parser always returns an AtfFile object, even when it's not
        ATF-compliant.
        """
        atf = self.parse("&X001001 = JCS 48, 089\n")
        serialized = self.serialize(atf)
        assert serialized.strip()+"\n" == "&X001001 = JCS 48, 089\n"

    @pytest.mark.xfail
    def test_text_project(self):
        """
        Check if serializing works for the project lines.
        Note the parser always returns an AtfFile object, even when it's not
        ATF-compliant.
        """
        serialized = self.parse_then_serialize("#project: cams/gkab\n")
        assert serialized.strip()+"\n" == "#project: cams/gkab\n"

    @skip("test_text_language is not implemented yet")
    def test_text_language(self):
        pass

    @skip("test_text_protocols is not implemented yet")
    def test_text_protocols(self):
        pass
