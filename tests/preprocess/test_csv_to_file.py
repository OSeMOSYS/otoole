import io
from unittest.mock import Mock

from pytest import fixture

import pandas as pd

from otoole.preprocess.excel_to_osemosys import read_config
from otoole.preprocess.narrow_to_datafile import DataPackageToCsv


class TestDataFrameWriting:

    @fixture
    def setup(self) -> DataPackageToCsv:

        dp = DataPackageToCsv
        dp._get_package = Mock()
        dp._get_default_values = Mock()

        return dp('', '')

    def test_write_empty_parameter_with_defaults(self, setup):

        convert = setup  # typing: DataPackageToCsv

        data = []

        df = pd.DataFrame(data=data, columns=['REGION', 'FUEL', 'VALUE'])

        stream = io.StringIO()
        convert.write_parameter(df, 'test_parameter', stream, 0)

        stream.seek(0)
        expected = ['param default 0 : test_parameter :=\n',
                    ';\n']
        actual = stream.readlines()

        for actual_line, expected_line in zip(actual, expected):
            assert actual_line == expected_line

    def test_write_parameter_as_tabbing_format(self, setup):

        data = [['SIMPLICITY', 'BIOMASS', 0.95969],
                ['SIMPLICITY', 'ETH1', 4.69969]]

        df = pd.DataFrame(data=data, columns=['REGION', 'FUEL', 'VALUE'])

        stream = io.StringIO()
        convert = setup
        convert.write_parameter(df, 'test_parameter', stream, 0)

        stream.seek(0)
        expected = ['param default 0 : test_parameter :=\n',
                    'SIMPLICITY BIOMASS 0.95969\n',
                    'SIMPLICITY ETH1 4.69969\n',
                    ';\n']
        actual = stream.readlines()

        for actual_line, expected_line in zip(actual, expected):
            assert actual_line == expected_line

    def test_write_parameter_skip_defaults(self, setup):

        data = [['SIMPLICITY', 'BIOMASS', 0.95969],
                ['SIMPLICITY', 'ETH1', 4.69969],
                ['SIMPLICITY', 'ETH2', -1],
                ['SIMPLICITY', 'ETH3', -1]]

        df = pd.DataFrame(data=data, columns=['REGION', 'FUEL', 'VALUE'])

        stream = io.StringIO()
        convert = setup
        convert.write_parameter(df, 'test_parameter', stream, -1)

        stream.seek(0)
        expected = ['param default -1 : test_parameter :=\n',
                    'SIMPLICITY BIOMASS 0.95969\n',
                    'SIMPLICITY ETH1 4.69969\n',
                    ';\n']
        actual = stream.readlines()

        for actual_line, expected_line in zip(actual, expected):
            assert actual_line == expected_line

    def test_write_set(self, setup):

        data = [['BIOMASS'],
                ['ETH1']]

        df = pd.DataFrame(data=data, columns=['VALUE'])

        stream = io.StringIO()
        convert = setup
        convert.write_set(df, 'TECHNOLOGY', stream)

        stream.seek(0)
        expected = ['set TECHNOLOGY :=\n',
                    'BIOMASS\n',
                    'ETH1\n',
                    ';\n']
        actual = stream.readlines()

        for actual_line, expected_line in zip(actual, expected):
            assert actual_line == expected_line


class TestConfig:

    def test_read_config(self):

        actual = read_config()
        expected = {
                        'default': 0,
                        'dtype': 'float',
                        'indices': ['REGION', 'FUEL', 'YEAR'],
                        'type': 'param',
                    }
        assert actual['AccumulatedAnnualDemand'] == expected
