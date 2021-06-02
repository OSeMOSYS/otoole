from pytest import mark

import os
import pandas as pd
from amply import Amply
from io import StringIO
from textwrap import dedent
from typing import List

from otoole import ReadDatafile, ReadExcel, ReadMemory
from otoole.preprocess.longify_data import check_datatypes
from otoole.results.results import (
    ReadCbc,
    ReadCplex,
    ReadGurobi,
    check_for_duplicates,
    identify_duplicate,
    rename_duplicate_column,
)


class TestReadCplex:

    cplex_empty = "AnnualFixedOperatingCost	REGION	AOBACKSTOP	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0"
    cplex_short = "AnnualFixedOperatingCost	REGION	CDBACKSTOP	0.0	0.0	137958.8400384134	305945.38410619126	626159.9611543404	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0"
    cplex_long = "RateOfActivity	REGION	S1D1	CGLFRCFURX	1	0.0	0.0	0.0	0.0	0.0	0.3284446367303371	0.3451714779880536	0.3366163200621617	0.3394945166233896	0.3137488154250392	0.28605725055560716	0.2572505015401749	0.06757558148965725	0.0558936625751148	0.04330608461292407	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0"

    cplex_mid_empty = (
        pd.DataFrame(
            data=[],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        )
        .astype({"VALUE": float})
        .set_index(["REGION", "TECHNOLOGY", "YEAR"])
    )

    cplex_mid_short = pd.DataFrame(
        data=[
            ["REGION", "CDBACKSTOP", 2017, 137958.8400384134],
            ["REGION", "CDBACKSTOP", 2018, 305945.38410619126],
            ["REGION", "CDBACKSTOP", 2019, 626159.9611543404],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

    cplex_mid_long = pd.DataFrame(
        data=[
            ["REGION", "S1D1", "CGLFRCFURX", 1, 2020, 0.3284446367303371],
            ["REGION", "S1D1", "CGLFRCFURX", 1, 2021, 0.3451714779880536],
            ["REGION", "S1D1", "CGLFRCFURX", 1, 2022, 0.3366163200621617],
            ["REGION", "S1D1", "CGLFRCFURX", 1, 2023, 0.3394945166233896],
            ["REGION", "S1D1", "CGLFRCFURX", 1, 2024, 0.3137488154250392],
            ["REGION", "S1D1", "CGLFRCFURX", 1, 2025, 0.28605725055560716],
            ["REGION", "S1D1", "CGLFRCFURX", 1, 2026, 0.2572505015401749],
            ["REGION", "S1D1", "CGLFRCFURX", 1, 2027, 0.06757558148965725],
            ["REGION", "S1D1", "CGLFRCFURX", 1, 2028, 0.0558936625751148],
            ["REGION", "S1D1", "CGLFRCFURX", 1, 2029, 0.04330608461292407],
        ],
        columns=[
            "REGION",
            "TIMESLICE",
            "TECHNOLOGY",
            "MODE_OF_OPERATION",
            "YEAR",
            "VALUE",
        ],
    ).set_index(["REGION", "TIMESLICE", "TECHNOLOGY", "MODE_OF_OPERATION", "YEAR"])

    dataframe_short = {
        "AnnualFixedOperatingCost": pd.DataFrame(
            data=[
                ["REGION", "CDBACKSTOP", 2017, 137958.8400384134],
                ["REGION", "CDBACKSTOP", 2018, 305945.3841061913],
                ["REGION", "CDBACKSTOP", 2019, 626159.9611543404],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    }

    dataframe_long = {
        "RateOfActivity": pd.DataFrame(
            data=[
                ["REGION", "S1D1", "CGLFRCFURX", 1, 2020, 0.3284446367303371],
                ["REGION", "S1D1", "CGLFRCFURX", 1, 2021, 0.3451714779880536],
                ["REGION", "S1D1", "CGLFRCFURX", 1, 2022, 0.3366163200621617],
                ["REGION", "S1D1", "CGLFRCFURX", 1, 2023, 0.3394945166233896],
                ["REGION", "S1D1", "CGLFRCFURX", 1, 2024, 0.3137488154250392],
                ["REGION", "S1D1", "CGLFRCFURX", 1, 2025, 0.28605725055560716],
                ["REGION", "S1D1", "CGLFRCFURX", 1, 2026, 0.2572505015401749],
                ["REGION", "S1D1", "CGLFRCFURX", 1, 2027, 0.06757558148965725],
                ["REGION", "S1D1", "CGLFRCFURX", 1, 2028, 0.0558936625751148],
                ["REGION", "S1D1", "CGLFRCFURX", 1, 2029, 0.04330608461292407],
            ],
            columns=[
                "REGION",
                "TIMESLICE",
                "TECHNOLOGY",
                "MODE_OF_OPERATION",
                "YEAR",
                "VALUE",
            ],
        ).set_index(["REGION", "TIMESLICE", "TECHNOLOGY", "MODE_OF_OPERATION", "YEAR"])
    }

    test_data = [
        (cplex_short, dataframe_short),
        (cplex_long, dataframe_long),
    ]

    @mark.parametrize("cplex_input,expected", test_data, ids=["short", "long"])
    def test_read_cplex_to_dataframe(self, cplex_input, expected):
        cplex_reader = ReadCplex()

        input_data = {
            "YEAR": pd.DataFrame(data=list(range(2015, 2071, 1)), columns=["VALUE"])
        }

        with StringIO(cplex_input) as file_buffer:
            actual, _ = cplex_reader.read(file_buffer, input_data=input_data)
        for name, item in actual.items():
            pd.testing.assert_frame_equal(item, expected[name])

    test_data_mid = [(cplex_short, cplex_mid_short), (cplex_long, cplex_mid_long)]

    def test_read_empty_cplex_to_dataframe(self):
        cplex_input = self.cplex_empty

        cplex_reader = ReadCplex()

        input_data = {
            "YEAR": pd.DataFrame(data=list(range(2015, 2071, 1)), columns=["VALUE"])
        }

        with StringIO(cplex_input) as file_buffer:
            data, _ = cplex_reader.read(file_buffer, input_data=input_data)
        assert "AnnualFixedOperatingCost" in data
        expected = (
            pd.DataFrame(
                [],
                columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
            )
            .astype({"REGION": str, "VALUE": float, "YEAR": int})
            .set_index(["REGION", "TECHNOLOGY", "YEAR"])
        )
        actual = data["AnnualFixedOperatingCost"]
        pd.testing.assert_frame_equal(actual, expected, check_index_type=False)

    test_data_to_cplex = [
        (cplex_empty, cplex_mid_empty),
        (cplex_short, cplex_mid_short),
        (cplex_long, cplex_mid_long),
    ]

    @mark.parametrize(
        "cplex_input,expected", test_data_to_cplex, ids=["empty", "short", "long"]
    )
    def test_convert_cplex_to_df(self, cplex_input, expected):

        data = cplex_input.split("\t")
        variable = data[0]
        cplex_reader = ReadCplex()
        actual = cplex_reader.convert_df([data], variable, 2015, 2070)
        pd.testing.assert_frame_equal(actual, expected, check_index_type=False)

    def test_convert_lines_to_df_empty(self):

        data = [
            [
                "AnnualFixedOperatingCost",
                "REGION",
                "AOBACKSTOP",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
                "0",
            ]
        ]
        variable = "AnnualFixedOperatingCost"
        cplex_reader = ReadCplex()
        actual = cplex_reader.convert_df(data, variable, 2015, 2023)
        pd.testing.assert_frame_equal(
            actual,
            pd.DataFrame(
                data=[],
                columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
            )
            .astype({"REGION": str, "TECHNOLOGY": str, "YEAR": int, "VALUE": float})
            .set_index(["REGION", "TECHNOLOGY", "YEAR"]),
            check_index_type=False,
        )

    def test_check_datatypes_with_empty(self):

        df = pd.DataFrame(data=[], columns=["REGION", "FUEL", "YEAR", "VALUE"])

        parameter = "AccumulatedAnnualDemand"

        config_dict = {
            "AccumulatedAnnualDemand": {
                "indices": ["REGION", "FUEL", "YEAR"],
                "type": "param",
                "dtype": float,
                "default": 0,
            },
            "REGION": {"dtype": "str", "type": "set"},
            "FUEL": {"dtype": "str", "type": "set"},
            "YEAR": {"dtype": "int", "type": "set"},
        }

        actual = check_datatypes(df, config_dict, parameter)

        expected = pd.DataFrame(
            data=[], columns=["REGION", "FUEL", "YEAR", "VALUE"]
        ).astype({"REGION": str, "FUEL": str, "YEAR": int, "VALUE": float})

        pd.testing.assert_frame_equal(actual, expected, check_index_type=False)


class TestReadGurobi:

    gurobi_data = dedent(
        """# Solution for model cost
# Objective value = 4.4973196701520455e+03
TotalDiscountedCost(SIMPLICITY,2013) 0
TotalDiscountedCost(SIMPLICITY,2014) 1.9360385416218188e+02
TotalDiscountedCost(SIMPLICITY,2015) 1.8772386050936669e+02
TotalDiscountedCost(SIMPLICITY,2016) 1.8399762956864294e+02
TotalDiscountedCost(SIMPLICITY,2017) 1.8172752298186381e+02
RateOfActivity(SIMPLICITY,ID,FEL1,1,2014) 1.59376124775045
RateOfActivity(SIMPLICITY,ID,FEL1,1,2015) 1.60167966406719
RateOfActivity(SIMPLICITY,ID,FEL1,1,2016) 1.6369526094781
RateOfActivity(SIMPLICITY,ID,FEL1,1,2017) 1.68590281943611
"""
    )

    def test_convert_to_dataframe(self):
        input_file = self.gurobi_data
        reader = ReadGurobi()
        with StringIO(input_file) as file_buffer:
            actual = reader._convert_to_dataframe(file_buffer)
        print(actual)
        expected = pd.DataFrame(
            [
                ["TotalDiscountedCost", "SIMPLICITY,2014", 1.9360385416218188e02],
                ["TotalDiscountedCost", "SIMPLICITY,2015", 1.8772386050936669e02],
                ["TotalDiscountedCost", "SIMPLICITY,2016", 1.8399762956864294e02],
                ["TotalDiscountedCost", "SIMPLICITY,2017", 1.8172752298186381e02],
                ["RateOfActivity", "SIMPLICITY,ID,FEL1,1,2014", 1.59376124775045],
                ["RateOfActivity", "SIMPLICITY,ID,FEL1,1,2015", 1.60167966406719],
                ["RateOfActivity", "SIMPLICITY,ID,FEL1,1,2016", 1.6369526094781],
                ["RateOfActivity", "SIMPLICITY,ID,FEL1,1,2017", 1.68590281943611],
            ],
            columns=["Variable", "Index", "Value"],
        ).astype({"Variable": str, "Index": str, "Value": float})

        pd.testing.assert_frame_equal(actual, expected)

    def test_solution_to_dataframe(self):
        input_file = self.gurobi_data
        reader = ReadGurobi()
        with StringIO(input_file) as file_buffer:
            actual = reader.read(file_buffer)
        print(actual)
        expected = (
            pd.DataFrame(
                [
                    ["SIMPLICITY", 2014, 1.9360385416218188e02],
                    ["SIMPLICITY", 2015, 1.8772386050936669e02],
                    ["SIMPLICITY", 2016, 1.8399762956864294e02],
                    ["SIMPLICITY", 2017, 1.8172752298186381e02],
                ],
                columns=["REGION", "YEAR", "VALUE"],
            )
            .astype({"YEAR": int, "VALUE": float})
            .set_index(["REGION", "YEAR"])
        )

        pd.testing.assert_frame_equal(actual[0]["TotalDiscountedCost"], expected)

        expected = (
            pd.DataFrame(
                [
                    ["SIMPLICITY", "ID", "FEL1", 1, 2014, 1.59376124775045],
                    ["SIMPLICITY", "ID", "FEL1", 1, 2015, 1.60167966406719],
                    ["SIMPLICITY", "ID", "FEL1", 1, 2016, 1.6369526094781],
                    ["SIMPLICITY", "ID", "FEL1", 1, 2017, 1.68590281943611],
                ],
                columns=[
                    "REGION",
                    "TIMESLICE",
                    "TECHNOLOGY",
                    "MODE_OF_OPERATION",
                    "YEAR",
                    "VALUE",
                ],
            )
            .astype({"YEAR": int, "VALUE": float, "MODE_OF_OPERATION": int})
            .set_index(
                ["REGION", "TIMESLICE", "TECHNOLOGY", "MODE_OF_OPERATION", "YEAR"]
            )
        )
        pd.testing.assert_frame_equal(actual[0]["RateOfActivity"], expected)


class TestReadCbc:

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

    test_data = [
        (
            cbc_data,
            otoole_data,
        )
    ]

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
        actual = ReadCbc()._convert_wide_to_long(prelim_data)["Trade"]
        pd.testing.assert_frame_equal(actual, self.otoole_data)

    test_data_4 = [
        (["REGION", "REGION", "TIMESLICE", "FUEL", "YEAR"], True),
        (["REGION", "TIMESLICE", "FUEL", "YEAR"], False),
        ([], False),
    ]

    @mark.parametrize("data,expected", test_data_4)
    def test_handle_duplicate_indices(self, data, expected):
        assert check_for_duplicates(data) is expected

    test_data_5 = [
        (["REGION", "REGION", "TIMESLICE", "FUEL", "YEAR"], 1),
        (["REGION", "TIMESLICE", "FUEL", "YEAR"], False),
        ([], False),
    ]

    @mark.parametrize("data,expected", test_data_5)
    def test_identify_duplicate(self, data, expected):
        assert identify_duplicate(data) == expected

    def test_rename_duplicate_column(self):
        data = ["REGION", "REGION", "TIMESLICE", "FUEL", "YEAR"]
        actual = rename_duplicate_column(data)
        expected = ["REGION", "_REGION", "TIMESLICE", "FUEL", "YEAR"]
        assert actual == expected

    total_cost_cbc = dedent(
        """Optimal - objective value 4483.96932237
                             1 TotalDiscountedCost(SIMPLICITY,2015){0}187.01576{1}0
                             2 TotalDiscountedCost(SIMPLICITY,2016){0}183.30788{1}0
                             3 TotalDiscountedCost(SIMPLICITY,2017){0}181.05465{1}0
                             4 TotalDiscountedCost(SIMPLICITY,2018){0}218.08923{1}0
                             5 TotalDiscountedCost(SIMPLICITY,2019){0}193.85792{1}0
                             6 TotalDiscountedCost(SIMPLICITY,2020){0}233.79202{1}0

                         """.format(
            " " * 51, " " * 23
        )
    )

    total_cost_cbc_mid = pd.DataFrame(
        data=[
            ["TotalDiscountedCost", "SIMPLICITY,2015", 187.01576],
            ["TotalDiscountedCost", "SIMPLICITY,2016", 183.30788],
            ["TotalDiscountedCost", "SIMPLICITY,2017", 181.05465],
            ["TotalDiscountedCost", "SIMPLICITY,2018", 218.08923],
            ["TotalDiscountedCost", "SIMPLICITY,2019", 193.85792],
            ["TotalDiscountedCost", "SIMPLICITY,2020", 233.79202],
        ],
        columns=["Variable", "Index", "Value"],
    )

    total_cost_otoole_df = {
        "TotalDiscountedCost": pd.DataFrame(
            data=[
                ["SIMPLICITY", 2015, 187.01576],
                ["SIMPLICITY", 2016, 183.30788],
                ["SIMPLICITY", 2017, 181.05465],
                ["SIMPLICITY", 2018, 218.08923],
                ["SIMPLICITY", 2019, 193.85792],
                ["SIMPLICITY", 2020, 233.79202],
            ],
            columns=["REGION", "YEAR", "VALUE"],
        ).set_index(["REGION", "YEAR"])
    }

    test_data = [(total_cost_cbc, total_cost_cbc_mid)]

    @mark.parametrize("cbc_input,expected", test_data, ids=["TotalDiscountedCost"])
    def test_read_cbc_to_dataframe(self, cbc_input, expected):
        cbc_reader = ReadCbc()
        with StringIO(cbc_input) as file_buffer:
            actual = cbc_reader._convert_to_dataframe(file_buffer)
        pd.testing.assert_frame_equal(actual, expected)

    test_data_2 = [
        # First case
        (total_cost_cbc_mid, total_cost_otoole_df),
        # Second case
        (
            pd.DataFrame(
                data=[
                    ["AnnualEmissions", "REGION,CO2,2017", 137958.8400384134],
                    ["AnnualEmissions", "REGION,CO2,2018", 305945.3841061913],
                    ["AnnualEmissions", "REGION,CO2,2019", 626159.9611543404],
                ],
                columns=["Variable", "Index", "Value"],
            ),
            {
                "AnnualEmissions": pd.DataFrame(
                    data=[
                        ["REGION", "CO2", 2017, 137958.8400384134],
                        ["REGION", "CO2", 2018, 305945.3841061913],
                        ["REGION", "CO2", 2019, 626159.9611543404],
                    ],
                    columns=["REGION", "EMISSION", "YEAR", "VALUE"],
                ).set_index(["REGION", "EMISSION", "YEAR"])
            },
        ),
    ]  # type: List

    @mark.parametrize(
        "results,expected",
        test_data_2,
        ids=["TotalDiscountedCost", "AnnualEmissions1"],
    )
    def test_convert_cbc_to_csv_long(self, results, expected):
        cbc_reader = ReadCbc()
        actual = cbc_reader._convert_wide_to_long(results)
        assert isinstance(actual, dict)
        for name, df in actual.items():
            pd.testing.assert_frame_equal(df, expected[name])

    test_data_3 = [(total_cost_cbc, {}, total_cost_otoole_df)]  # type: List

    @mark.parametrize(
        "cbc_solution,input_data,expected",
        test_data_3,
        ids=["TotalDiscountedCost"],
    )
    def test_convert_cbc_to_csv_long_read(self, cbc_solution, input_data, expected):
        cbc_reader = ReadCbc()
        with StringIO(cbc_solution) as file_buffer:
            actual = cbc_reader.read(file_buffer, kwargs={"input_data": input_data})[0][
                "TotalDiscountedCost"
            ]
        assert isinstance(actual, pd.DataFrame)
        pd.testing.assert_frame_equal(actual, expected["TotalDiscountedCost"])

    def test_calculate_results(self):
        cbc_results = {
            "RateOfActivity": pd.DataFrame(
                data=[
                    ["SIMPLICITY", "GAS_EXTRACTION", "ID", 1, 2014, 1],
                    ["SIMPLICITY", "GAS_EXTRACTION", "IN", 1, 2014, 1],
                    ["SIMPLICITY", "GAS_EXTRACTION", "SD", 1, 2014, 1],
                    ["SIMPLICITY", "GAS_EXTRACTION", "SN", 1, 2014, 1],
                    ["SIMPLICITY", "GAS_EXTRACTION", "WD", 1, 2014, 1],
                    ["SIMPLICITY", "GAS_EXTRACTION", "WN", 1, 2014, 1],
                    ["SIMPLICITY", "DUMMY", "ID", 1, 2014, 1],
                    ["SIMPLICITY", "DUMMY", "IN", 1, 2014, 1],
                    ["SIMPLICITY", "DUMMY", "SD", 1, 2014, 1],
                    ["SIMPLICITY", "DUMMY", "SN", 1, 2014, 1],
                    ["SIMPLICITY", "DUMMY", "WD", 1, 2014, 1],
                    ["SIMPLICITY", "DUMMY", "WN", 1, 2014, 1],
                ],
                columns=[
                    "REGION",
                    "TECHNOLOGY",
                    "TIMESLICE",
                    "MODE_OF_OPERATION",
                    "YEAR",
                    "VALUE",
                ],
            ).set_index(
                ["REGION", "TECHNOLOGY", "TIMESLICE", "MODE_OF_OPERATION", "YEAR"]
            )
        }
        input_data = {
            "EmissionActivityRatio": pd.DataFrame(
                data=[["SIMPLICITY", "GAS_EXTRACTION", "CO2", 1, 2014, 1.0]],
                columns=[
                    "REGION",
                    "TECHNOLOGY",
                    "EMISSION",
                    "MODE_OF_OPERATION",
                    "YEAR",
                    "VALUE",
                ],
            ).set_index(
                ["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"]
            ),
            "YearSplit": pd.DataFrame(
                data=[
                    ["ID", 2014, 0.1667],
                    ["IN", 2014, 0.0833],
                    ["SD", 2014, 0.1667],
                    ["SN", 2014, 0.0833],
                    ["WD", 2014, 0.3333],
                    ["WN", 2014, 0.1667],
                ],
                columns=["TIMESLICE", "YEAR", "VALUE"],
            ).set_index(["TIMESLICE", "YEAR"]),
        }

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "CO2", 2014, 1.0]],
            columns=["REGION", "EMISSION", "YEAR", "VALUE"],
        ).set_index(["REGION", "EMISSION", "YEAR"])

        cbc_reader = ReadCbc()
        actual = cbc_reader.calculate_results(cbc_results, input_data)
        assert isinstance(actual, dict)
        pd.testing.assert_frame_equal(actual["AnnualEmissions"], expected)

    def test_solution_to_dataframe(self):
        input_file = self.total_cost_cbc
        reader = ReadCbc()
        with StringIO(input_file) as file_buffer:
            actual = reader.read(file_buffer)
        expected = self.total_cost_otoole_df
        pd.testing.assert_frame_equal(
            actual[0]["TotalDiscountedCost"], expected["TotalDiscountedCost"]
        )

    cbc_infeasible = dedent(
        """header
381191 RateOfActivity(GLOBAL,S4D24,INRNGIM00,1,2041)                           0             0
381191 RateOfActivity(GLOBAL,S4D24,INRNGIM00,1,2042)                           -7.7011981e-07             0.024001857
381192 RateOfActivity(GLOBAL,S1D1,INRNGIM00,1,2043)                            -3.6128354e-06             0.022858911
381199 RateOfActivity(GLOBAL,S1D8,INRNGIM00,1,2043)                            -3.1111316e-06             0.022858911
381200 RateOfActivity(GLOBAL,S1D9,INRNGIM00,1,2043)                            -8.2325306e-07             0.022858911
381201 RateOfActivity(GLOBAL,S1D10,INRNGIM00,1,2043)                           -3.1112991e-06             0.022858911
**  381218 RateOfActivity(GLOBAL,S2D3,INRNGIM00,1,2043)                            -1.6357402e-06             0.022858911
**  381221 RateOfActivity(GLOBAL,S2D6,INRNGIM00,1,2043)                            -3.1111969e-06             0.022858911
**  381229 RateOfActivity(GLOBAL,S2D14,INRNGIM00,1,2043)                           -1.3925924e-07             0.010964295
"""
    )

    def test_manage_infeasible_variables(self):
        input_file = self.cbc_infeasible
        reader = ReadCbc()
        with StringIO(input_file) as file_buffer:
            actual = reader._convert_to_dataframe(file_buffer)
        expected = pd.DataFrame(
            [
                ["RateOfActivity", "GLOBAL,S4D24,INRNGIM00,1,2041", 0],
                ["RateOfActivity", "GLOBAL,S4D24,INRNGIM00,1,2042", -7.7011981e-07],
                ["RateOfActivity", "GLOBAL,S1D1,INRNGIM00,1,2043", -3.6128354e-06],
                ["RateOfActivity", "GLOBAL,S1D8,INRNGIM00,1,2043", -3.1111316e-06],
                ["RateOfActivity", "GLOBAL,S1D9,INRNGIM00,1,2043", -8.2325306e-07],
                ["RateOfActivity", "GLOBAL,S1D10,INRNGIM00,1,2043", -3.1112991e-06],
                ["RateOfActivity", "GLOBAL,S2D3,INRNGIM00,1,2043", -1.6357402e-06],
                ["RateOfActivity", "GLOBAL,S2D6,INRNGIM00,1,2043", -3.1111969e-06],
                ["RateOfActivity", "GLOBAL,S2D14,INRNGIM00,1,2043", -1.3925924e-07],
            ],
            columns=["Variable", "Index", "Value"],
        )
        pd.testing.assert_frame_equal(actual, expected)


class TestCleanOnRead:
    """Tests that a datapackage is cleaned and indexed upon reading"""

    def test_index_dtypes_available(self):
        reader = ReadMemory({})
        config = reader._input_config
        assert "index_dtypes" in config["AccumulatedAnnualDemand"].keys()
        actual = config["AccumulatedAnnualDemand"]["index_dtypes"]
        assert actual == {
            "REGION": "str",
            "FUEL": "str",
            "YEAR": "int",
            "VALUE": "float",
        }

    def test_remove_empty_lines(self):

        data = [
            ["SIMPLICITY", "ETH", 2014, 1.0],
            [],
            ["SIMPLICITY", "ETH", 2015, 1.03],
            [],
        ]
        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"])
        parameters = {"AccumulatedAnnualDemand": df}

        reader = ReadMemory(parameters)
        actual, _ = reader.read()

        expected = {
            "AccumulatedAnnualDemand": pd.DataFrame(
                data=[
                    ["SIMPLICITY", "ETH", 2014, 1.0],
                    ["SIMPLICITY", "ETH", 2015, 1.03],
                ],
                columns=["REGION", "FUEL", "YEAR", "VALUE"],
            )
            .astype({"REGION": str, "FUEL": str, "YEAR": int, "VALUE": float})
            .set_index(["REGION", "FUEL", "YEAR"])
        }

        assert "AccumulatedAnnualDemand" in actual.keys()
        pd.testing.assert_frame_equal(
            actual["AccumulatedAnnualDemand"], expected["AccumulatedAnnualDemand"]
        )

    def test_change_types(self):

        data = [
            ["SIMPLICITY", "ETH", 2014.0, 1],
            ["SIMPLICITY", "ETH", 2015.0, 1],
        ]
        df = pd.DataFrame(
            data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"]
        ).astype({"REGION": str, "FUEL": str, "YEAR": float, "VALUE": int})
        parameters = {"AccumulatedAnnualDemand": df}

        reader = ReadMemory(parameters)
        actual, _ = reader.read()

        expected = {
            "AccumulatedAnnualDemand": pd.DataFrame(
                data=[
                    ["SIMPLICITY", "ETH", 2014, 1.0],
                    ["SIMPLICITY", "ETH", 2015, 1.0],
                ],
                columns=["REGION", "FUEL", "YEAR", "VALUE"],
            )
            .astype({"REGION": str, "FUEL": str, "YEAR": int, "VALUE": float})
            .set_index(["REGION", "FUEL", "YEAR"])
        }

        assert "AccumulatedAnnualDemand" in actual.keys()
        pd.testing.assert_frame_equal(
            actual["AccumulatedAnnualDemand"], expected["AccumulatedAnnualDemand"]
        )


class TestReadMemoryStrategy:
    def test_read_memory(self):

        data = [
            ["SIMPLICITY", "ETH", 2014, 1.0],
            ["SIMPLICITY", "RAWSUG", 2014, 0.5],
            ["SIMPLICITY", "ETH", 2015, 1.03],
            ["SIMPLICITY", "RAWSUG", 2015, 0.51],
        ]
        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"])
        parameters = {"AccumulatedAnnualDemand": df}

        actual, default_values = ReadMemory(parameters).read()

        expected = {
            "AccumulatedAnnualDemand": pd.DataFrame(
                data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"]
            ).set_index(["REGION", "FUEL", "YEAR"])
        }

        assert "AccumulatedAnnualDemand" in actual.keys()
        pd.testing.assert_frame_equal(
            actual["AccumulatedAnnualDemand"], expected["AccumulatedAnnualDemand"]
        )


class TestConfig:
    def test_read_config(self):

        read = ReadDatafile()

        actual = read._read_config()
        expected = {
            "default": 0,
            "dtype": "float",
            "indices": ["REGION", "FUEL", "YEAR"],
            "type": "param",
        }
        assert actual["AccumulatedAnnualDemand"] == expected


class TestReadDatafile:
    def test_amply(self):

        Amply(
            """set REGION;
            # set REGION := SIMPLICITY;
            set TECHNOLOGY;
            set TECHNOLOGY := ETHPLANT GAS_EXTRACTION;
            set MODE_OF_OPERATION;
            set MODE_OF_OPERATION := 1 2;
            set YEAR;
            set YEAR := 2014;
            end;"""
        )

    def test_convert_amply_to_dataframe(self):

        config = {
            "VariableCost": {
                "type": "param",
                "indices": ["REGION", "TECHNOLOGY", "MODE_OF_OPERATION", "YEAR"],
                "dtype": "float",
                "default": 0,
            },
            "REGION": {"type": "set", "dtype": "str"},
            "YEAR": {"dtype": "int", "type": "set"},
            "MODE_OF_OPERATION": {"dtype": "int", "type": "set"},
            "TECHNOLOGY": {"dtype": "str", "type": "set"},
        }

        amply = Amply(
            """set REGION;
                        set REGION := SIMPLICITY;
                        set TECHNOLOGY;
                        set TECHNOLOGY := ETHPLANT GAS_EXTRACTION;
                        set MODE_OF_OPERATION;
                        set MODE_OF_OPERATION := 1 2;
                        set YEAR;
                        set YEAR := 2014;"""
        )
        amply.load_string(
            "param VariableCost {REGION,TECHNOLOGY,MODE_OF_OPERATION,YEAR};"
        )
        #     amply.load_string("""param default 0 : VariableCost :=
        # SIMPLICITY ETHPLANT 1 2014 2.89
        # SIMPLICITY ETHPLANT 2 2014 999999.0
        # SIMPLICITY GAS_EXTRACTION 1 2014 7.5
        # SIMPLICITY GAS_EXTRACTION 2 2014 999999.0""")
        amply.load_string(
            """
    param VariableCost default 0.0001 :=
    [SIMPLICITY,ETHPLANT,*,*]:
    2014 :=
    1 2.89
    2 999999.0
    [SIMPLICITY,GAS_EXTRACTION,*,*]:
    2014 :=
    1 7.5
    2 999999.0;"""
        )

        read = ReadDatafile()

        actual = read._convert_amply_to_dataframe(amply, config)
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "ETHPLANT", 1, 2014, 2.89],
                ["SIMPLICITY", "ETHPLANT", 2, 2014, 999999.0],
                ["SIMPLICITY", "GAS_EXTRACTION", 1, 2014, 7.5],
                ["SIMPLICITY", "GAS_EXTRACTION", 2, 2014, 999999.0],
            ],
            columns=["REGION", "TECHNOLOGY", "MODE_OF_OPERATION", "YEAR", "VALUE"],
        )
        pd.testing.assert_frame_equal(actual["VariableCost"], expected)

    def test_convert_amply_data_to_list_of_lists(self):

        data = {
            "SIMPLICITY": {
                "ETHPLANT": {1.0: {2014.0: 2.89}, 2.0: {2014.0: 999999.0}},
                "GAS_EXTRACTION": {1.0: {2014.0: 7.5}, 2.0: {2014.0: 999999.0}},
            }
        }
        expected = [
            ["SIMPLICITY", "ETHPLANT", 1.0, 2014.0, 2.89],
            ["SIMPLICITY", "ETHPLANT", 2.0, 2014.0, 999999.0],
            ["SIMPLICITY", "GAS_EXTRACTION", 1.0, 2014.0, 7.5],
            ["SIMPLICITY", "GAS_EXTRACTION", 2.0, 2014.0, 999999.0],
        ]
        read = ReadDatafile()
        actual = read._convert_amply_data_to_list(data)
        assert actual == expected

    def test_load_parameters(self):

        config = {"TestParameter": {"type": "param", "indices": ["index1", "index2"]}}
        read = ReadDatafile()
        actual = read._load_parameter_definitions(config)
        expected = "param TestParameter {index1,index2};\n"
        assert actual == expected

    def test_load_sets(self):

        config = {"TestSet": {"type": "set"}}

        read = ReadDatafile()
        actual = read._load_parameter_definitions(config)
        expected = "set TestSet;\n"
        assert actual == expected

    def test_catch_error_no_parameter(self, caplog):
        """Fix for https://github.com/OSeMOSYS/otoole/issues/70 where parameter in
        datafile but not in config causes error.  Instead, throw warning (and advise
        that user should use a custom configuration).
        """
        read = ReadDatafile()
        config = read.input_config
        amply_datafile = amply = Amply(
            """set REGION;
            set TECHNOLOGY;
            set MODE_OF_OPERATION;
            set YEAR;"""
        )
        amply.load_string("""param ResultsPath := 'test_path';""")
        read._convert_amply_to_dataframe(amply_datafile, config)
        assert (
            "Parameter ResultsPath could not be found in the configuration."
            in caplog.text
        )


