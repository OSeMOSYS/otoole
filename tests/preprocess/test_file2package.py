import pandas as pd
from pulp.amply import Amply

from otoole.preprocess.datafile_to_datapackage import (
    convert_amply_data_to_list,
    convert_amply_to_dataframe,
    load_parameter_definitions
)


def test_amply():

    Amply("""set REGION;
          # set REGION := SIMPLICITY;
          set TECHNOLOGY;
          set TECHNOLOGY := ETHPLANT GAS_EXTRACTION;
          set MODE_OF_OPERATION;
          set MODE_OF_OPERATION := 1 2;
          set YEAR;
          set YEAR := 2014;
          end;""")


def test_convert_amply_to_dataframe():

    config = {'VariableCost': {'type': 'param',
                               'indices': ['REGION', 'TECHNOLOGY', 'MODE_OF_OPERATION', 'YEAR'],
                               'dtype': 'float',
                               'default': 0},
              'REGION': {'type': 'set', 'dtype': 'str'},
              'YEAR': {'dtype': 'int', 'type': 'set'},
              'MODE_OF_OPERATION': {'dtype': 'int', 'type': 'set'},
              'TECHNOLOGY': {'dtype': 'str', 'type': 'set'}}

    amply = Amply("""set REGION;
                     set REGION := SIMPLICITY;
                     set TECHNOLOGY;
                     set TECHNOLOGY := ETHPLANT GAS_EXTRACTION;
                     set MODE_OF_OPERATION;
                     set MODE_OF_OPERATION := 1 2;
                     set YEAR;
                     set YEAR := 2014;""")
    amply.load_string(
        "param VariableCost {REGION,TECHNOLOGY,MODE_OF_OPERATION,YEAR};")
#     amply.load_string("""param default 0 : VariableCost :=
# SIMPLICITY ETHPLANT 1 2014 2.89
# SIMPLICITY ETHPLANT 2 2014 999999.0
# SIMPLICITY GAS_EXTRACTION 1 2014 7.5
# SIMPLICITY GAS_EXTRACTION 2 2014 999999.0""")
    amply.load_string("""
param VariableCost default 0.0001 :=
[SIMPLICITY,ETHPLANT,*,*]:
2014 :=
1 2.89
2 999999.0
[SIMPLICITY,GAS_EXTRACTION,*,*]:
2014 :=
1 7.5
2 999999.0;""")
    actual = convert_amply_to_dataframe(amply, config)
    expected = pd.DataFrame(
        data=[['SIMPLICITY', 'ETHPLANT', 1, 2014, 2.89],
              ['SIMPLICITY', 'ETHPLANT', 2, 2014, 999999.0],
              ['SIMPLICITY', 'GAS_EXTRACTION', 1, 2014, 7.5],
              ['SIMPLICITY', 'GAS_EXTRACTION', 2, 2014, 999999.0]],
        columns=['REGION', 'TECHNOLOGY', 'MODE_OF_OPERATION', 'YEAR', 'VALUE'])

    pd.testing.assert_frame_equal(actual['VariableCost'], expected)


def test_convert_amply_data_to_list_of_lists():

    data = {'SIMPLICITY': {
        'ETHPLANT': {
            1.0: {2014.0: 2.89},
            2.0: {2014.0: 999999.0}},
        'GAS_EXTRACTION': {
            1.0: {2014.0: 7.5},
            2.0: {2014.0: 999999.0}},
                            }
            }
    expected = [['SIMPLICITY', 'ETHPLANT', 1.0, 2014.0, 2.89],
                ['SIMPLICITY', 'ETHPLANT', 2.0, 2014.0, 999999.0],
                ['SIMPLICITY', 'GAS_EXTRACTION', 1.0, 2014.0, 7.5],
                ['SIMPLICITY', 'GAS_EXTRACTION', 2.0, 2014.0, 999999.0]]
    actual = convert_amply_data_to_list(data)
    assert actual == expected


def test_load_parameters():

    config = {
        'TestParameter': {'type': 'param',
                          'indices': ['index1', 'index2']}}

    actual = load_parameter_definitions(config)
    expected = 'param TestParameter {index1,index2};\n'
    assert actual == expected


def test_load_sets():

    config = {
        'TestSet': {'type': 'set'}}

    actual = load_parameter_definitions(config)
    expected = 'set TestSet;\n'
    assert actual == expected
