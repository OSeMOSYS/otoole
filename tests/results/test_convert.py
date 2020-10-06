from io import StringIO
from textwrap import dedent

from pytest import mark

import pandas as pd

from otoole.results.results import (
    ReadCbc,
    check_duplicate_index,
    identify_duplicate,
    rename_duplicate_column,
)


class TestCbcToOtooleDataFrame:

    cbc_data = dedent(
        """0 Trade(Globe,Globe,IP,L_AGR,2015) -0.0 0
0 Trade(Globe,Globe,IP,L_AGR,2016) -1.0 0
0 Trade(Globe,Globe,IP,L_AGR,2017) -2.0 0
0 Trade(Globe,Globe,IP,L_AGR,2018) -3.0 0
0 Trade(Globe,Globe,IP,L_AGR,2019) -4.0 0
0 Trade(Globe,Globe,IP,L_AGR,2020) -5.0 0
            """
    )
    otoole_data = pd.DataFrame(
        data=[
            ["Globe", "Globe", "IP", "L_AGR", 2016, -1.0],
            ["Globe", "Globe", "IP", "L_AGR", 2017, -2.0],
            ["Globe", "Globe", "IP", "L_AGR", 2018, -3.0],
            ["Globe", "Globe", "IP", "L_AGR", 2019, -4.0],
            ["Globe", "Globe", "IP", "L_AGR", 2020, -5.0],
        ],
        columns=["REGION", "_REGION", "TIMESLICE", "FUEL", "YEAR", "VALUE"],
    ).set_index(["REGION", "_REGION", "TIMESLICE", "FUEL", "YEAR"])

    test_data = [(cbc_data, otoole_data,)]

    @mark.parametrize("cbc_input,expected", test_data)
    def test_read_cbc_to_otoole_dataframe(self, cbc_input, expected):
        with StringIO(cbc_input) as file_buffer:
            actual = ReadCbc().read(file_buffer, kwargs={"input_data": {}})[0]["Trade"]
        pd.testing.assert_frame_equal(actual, expected)

    def test_read_cbc_dataframe_to_otoole_dataframe(self):

        prelim_data = pd.DataFrame(
            data=[
                ["Trade", "Globe,Globe,IP,L_AGR,2016", -1.0],
                ["Trade", "Globe,Globe,IP,L_AGR,2017", -2.0],
                ["Trade", "Globe,Globe,IP,L_AGR,2018", -3.0],
                ["Trade", "Globe,Globe,IP,L_AGR,2019", -4.0],
                ["Trade", "Globe,Globe,IP,L_AGR,2020", -5.0],
            ],
            columns=["Variable", "Index", "Value"],
        )
        actual = ReadCbc()._convert_dataframe_to_csv(prelim_data, {})["Trade"]
        pd.testing.assert_frame_equal(actual, self.otoole_data)

    test_data_2 = [
        (["REGION", "REGION", "TIMESLICE", "FUEL", "YEAR"], True),
        (["REGION", "TIMESLICE", "FUEL", "YEAR"], False),
        ([], False),
    ]

    @mark.parametrize("data,expected", test_data_2)
    def test_handle_duplicate_indices(self, data, expected):
        assert check_duplicate_index(data) is expected

    test_data_3 = [
        (["REGION", "REGION", "TIMESLICE", "FUEL", "YEAR"], 1),
        (["REGION", "TIMESLICE", "FUEL", "YEAR"], False),
        ([], False),
    ]

    @mark.parametrize("data,expected", test_data_3)
    def test_identify_duplicate(self, data, expected):
        assert identify_duplicate(data) == expected

    def test_rename_duplicate_column(self):
        data = ["REGION", "REGION", "TIMESLICE", "FUEL", "YEAR"]
        actual = rename_duplicate_column(data)
        expected = ["REGION", "_REGION", "TIMESLICE", "FUEL", "YEAR"]
        assert actual == expected
