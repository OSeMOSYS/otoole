from pytest import mark
from io import StringIO
from textwrap import dedent
import pandas as pd
from otoole.results.convert import ConvertLine

from otoole.results.convert import (
    ConvertLine,
    check_duplicate_index,
    convert_cbc_to_dataframe,
    convert_cbc_to_df,
    convert_dataframe_to_csv,
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
            actual = convert_cbc_to_df(file_buffer, {})["Trade"]
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
        actual = convert_dataframe_to_csv(prelim_data, {})["Trade"]
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


class TestCplexToCsv:

    test_data = [
        (
            "AnnualFixedOperatingCost	REGION	AOBACKSTOP	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0		",
            [],
        ),
        (
            "AnnualFixedOperatingCost	REGION	CDBACKSTOP	0.0	0.0	137958.8400384134	305945.38410619126	626159.9611543404	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0",
            [
                'AnnualFixedOperatingCost,"REGION,CDBACKSTOP,2017",137958.8400384134\n',
                'AnnualFixedOperatingCost,"REGION,CDBACKSTOP,2018",305945.3841061913\n',
                'AnnualFixedOperatingCost,"REGION,CDBACKSTOP,2019",626159.9611543404\n',
            ],
        ),
        (
            """RateOfActivity	REGION	S1D1	CGLFRCFURX	1	0.0	0.0	0.0	0.0	0.0	0.3284446367303371	0.3451714779880536	0.3366163200621617	0.3394945166233896	0.3137488154250392	0.28605725055560716	0.2572505015401749	0.06757558148965725	0.0558936625751148	0.04330608461292407	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0""",
            [
                'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2020",0.3284446367303371\n',
                'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2021",0.3451714779880536\n',
                'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2022",0.3366163200621617\n',
                'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2023",0.3394945166233896\n',
                'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2024",0.3137488154250392\n',
                'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2025",0.28605725055560716\n',
                'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2026",0.2572505015401749\n',
                'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2027",0.06757558148965725\n',
                'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2028",0.0558936625751148\n',
                'RateOfActivity,"REGION,S1D1,CGLFRCFURX,1,2029",0.04330608461292407\n',
            ],
        ),
    ]

    @mark.parametrize("cplex_input,expected", test_data)
    def test_convert_from_cplex_to_cbc(self, cplex_input, expected):

        row_as_list = cplex_input.split("\t")
        actual = ConvertLine(row_as_list, 2015, 2070, "csv").convert()
        assert actual == expected


class TestCplexToCbc:

    test_data = [
        (
            "AnnualFixedOperatingCost	REGION	AOBACKSTOP	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0		",
            [],
        ),
        (
            "AnnualFixedOperatingCost	REGION	CDBACKSTOP	0.0	0.0	137958.8400384134	305945.38410619126	626159.9611543404	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0",
            [
                "0 AnnualFixedOperatingCost(REGION,CDBACKSTOP,2017) 137958.8400384134 0\n",
                "0 AnnualFixedOperatingCost(REGION,CDBACKSTOP,2018) 305945.3841061913 0\n",
                "0 AnnualFixedOperatingCost(REGION,CDBACKSTOP,2019) 626159.9611543404 0\n",
            ],
        ),
        (
            """RateOfActivity	REGION	S1D1	CGLFRCFURX	1	0.0	0.0	0.0	0.0	0.0	0.3284446367303371	0.3451714779880536	0.3366163200621617	0.3394945166233896	0.3137488154250392	0.28605725055560716	0.2572505015401749	0.06757558148965725	0.0558936625751148	0.04330608461292407	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0""",
            [
                "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2020) 0.3284446367303371 0\n",
                "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2021) 0.3451714779880536 0\n",
                "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2022) 0.3366163200621617 0\n",
                "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2023) 0.3394945166233896 0\n",
                "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2024) 0.3137488154250392 0\n",
                "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2025) 0.28605725055560716 0\n",
                "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2026) 0.2572505015401749 0\n",
                "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2027) 0.06757558148965725 0\n",
                "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2028) 0.0558936625751148 0\n",
                "0 RateOfActivity(REGION,S1D1,CGLFRCFURX,1,2029) 0.04330608461292407 0\n",
            ],
        ),
    ]

    @mark.parametrize("cplex_input,expected", test_data)
    def test_convert_from_cplex_to_cbc(self, cplex_input, expected):

        row_as_list = cplex_input.split("\t")
        actual = ConvertLine(row_as_list, 2015, 2070, "cbc").convert()
        assert actual == expected
