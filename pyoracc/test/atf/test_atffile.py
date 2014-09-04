from ...atf.atffile import AtfFile
from nose.tools import assert_in, assert_equal

from ..fixtures import anzu, belsunu, sample_file


def test_create():
    afile = AtfFile(belsunu())
    assert_equal(afile.text.code, "X001001")
    assert_equal(afile.text.description, "JCS 48, 089")


def test_composite():
    afile = AtfFile(anzu())
    assert_equal(afile.text.texts[0].code, "X002001")
    assert_equal(afile.text.texts[0].description, "SB Anzu 1")
    assert_equal(afile.text.texts[1].code, "Q002770")
    assert_equal(afile.text.texts[1].description, "SB Anzu 2")

def test_SAA_19():
    afile= AtfFile(sample_file('SAA19_13'))
    assert_equal(afile.text.texts[0].code, 'P393708')

def test_SAA_19_11():
    afile= AtfFile(sample_file('SAA19_11'))
    assert_equal(afile.text.texts[0].code, 'P224439')

def test_5_fm_erimh():
    afile= AtfFile(sample_file('5-fm-erimh-p'))
    assert_equal(afile.text.texts[0].code,'P346083')

def test_5_fm_emesal():
    afile= AtfFile(sample_file('5-fm-emesal-p'))
    assert_equal(afile.text.texts[0].code,'P228608')

def consider_file(name,code,description):
    afile = AtfFile(sample_file(name))
    assert_equal(afile.text.code, code)
    assert_equal(afile.text.description,description)

texts=[
    ['bb','X002002',"BagM Beih. 02, 005"],
    ['bb_2_6','X002004',"BagM Beih. 02, 006"],
    ['bb_2_7','X002005',"BagM Beih. 02, 007"],
    ['bb_2_10','X002006',"BagM Beih. 02, 010"],
    ['bb_2_13','X002013',"BagM Beih. 02, 013"],
    ['bb_2_61','X002061',"BagM Beih. 02, 061"],
    ['bb_2_062','P363326','BagM Beih. 02, 062'],
    ['bb_2_79','X002079',"BagM Beih. 02, 079"],
    ['bb_2_83','X002083',"Bagm Beih. 02, 083"],
    ['bb_2_96','X002096',"BagM Beih. 02, 096"],
    ['afo','X002003','AfO 14, Taf. VI'],
    ['brm_4_6','P363407','BRM 4, 06'],
    ['brm_4_19','P363411','BRM 4, 19'],
    ['cm_31_139','P415763','CM 31, 139'],
    ['ctn_4_006','P363421','CTN 4, 006'],
    ['Senn2002','Q004089','Sennacherib 2002'],
    ['Esar1014','Q003386','Esarhaddon 1014'],
    ['Esar0032','Q003261','Esarhaddon 32'],
    ['UF_10_16','P405422','UF 10, 16'],
    ['P229574','P229574','MSL 13, 14 Q1'],
    ['MEE15_54','P244115','MEE 15, 054'],
    ['BagM_27_217','P405130','BagM 27 217'],
    ['3-ob-ura2-q-l-t','Q000040','OB Nippur Ura 2'],
    ['TPIII0001','Q003414','Tiglath-pileser III 1'],
    ['K_04145F','P382580','CT 11, pl. 33, K 04145F']
    ]

def test_texts():
    for text in texts:
        yield [consider_file]+text