class TestReadExcel:
    def test_read_excel_yearsplit(self):
        """ """
        spreadsheet = os.path.join("tests", "fixtures", "combined_inputs.xlsx")
        reader = ReadExcel()
        actual, _ = reader.read(spreadsheet)
        data = [
            ["IW0016", 2017, 0.238356164],
            ["IW0016", 2018, 0.238356164],
            ["IW0016", 2019, 0.238356164],
            ["IW1624", 2017, 0.119178082],
            ["IW1624", 2018, 0.119178082],
            ["IW1624", 2019, 0.119178082],
            ["IH0012", 2017, 0.071232876],
            ["IH0012", 2018, 0.071232876],
            ["IH0012", 2019, 0.071232876],
        ]
        expected = pd.DataFrame(data, columns=["TIMESLICE", "YEAR", "VALUE"]).set_index(
            ["TIMESLICE", "YEAR"]
        )

        assert "YearSplit" in actual

        index = [
            ("IW0016", 2017),
            ("IW0016", 2018),
            ("IW0016", 2019),
            ("IW1624", 2017),
            ("IW1624", 2018),
            ("IW1624", 2019),
            ("IH0012", 2017),
            ("IH0012", 2018),
            ("IH0012", 2019),
        ]

        assert actual["YearSplit"].index.names == ["TIMESLICE", "YEAR"]
        actual_data = actual["YearSplit"].loc[index, "VALUE"]

        expected = [
            0.238356164,
            0.238356164,
            0.238356164,
            0.119178082,
            0.119178082,
            0.119178082,
            0.071232876,
            0.071232876,
            0.071232876,
        ]

        assert (actual_data == expected).all()

    def test_narrow_parameters(self):
        data = [
            ["IW0016", 0.238356164, 0.238356164, 0.238356164],
            ["IW1624", 0.119178082, 0.119178082, 0.119178082],
            ["IH0012", 0.071232876, 0.071232876, 0.071232876],
        ]
        df = pd.DataFrame(data, columns=["TIMESLICE", 2017, 2018, 2019])
        config_details = ["TIMESLICE", "YEAR"]
        name = "YearSplit"

        reader = ReadExcel()
        actual = reader._check_parameter(df, config_details, name)
        data = [
            ["IW0016", 2017, 0.238356164],
            ["IW1624", 2017, 0.119178082],
            ["IH0012", 2017, 0.071232876],
            ["IW0016", 2018, 0.238356164],
            ["IW1624", 2018, 0.119178082],
            ["IH0012", 2018, 0.071232876],
            ["IW0016", 2019, 0.238356164],
            ["IW1624", 2019, 0.119178082],
            ["IH0012", 2019, 0.071232876],
        ]
        expected = (
            pd.DataFrame(data, columns=["TIMESLICE", "YEAR", "VALUE"])
            .astype({"YEAR": "object"})
            .set_index(["TIMESLICE", "YEAR"])
        )
        pd.testing.assert_frame_equal(actual, expected)

    def test_check_index(self):

        data = [
            ["IW0016", 2017, 0.238356164],
            ["IW0016", 2018, 0.238356164],
            ["IW0016", 2019, 0.238356164],
            ["IW1624", 2017, 0.119178082],
            ["IW1624", 2018, 0.119178082],
            ["IW1624", 2019, 0.119178082],
            ["IH0012", 2017, 0.071232876],
            ["IH0012", 2018, 0.071232876],
            ["IH0012", 2019, 0.071232876],
        ]
        fixture = {
            "YearSplit": pd.DataFrame(data, columns=["TIMESLICE", "YEAR", "VALUE"])
            .astype({"YEAR": object})
            .set_index(["TIMESLICE", "YEAR"])
        }
        reader = ReadExcel()
        actual = reader._check_index(fixture)
        expected = {
            "YearSplit": pd.DataFrame(
                data, columns=["TIMESLICE", "YEAR", "VALUE"]
            ).set_index(["TIMESLICE", "YEAR"])
        }
        pd.testing.assert_frame_equal(actual["YearSplit"], expected["YearSplit"])
