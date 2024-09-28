import os
from io import StringIO
from textwrap import dedent

import pandas as pd
from amply import Amply
from pytest import mark, raises

from otoole.exceptions import OtooleDeprecationError, OtooleError
from otoole.preprocess.longify_data import check_datatypes
from otoole.read_strategies import ReadCsv, ReadDatafile, ReadExcel, ReadMemory
from otoole.results.results import (
    ReadCbc,
    ReadCplex,
    ReadGlpk,
    ReadGurobi,
    ReadHighs,
    ReadResults,
    check_for_duplicates,
    identify_duplicate,
    rename_duplicate_column,
)
from otoole.utils import _read_file


# To instantiate abstract class ReadResults
class DummyReadResults(ReadResults):
    def get_results_from_file(self, filepath, input_data):
        raise NotImplementedError()


class TestReadCplex:

    cplex_data = """<?xml version = "1.0" encoding="UTF-8" standalone="yes"?>
<CPLEXSolution version="1.2">
 <header
   problemName="model.lp"
   objectiveValue="3942.194792652062"
   solutionTypeValue="1"
   solutionTypeString="basic"
   solutionStatusValue="1"
   solutionStatusString="optimal"
   solutionMethodString="dual"
   primalFeasible="1"
   dualFeasible="1"
   simplexIterations="3011"
   writeLevel="1"/>
 <quality
   epRHS="9.9999999999999995e-07"
   epOpt="9.9999999999999995e-07"
   maxPrimalInfeas="1.4210854715202004e-13"
   maxDualInfeas="1.9618827037793883e-12"
   maxPrimalResidual="5.3193968022437806e-12"
   maxDualResidual="5.6354920729972946e-13"
   maxX="1331.0025494901022"
   maxPi="525.09145670749103"
   maxSlack="9998.6832048983561"
   maxRedCost="999999.00000000105"
   kappa="57958.643677766071"/>
 <linearConstraints>
  <constraint name="CAa4_Constraint_Capacity(SIMPLICITY,ID,BACKSTOP1,2014)" index="0" status="BS" slack="-0" dual="0"/>
  <constraint name="CAa4_Constraint_Capacity(SIMPLICITY,ID,BACKSTOP1,2015)" index="1" status="BS" slack="-0" dual="0"/>
  <constraint name="CAa4_Constraint_Capacity(SIMPLICITY,ID,BACKSTOP1,2016)" index="2" status="BS" slack="-0" dual="0"/>
  <constraint name="EBa11_EnergyBalanceEachTS5(SIMPLICITY,IN,DSL,2014)" index="5400" status="LL" slack="0" dual="-2.4281963661332018e-14"/>
  <constraint name="EBa11_EnergyBalanceEachTS5(SIMPLICITY,IN,DSL,2015)" index="5401" status="LL" slack="0" dual="-4.4565525073113654e-15"/>
  <constraint name="EBa11_EnergyBalanceEachTS5(SIMPLICITY,IN,DSL,2016)" index="5402" status="LL" slack="0" dual="7.5386542413397867e-15"/>
  <constraint name="TCC1_TotalAnnualMaxCapacityConstraint(SIMPLICITY,HYD2,2014)" index="11529" status="BS" slack="0.10000000000000001" dual="0"/>
  <constraint name="TCC1_TotalAnnualMaxCapacityConstraint(SIMPLICITY,HYD2,2015)" index="11530" status="BS" slack="0.10000000000000001" dual="0"/>
  <constraint name="TCC1_TotalAnnualMaxCapacityConstraint(SIMPLICITY,HYD2,2016)" index="11531" status="BS" slack="0.10000000000000001" dual="0"/>
 </linearConstraints>
 <variables>
  <variable name="NewCapacity(SIMPLICITY,ETHPLANT,2014)" index="54" status="LL" value="0" reducedCost="9.8033882532023107"/>
  <variable name="NewCapacity(SIMPLICITY,ETHPLANT,2015)" index="55" status="BS" value="0.030000000000000027" reducedCost="0"/>
  <variable name="NewCapacity(SIMPLICITY,ETHPLANT,2016)" index="56" status="BS" value="0.030999999999999917" reducedCost="0"/>
  <variable name="RateOfActivity(SIMPLICITY,ID,GRID_EXP,1,2014)" index="6048" status="LL" value="0" reducedCost="2.5520010388720782"/>
  <variable name="RateOfActivity(SIMPLICITY,ID,GRID_EXP,2,2014)" index="6049" status="LL" value="0" reducedCost="2.5520010388720782"/>
  <variable name="RateOfActivity(SIMPLICITY,ID,HYD1,1,2020)" index="6108" status="BS" value="0.25228800000000001" reducedCost="0"/>
  <variable name="RateOfActivity(SIMPLICITY,ID,HYD1,1,2021)" index="6109" status="BS" value="0.25228800000000001" reducedCost="0"/>
  <variable name="RateOfActivity(SIMPLICITY,ID,HYD1,1,2022)" index="6110" status="BS" value="0.25228800000000001" reducedCost="0"/>
 </variables>
 <objectiveValues>
  <objective index="0" name="cost" value="3942.1947926520666"/>
 </objectiveValues>
</CPLEXSolution>"""

    def test_convert_to_dataframe(self, user_config):
        input_file = self.cplex_data
        reader = ReadCplex(user_config)
        with StringIO(input_file) as file_buffer:
            actual = reader._convert_to_dataframe(file_buffer)
        expected = pd.DataFrame(
            [
                ["NewCapacity", "SIMPLICITY,ETHPLANT,2015", 0.030000000000000027],
                ["NewCapacity", "SIMPLICITY,ETHPLANT,2016", 0.030999999999999917],
                ["RateOfActivity", "SIMPLICITY,ID,HYD1,1,2020", 0.25228800000000001],
                ["RateOfActivity", "SIMPLICITY,ID,HYD1,1,2021", 0.25228800000000001],
                ["RateOfActivity", "SIMPLICITY,ID,HYD1,1,2022", 0.25228800000000001],
            ],
            columns=["Variable", "Index", "Value"],
        ).astype({"Variable": str, "Index": str, "Value": float})

        pd.testing.assert_frame_equal(actual, expected)

    def test_solution_to_dataframe(self, user_config):
        input_file = self.cplex_data
        reader = ReadCplex(user_config)
        with StringIO(input_file) as file_buffer:
            actual = reader.read(file_buffer)
        expected = (
            pd.DataFrame(
                [
                    ["SIMPLICITY", "ETHPLANT", 2015, 0.030000000000000027],
                    ["SIMPLICITY", "ETHPLANT", 2016, 0.030999999999999917],
                ],
                columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
            )
            .astype({"REGION": str, "TECHNOLOGY": str, "YEAR": "int64", "VALUE": float})
            .set_index(["REGION", "TECHNOLOGY", "YEAR"])
        )

        pd.testing.assert_frame_equal(actual[0]["NewCapacity"], expected)

        expected = (
            pd.DataFrame(
                [
                    ["SIMPLICITY", "ID", "HYD1", 1, 2020, 0.25228800000000001],
                    ["SIMPLICITY", "ID", "HYD1", 1, 2021, 0.25228800000000001],
                    ["SIMPLICITY", "ID", "HYD1", 1, 2022, 0.25228800000000001],
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
            .astype(
                {
                    "REGION": str,
                    "TIMESLICE": str,
                    "TECHNOLOGY": str,
                    "MODE_OF_OPERATION": "int64",
                    "YEAR": "int64",
                    "VALUE": float,
                }
            )
            .set_index(
                ["REGION", "TIMESLICE", "TECHNOLOGY", "MODE_OF_OPERATION", "YEAR"]
            )
        )
        pd.testing.assert_frame_equal(actual[0]["RateOfActivity"], expected)

    def test_solution_to_dataframe_with_defaults(self, user_config):
        input_file = self.cplex_data

        regions = pd.DataFrame(data=["SIMPLICITY"], columns=["VALUE"])
        technologies = pd.DataFrame(data=["ETHPLANT"], columns=["VALUE"])
        years = pd.DataFrame(data=[2014, 2015, 2016], columns=["VALUE"])
        input_data = {"REGION": regions, "TECHNOLOGY": technologies, "YEAR": years}

        reader = ReadCplex(user_config, write_defaults=True)
        with StringIO(input_file) as file_buffer:
            actual = reader.read(file_buffer, input_data=input_data)
        expected = (
            pd.DataFrame(
                [
                    ["SIMPLICITY", "ETHPLANT", 2014, 0],
                    ["SIMPLICITY", "ETHPLANT", 2015, 0.030000000000000027],
                    ["SIMPLICITY", "ETHPLANT", 2016, 0.030999999999999917],
                ],
                columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
            )
            .astype({"REGION": str, "TECHNOLOGY": str, "YEAR": "int64", "VALUE": float})
            .set_index(["REGION", "TECHNOLOGY", "YEAR"])
        )

        pd.testing.assert_frame_equal(actual[0]["NewCapacity"], expected)


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

    def test_convert_to_dataframe(self, user_config):
        input_file = self.gurobi_data
        reader = ReadGurobi(user_config)
        with StringIO(input_file) as file_buffer:
            actual = reader._convert_to_dataframe(file_buffer)
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

    def test_solution_to_dataframe(self, user_config):
        input_file = self.gurobi_data
        reader = ReadGurobi(user_config)
        with StringIO(input_file) as file_buffer:
            actual = reader.read(file_buffer)
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
            .astype({"YEAR": "int64", "VALUE": float})
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
            .astype({"YEAR": "int64", "VALUE": float, "MODE_OF_OPERATION": "int64"})
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
    def test_read_cbc_to_otoole_dataframe(self, cbc_input, expected, user_config):
        with StringIO(cbc_input) as file_buffer:
            actual = ReadCbc(user_config).read(file_buffer, kwargs={"input_data": {}})[
                0
            ]["Trade"]
        pd.testing.assert_frame_equal(actual, expected)

    def test_read_cbc_dataframe_to_otoole_dataframe(self, user_config):

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
        actual = ReadCbc(user_config)._convert_wide_to_long(prelim_data)["Trade"]
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
    def test_read_cbc_to_dataframe(self, cbc_input, expected, user_config):
        cbc_reader = ReadCbc(user_config)
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
    ]  # type: list

    @mark.parametrize(
        "results,expected",
        test_data_2,
        ids=["TotalDiscountedCost", "AnnualEmissions1"],
    )
    def test_convert_cbc_to_csv_long(self, results, expected, user_config):
        cbc_reader = ReadCbc(user_config=user_config)
        actual = cbc_reader._convert_wide_to_long(results)
        assert isinstance(actual, dict)
        for name, df in actual.items():
            pd.testing.assert_frame_equal(df, expected[name])

    test_data_3 = [(total_cost_cbc, {}, total_cost_otoole_df)]  # type: list

    @mark.parametrize(
        "cbc_solution,input_data,expected",
        test_data_3,
        ids=["TotalDiscountedCost"],
    )
    def test_convert_cbc_to_csv_long_read(
        self, cbc_solution, input_data, expected, user_config
    ):
        cbc_reader = ReadCbc(user_config=user_config)
        with StringIO(cbc_solution) as file_buffer:
            actual = cbc_reader.read(file_buffer, kwargs={"input_data": input_data})[0][
                "TotalDiscountedCost"
            ]
        assert isinstance(actual, pd.DataFrame)
        pd.testing.assert_frame_equal(actual, expected["TotalDiscountedCost"])

    def test_calculate_results(self, user_config):
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

        cbc_reader = ReadCbc(user_config)
        actual = cbc_reader.calculate_results(cbc_results, input_data)
        assert isinstance(actual, dict)
        pd.testing.assert_frame_equal(actual["AnnualEmissions"], expected)

    def test_solution_to_dataframe(self, user_config):
        input_file = self.total_cost_cbc
        reader = ReadCbc(user_config)
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

    def test_manage_infeasible_variables(self, user_config):
        input_file = self.cbc_infeasible
        reader = ReadCbc(user_config)
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


class TestReadGlpk:
    """Use fixtures instead of StringIO due to the use of context managers in the logic"""

    model_data = dedent(
        """p lp min 12665 9450 82606
n p osemosys_fast
n z cost
i 1 f
n i 1 cost
i 2 u -0
n i 2 CAa4_Constraint_Capacity[SIMPLICITY,ID,BACKSTOP1,2014]
i 3 u -0
n i 3 CAa4_Constraint_Capacity[SIMPLICITY,ID,BACKSTOP1,2015]
i 300 u 147.115
n i 300 CAa4_Constraint_Capacity[SIMPLICITY,ID,LNDFORCOV,2015]
i 301 u 144.231
n i 301 CAa4_Constraint_Capacity[SIMPLICITY,ID,LNDFORCOV,2016]
n j 1 SalvageValueStorage[SIMPLICITY,DAM,2014]
n j 2 SalvageValueStorage[SIMPLICITY,DAM,2015]
n j 130 StorageLevelSeasonStart[SIMPLICITY,DAM,2,2035]
n j 131 StorageLevelSeasonStart[SIMPLICITY,DAM,2,2036]
n j 1025 NewCapacity[SIMPLICITY,WINDPOWER,2039]
n j 1026 NewCapacity[SIMPLICITY,WINDPOWER,2040]
n j 1027 RateOfActivity[SIMPLICITY,ID,BACKSTOP1,1,2014]
n j 1028 RateOfActivity[SIMPLICITY,IN,BACKSTOP1,1,2014]
"""
    )

    sol_data = dedent(
        """c Problem:    osemosys_fast
c Rows:       12665
c Columns:    9450
c Non-zeros:  82606
c Status:     OPTIMAL
c Objective:  cost = 4497.31967 (MINimum)
c
s bas 12665 9450 f f 4497.31967015205
i 1 b 3942.19479265207 0
i 2 b 0 0
i 3 b 0 0
i 300 b 37.499 0
i 301 b 31.7309999999999 0
j 1 b 0 0
j 2 b 0 0
j 130 l 0 0.282765294823514
j 131 l 0 0.601075755990521
j 1025 b 0.0305438002923389 0
j 1026 b 0.0422503416065477 0
j 1027 l 0 162679.693161095
j 1028 l 0 81291.0524314291
e o f
"""
    )

    expected_solution = pd.DataFrame(
        [
            ["i", 1, "b", 3942.19479265207, 0],
            ["i", 2, "b", 0, 0],
            ["i", 3, "b", 0, 0],
            ["i", 300, "b", 37.499, 0],
            ["i", 301, "b", 31.7309999999999, 0],
            ["j", 1, "b", 0, 0],
            ["j", 2, "b", 0, 0],
            ["j", 130, "l", 0, 0.282765294823514],
            ["j", 131, "l", 0, 0.601075755990521],
            ["j", 1025, "b", 0.0305438002923389, 0],
            ["j", 1026, "b", 0.0422503416065477, 0],
            ["j", 1027, "l", 0, 162679.693161095],
            ["j", 1028, "l", 0, 81291.0524314291],
        ],
        columns=["ID", "NUM", "STATUS", "PRIM", "DUAL"],
    )

    def test_read_model(self, user_config):
        model_data = self.model_data
        with StringIO(model_data) as file_buffer:
            reader = ReadGlpk(user_config=user_config, glpk_model=file_buffer)
        actual = reader.model

        expected = pd.DataFrame(
            [
                ["i", 2, "CAa4_Constraint_Capacity", "SIMPLICITY,ID,BACKSTOP1,2014"],
                ["i", 3, "CAa4_Constraint_Capacity", "SIMPLICITY,ID,BACKSTOP1,2015"],
                ["i", 300, "CAa4_Constraint_Capacity", "SIMPLICITY,ID,LNDFORCOV,2015"],
                ["i", 301, "CAa4_Constraint_Capacity", "SIMPLICITY,ID,LNDFORCOV,2016"],
                ["j", 1, "SalvageValueStorage", "SIMPLICITY,DAM,2014"],
                ["j", 2, "SalvageValueStorage", "SIMPLICITY,DAM,2015"],
                ["j", 130, "StorageLevelSeasonStart", "SIMPLICITY,DAM,2,2035"],
                ["j", 131, "StorageLevelSeasonStart", "SIMPLICITY,DAM,2,2036"],
                ["j", 1025, "NewCapacity", "SIMPLICITY,WINDPOWER,2039"],
                ["j", 1026, "NewCapacity", "SIMPLICITY,WINDPOWER,2040"],
                ["j", 1027, "RateOfActivity", "SIMPLICITY,ID,BACKSTOP1,1,2014"],
                ["j", 1028, "RateOfActivity", "SIMPLICITY,IN,BACKSTOP1,1,2014"],
            ],
            columns=["ID", "NUM", "NAME", "INDEX"],
        ).astype({"ID": str, "NUM": "int64", "NAME": str, "INDEX": str})

        pd.testing.assert_frame_equal(actual, expected)

    def test_read_solution(self, user_config):
        model_data = self.model_data
        sol_data = self.sol_data
        with StringIO(model_data) as file_buffer:
            reader = ReadGlpk(user_config=user_config, glpk_model=file_buffer)
        with StringIO(sol_data) as file_buffer:
            actual_status, actual_data = reader.read_solution(file_buffer)

        expected_status = {
            "name": "osemosys_fast",
            "status": "OPTIMAL",
            "objective": 4497.31967,
        }
        assert actual_status == expected_status

        pd.testing.assert_frame_equal(actual_data, self.expected_solution)

    def test_merge_model_sol(self, user_config):
        model_data = self.model_data
        with StringIO(model_data) as file_buffer:
            reader = ReadGlpk(user_config=user_config, glpk_model=file_buffer)

        actual = reader._merge_model_sol(self.expected_solution)
        expected = pd.DataFrame(
            [
                ["SalvageValueStorage", "SIMPLICITY,DAM,2014", 0],
                ["SalvageValueStorage", "SIMPLICITY,DAM,2015", 0],
                ["StorageLevelSeasonStart", "SIMPLICITY,DAM,2,2035", 0],
                ["StorageLevelSeasonStart", "SIMPLICITY,DAM,2,2036", 0],
                ["NewCapacity", "SIMPLICITY,WINDPOWER,2039", 0.0305438002923389],
                ["NewCapacity", "SIMPLICITY,WINDPOWER,2040", 0.0422503416065477],
                ["RateOfActivity", "SIMPLICITY,ID,BACKSTOP1,1,2014", 0],
                ["RateOfActivity", "SIMPLICITY,IN,BACKSTOP1,1,2014", 0],
            ],
            columns=["Variable", "Index", "Value"],
        )

        pd.testing.assert_frame_equal(actual, expected)

    def test_convert_to_dataframe(self, user_config):
        model_data = self.model_data
        sol_data = self.sol_data
        with StringIO(model_data) as file_buffer:
            reader = ReadGlpk(user_config=user_config, glpk_model=file_buffer)
        with StringIO(sol_data) as file_buffer:
            reader._convert_to_dataframe(file_buffer)

    def test_convert_to_dataframe_error(self, user_config):
        model_data = self.model_data
        with StringIO(model_data) as file_buffer:
            reader = ReadGlpk(user_config=user_config, glpk_model=file_buffer)

        sol = pd.DataFrame()

        with raises(TypeError):
            reader._convert_to_dataframe(sol)

    def test_read_model_error(self, user_config):
        with raises(TypeError):
            ReadGlpk(user_config)


class TestReadHighs:
    """Tests reading of HiGHS solution file"""

    highs_data_with_type_col = dedent(
        """Columns
    Index Status        Lower        Upper       Primal         Dual  Type        Name
        0     BS            0          inf      193.604            0  Continuous  TotalDiscountedCost(SIMPLICITY,2014)
        1     BS            0          inf      187.724            0  Continuous  TotalDiscountedCost(SIMPLICITY,2015)
        2     BS            0          inf      183.998            0  Continuous  TotalDiscountedCost(SIMPLICITY,2016)
        3     BS            0          inf      181.728            0  Continuous  TotalDiscountedCost(SIMPLICITY,2017)
     2433     LB            0          inf            0       162680  Continuous  RateOfActivity(SIMPLICITY,ID,BACKSTOP1,1,2014)
     2434     LB            0          inf            0       162682  Continuous  RateOfActivity(SIMPLICITY,ID,BACKSTOP1,2,2014)
     2435     BS            0          inf           -0            0  Continuous  RateOfTotalActivity(SIMPLICITY,BACKSTOP1,ID,2014)
     2436     LB            0          inf            0       154933  Continuous  RateOfActivity(SIMPLICITY,ID,BACKSTOP1,1,2015)
     5772     BS            0          inf     0.353203            0  Continuous  RateOfActivity(SIMPLICITY,WN,HYD1,1,2020)
     5773     LB            0          inf            0      2.15221  Continuous  RateOfActivity(SIMPLICITY,WN,HYD1,2,2020)
     5774     BS            0          inf     0.353203            0  Continuous  RateOfTotalActivity(SIMPLICITY,HYD1,WN,2020)
     5775     BS            0          inf     0.353203            0  Continuous  RateOfActivity(SIMPLICITY,WN,HYD1,1,2021)
    15417     BS            0          inf           -0            0  Continuous  RateOfProductionByTechnologyByMode(SIMPLICITY,ID,GAS_IMPORT,1,GAS,2038)
    15418     BS            0          inf           -0            0  Continuous  RateOfProductionByTechnologyByMode(SIMPLICITY,ID,GAS_IMPORT,1,GAS,2039)
    15419     BS            0          inf           -0            0  Continuous  RateOfProductionByTechnologyByMode(SIMPLICITY,ID,GAS_IMPORT,1,GAS,2040)
Rows
    Index Status        Lower        Upper       Primal         Dual  Name
        0     FX     -1.59376     -1.59376     -1.59376     -2.68632  EQ_SpecifiedDemand(SIMPLICITY,ID,FEL1,2014)
        1     FX     -1.60168     -1.60168     -1.60168      -2.5584  EQ_SpecifiedDemand(SIMPLICITY,ID,FEL1,2015)
        2     FX     -1.63695     -1.63695     -1.63695     -2.43657  EQ_SpecifiedDemand(SIMPLICITY,ID,FEL1,2016)
        3     FX      -1.6859      -1.6859      -1.6859     -2.32054  EQ_SpecifiedDemand(SIMPLICITY,ID,FEL1,2017)
        4     FX     -1.74637     -1.74637     -1.74637     -2.21004  EQ_SpecifiedDemand(SIMPLICITY,ID,FEL1,2018)
        5     FX     -1.80612     -1.80612     -1.80612      -2.1048  EQ_SpecifiedDemand(SIMPLICITY,ID,FEL1,2019)

Model status: Optimal

Objective value: 4497.319670152045
"""
    )

    highs_data_no_type_col = dedent(
        """Columns
    Index Status        Lower        Upper       Primal         Dual  Name
        0     BS            0          inf      193.604            0  TotalDiscountedCost(SIMPLICITY,2014)
        1     BS            0          inf      187.724            0  TotalDiscountedCost(SIMPLICITY,2015)
        2     BS            0          inf      183.998            0  TotalDiscountedCost(SIMPLICITY,2016)
        3     BS            0          inf      181.728            0  TotalDiscountedCost(SIMPLICITY,2017)
     2433     LB            0          inf            0       162680  RateOfActivity(SIMPLICITY,ID,BACKSTOP1,1,2014)
     2434     LB            0          inf            0       162682  RateOfActivity(SIMPLICITY,ID,BACKSTOP1,2,2014)
     2435     BS            0          inf           -0            0  RateOfTotalActivity(SIMPLICITY,BACKSTOP1,ID,2014)
     2436     LB            0          inf            0       154933  RateOfActivity(SIMPLICITY,ID,BACKSTOP1,1,2015)
     5772     BS            0          inf     0.353203            0  RateOfActivity(SIMPLICITY,WN,HYD1,1,2020)
     5773     LB            0          inf            0      2.15221  RateOfActivity(SIMPLICITY,WN,HYD1,2,2020)
     5774     BS            0          inf     0.353203            0  RateOfTotalActivity(SIMPLICITY,HYD1,WN,2020)
     5775     BS            0          inf     0.353203            0  RateOfActivity(SIMPLICITY,WN,HYD1,1,2021)
    15417     BS            0          inf           -0            0  RateOfProductionByTechnologyByMode(SIMPLICITY,ID,GAS_IMPORT,1,GAS,2038)
    15418     BS            0          inf           -0            0  RateOfProductionByTechnologyByMode(SIMPLICITY,ID,GAS_IMPORT,1,GAS,2039)
    15419     BS            0          inf           -0            0  RateOfProductionByTechnologyByMode(SIMPLICITY,ID,GAS_IMPORT,1,GAS,2040)
Rows
    Index Status        Lower        Upper       Primal         Dual  Name
        0     FX     -1.59376     -1.59376     -1.59376     -2.68632  EQ_SpecifiedDemand(SIMPLICITY,ID,FEL1,2014)
        1     FX     -1.60168     -1.60168     -1.60168      -2.5584  EQ_SpecifiedDemand(SIMPLICITY,ID,FEL1,2015)
        2     FX     -1.63695     -1.63695     -1.63695     -2.43657  EQ_SpecifiedDemand(SIMPLICITY,ID,FEL1,2016)
        3     FX      -1.6859      -1.6859      -1.6859     -2.32054  EQ_SpecifiedDemand(SIMPLICITY,ID,FEL1,2017)
        4     FX     -1.74637     -1.74637     -1.74637     -2.21004  EQ_SpecifiedDemand(SIMPLICITY,ID,FEL1,2018)
        5     FX     -1.80612     -1.80612     -1.80612      -2.1048  EQ_SpecifiedDemand(SIMPLICITY,ID,FEL1,2019)

Model status: Optimal

Objective value: 4497.319670152045
"""
    )

    test_data = [highs_data_with_type_col, highs_data_no_type_col]

    @mark.parametrize("highs_sol", test_data, ids=["with_type_col", "no_type_col"])
    def test_convert_to_dataframe(self, user_config, highs_sol):
        reader = ReadHighs(user_config)
        with StringIO(highs_sol) as file_buffer:
            actual = reader._convert_to_dataframe(file_buffer)
        expected = pd.DataFrame(
            [
                ["TotalDiscountedCost", "SIMPLICITY,2014", 193.604],
                ["TotalDiscountedCost", "SIMPLICITY,2015", 187.724],
                ["TotalDiscountedCost", "SIMPLICITY,2016", 183.998],
                ["TotalDiscountedCost", "SIMPLICITY,2017", 181.728],
                ["RateOfActivity", "SIMPLICITY,WN,HYD1,1,2020", 0.353203],
                ["RateOfTotalActivity", "SIMPLICITY,HYD1,WN,2020", 0.353203],
                ["RateOfActivity", "SIMPLICITY,WN,HYD1,1,2021", 0.353203],
            ],
            columns=["Variable", "Index", "Value"],
        ).astype({"Variable": str, "Index": str, "Value": float})

        pd.testing.assert_frame_equal(actual, expected)

    def test_solution_to_dataframe(self, user_config):
        input_file = self.highs_data_with_type_col
        reader = ReadHighs(user_config)
        with StringIO(input_file) as file_buffer:
            actual = reader.read(file_buffer)
        # print(actual)
        expected = (
            pd.DataFrame(
                [
                    ["SIMPLICITY", 2014, 193.604],
                    ["SIMPLICITY", 2015, 187.724],
                    ["SIMPLICITY", 2016, 183.998],
                    ["SIMPLICITY", 2017, 181.728],
                ],
                columns=["REGION", "YEAR", "VALUE"],
            )
            .astype({"YEAR": "int64", "VALUE": float})
            .set_index(["REGION", "YEAR"])
        )

        pd.testing.assert_frame_equal(actual[0]["TotalDiscountedCost"], expected)

        expected = (
            pd.DataFrame(
                [
                    ["SIMPLICITY", "WN", "HYD1", 1, 2020, 0.353203],
                    ["SIMPLICITY", "WN", "HYD1", 1, 2021, 0.353203],
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
            .astype({"YEAR": "int64", "VALUE": float, "MODE_OF_OPERATION": "int64"})
            .set_index(
                ["REGION", "TIMESLICE", "TECHNOLOGY", "MODE_OF_OPERATION", "YEAR"]
            )
        )
        pd.testing.assert_frame_equal(actual[0]["RateOfActivity"], expected)


class TestCleanOnRead:
    """Tests that a data is cleaned and indexed upon reading"""

    def test_index_dtypes_available(self, user_config):
        reader = ReadMemory({}, user_config=user_config)
        config = reader.user_config
        assert "index_dtypes" in config["AccumulatedAnnualDemand"].keys()
        actual = config["AccumulatedAnnualDemand"]["index_dtypes"]
        assert actual == {
            "REGION": "str",
            "FUEL": "str",
            "YEAR": "int64",
            "VALUE": "float",
        }

    def test_remove_empty_lines(self, user_config):

        data = [
            ["SIMPLICITY", "ETH", 2014, 1.0],
            [],
            ["SIMPLICITY", "ETH", 2015, 1.03],
            [],
        ]
        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"])
        parameters = {"AccumulatedAnnualDemand": df}

        reader = ReadMemory(parameters, user_config=user_config)
        actual, _ = reader.read()

        expected = {
            "AccumulatedAnnualDemand": pd.DataFrame(
                data=[
                    ["SIMPLICITY", "ETH", 2014, 1.0],
                    ["SIMPLICITY", "ETH", 2015, 1.03],
                ],
                columns=["REGION", "FUEL", "YEAR", "VALUE"],
            )
            .astype({"REGION": str, "FUEL": str, "YEAR": "int64", "VALUE": float})
            .set_index(["REGION", "FUEL", "YEAR"])
        }

        assert "AccumulatedAnnualDemand" in actual.keys()
        pd.testing.assert_frame_equal(
            actual["AccumulatedAnnualDemand"], expected["AccumulatedAnnualDemand"]
        )

    def test_change_types(self, user_config):

        data = [
            ["SIMPLICITY", "ETH", 2014.0, 1],
            ["SIMPLICITY", "ETH", 2015.0, 1],
        ]
        df = pd.DataFrame(
            data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"]
        ).astype({"REGION": str, "FUEL": str, "YEAR": float, "VALUE": int})
        parameters = {"AccumulatedAnnualDemand": df}

        reader = ReadMemory(parameters, user_config=user_config)
        actual, _ = reader.read()

        expected = {
            "AccumulatedAnnualDemand": pd.DataFrame(
                data=[
                    ["SIMPLICITY", "ETH", 2014, 1.0],
                    ["SIMPLICITY", "ETH", 2015, 1.0],
                ],
                columns=["REGION", "FUEL", "YEAR", "VALUE"],
            )
            .astype({"REGION": str, "FUEL": str, "YEAR": "int64", "VALUE": float})
            .set_index(["REGION", "FUEL", "YEAR"])
        }

        assert "AccumulatedAnnualDemand" in actual.keys()
        pd.testing.assert_frame_equal(
            actual["AccumulatedAnnualDemand"], expected["AccumulatedAnnualDemand"]
        )


class TestReadMemoryStrategy:
    def test_read_memory(self, user_config):

        data = [
            ["SIMPLICITY", "ETH", 2014, 1.0],
            ["SIMPLICITY", "RAWSUG", 2014, 0.5],
            ["SIMPLICITY", "ETH", 2015, 1.03],
            ["SIMPLICITY", "RAWSUG", 2015, 0.51],
        ]
        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"])
        parameters = {"AccumulatedAnnualDemand": df}

        actual, default_values = ReadMemory(parameters, user_config).read()

        expected = {
            "AccumulatedAnnualDemand": pd.DataFrame(
                data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"]
            ).set_index(["REGION", "FUEL", "YEAR"])
        }

        assert "AccumulatedAnnualDemand" in actual.keys()
        pd.testing.assert_frame_equal(
            actual["AccumulatedAnnualDemand"], expected["AccumulatedAnnualDemand"]
        )

    def test_read_memory_user_config(self, user_config):

        data = [
            ["SIMPLICITY", "ETH", 2014, 1.0],
            ["SIMPLICITY", "RAWSUG", 2014, 0.5],
            ["SIMPLICITY", "ETH", 2015, 1.03],
            ["SIMPLICITY", "RAWSUG", 2015, 0.51],
        ]
        df = pd.DataFrame(data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"])
        parameters = {"AccumulatedAnnualDemand": df}

        actual, default_values = ReadMemory(parameters, user_config=user_config).read()

        expected = {
            "AccumulatedAnnualDemand": pd.DataFrame(
                data=data, columns=["REGION", "FUEL", "YEAR", "VALUE"]
            ).set_index(["REGION", "FUEL", "YEAR"])
        }

        assert "AccumulatedAnnualDemand" in actual.keys()
        pd.testing.assert_frame_equal(
            actual["AccumulatedAnnualDemand"], expected["AccumulatedAnnualDemand"]
        )

        assert default_values["AccumulatedAnnualDemand"] == 0


class TestConfig:
    def test_read_config(self, user_config):

        read = ReadDatafile(user_config=user_config)

        actual = read.user_config
        expected = {
            "default": 0,
            "dtype": "float",
            "indices": ["REGION", "FUEL", "YEAR"],
            "type": "param",
            "index_dtypes": {
                "FUEL": "str",
                "REGION": "str",
                "VALUE": "float",
                "YEAR": "int64",
            },
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

    def test_convert_amply_to_dataframe(self, user_config):

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

        read = ReadDatafile(user_config=user_config)

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

    def test_convert_amply_data_to_list_of_lists(self, user_config):

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
        read = ReadDatafile(user_config=user_config)
        actual = read._convert_amply_data_to_list(data)
        assert actual == expected

    def test_load_parameters(self, user_config):

        config = {"TestParameter": {"type": "param", "indices": ["index1", "index2"]}}
        read = ReadDatafile(user_config=user_config)
        actual = read._load_parameter_definitions(config)
        expected = "param TestParameter {index1,index2};\n"
        assert actual == expected

    def test_load_sets(self, user_config):

        config = {"TestSet": {"type": "set"}}

        read = ReadDatafile(user_config=user_config)
        actual = read._load_parameter_definitions(config)
        expected = "set TestSet;\n"
        assert actual == expected

    def test_catch_error_no_parameter(self, caplog, user_config):
        """Fix for https://github.com/OSeMOSYS/otoole/issues/70 where parameter in
        datafile but not in config causes error.  Instead, throw warning (and advise
        that user should use a custom configuration).
        """
        read = ReadDatafile(user_config=user_config)
        config = read.user_config
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

    def test_read_datafile_with_defaults(self, user_config):
        datafile = os.path.join("tests", "fixtures", "simplicity.txt")
        reader = ReadDatafile(user_config=user_config, write_defaults=True)
        actual, _ = reader.read(datafile)
        data = [
            ["SIMPLICITY", "DAM", 2014, 0.0],
            ["SIMPLICITY", "DAM", 2015, 0.0],
            ["SIMPLICITY", "DAM", 2016, 0.0],
        ]
        expected = pd.DataFrame(
            data, columns=["REGION", "STORAGE", "YEAR", "VALUE"]
        ).set_index(["REGION", "STORAGE", "YEAR"])

        pd.testing.assert_frame_equal(actual["CapitalCostStorage"].iloc[:3], expected)


class TestReadExcel:
    def test_read_excel_yearsplit(self, user_config):
        """ """
        spreadsheet = os.path.join("tests", "fixtures", "combined_inputs.xlsx")
        reader = ReadExcel(user_config=user_config)
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

    def test_read_excel_with_defaults(self, user_config):
        spreadsheet = os.path.join("tests", "fixtures", "combined_inputs.xlsx")
        reader = ReadExcel(user_config=user_config, write_defaults=True)
        actual, _ = reader.read(spreadsheet)
        data = [
            ["09_ROK", "CO2", 2017, -1.0],
            ["09_ROK", "CO2", 2018, -1.0],
            ["09_ROK", "CO2", 2019, -1.0],
        ]
        expected = pd.DataFrame(
            data, columns=["REGION", "EMISSION", "YEAR", "VALUE"]
        ).set_index(["REGION", "EMISSION", "YEAR"])

        pd.testing.assert_frame_equal(actual["AnnualEmissionLimit"].iloc[:3], expected)

    def test_narrow_parameters(self, user_config):
        data = [
            ["IW0016", 0.238356164, 0.238356164, 0.238356164],
            ["IW1624", 0.119178082, 0.119178082, 0.119178082],
            ["IH0012", 0.071232876, 0.071232876, 0.071232876],
        ]
        df = pd.DataFrame(data, columns=["TIMESLICE", 2017, 2018, 2019])
        name = "YearSplit"

        reader = ReadExcel(user_config=user_config)
        actual = reader._convert_wide_2_narrow(df, name)
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

    def test_invalid_column_name(self, user_config):
        data = [
            ["ELC", "IW0016", 0.238356164, 0.238356164, 0.238356164],
            ["ELC", "IW1624", 0.119178082, 0.119178082, 0.119178082],
            ["ELC", "IH0012", 0.071232876, 0.071232876, 0.071232876],
        ]
        df = pd.DataFrame(data, columns=["VALUE", "TIMESLICE", 2017, 2018, 2019])
        reader = ReadExcel(user_config=user_config)
        with raises(OtooleError):
            reader._convert_wide_2_narrow(df=df, name="example")

    def test_check_index(self, user_config):

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
        df = {
            "YearSplit": pd.DataFrame(data, columns=["TIMESLICE", "YEAR", "VALUE"])
            .astype({"YEAR": object})
            .set_index(["TIMESLICE", "YEAR"])
        }
        reader = ReadExcel(user_config=user_config)
        actual = reader._check_index(df)
        expected = {
            "YearSplit": pd.DataFrame(
                data, columns=["TIMESLICE", "YEAR", "VALUE"]
            ).set_index(["TIMESLICE", "YEAR"])
        }
        pd.testing.assert_frame_equal(actual["YearSplit"], expected["YearSplit"])


class TestReadCSV:
    accumulated_annual_demand_df = pd.DataFrame(
        [
            ["SIMPLICITY", "ETH", 2014, 1.0],
            ["SIMPLICITY", "RAWSUG", 2014, 0.5],
            ["SIMPLICITY", "ETH", 2015, 1.03],
            ["SIMPLICITY", "RAWSUG", 2015, 0.51],
            ["SIMPLICITY", "ETH", 2016, 1.061],
            ["SIMPLICITY", "RAWSUG", 2016, 0.519],
        ],
        columns=["REGION", "FUEL", "YEAR", "VALUE"],
    )
    availability_factor_df = pd.DataFrame(
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"]
    )

    test_data = [
        ("AccumulatedAnnualDemand", accumulated_annual_demand_df),
        ("AvailabilityFactor", availability_factor_df),
    ]

    @mark.parametrize("parameter, expected", test_data, ids=["full", "empty"])
    def test_get_input_data_empty(self, user_config, parameter, expected):
        reader = ReadCsv(user_config=user_config)
        filepath = os.path.join("tests", "fixtures", "data")
        details = user_config[parameter]
        actual = reader._get_input_data(filepath, parameter, details)

        pd.testing.assert_frame_equal(actual, expected)

    def test_read_default_values_csv_fails(self, user_config, tmp_path):
        f = tmp_path / "input/default_values.csv"
        f.parent.mkdir()
        f.touch()

        reader = ReadCsv(user_config=user_config)
        with raises(OtooleDeprecationError):
            reader._check_for_default_values_csv(f)

    def test_read_default_values_csv(self, user_config):
        filepath = os.path.join(
            "tests", "fixtures", "data", "AccumulatedAnnualDemand.csv"
        )
        reader = ReadCsv(user_config=user_config)
        actual = reader._check_for_default_values_csv(filepath)
        expected = None
        assert actual == expected

    def test_read_csv_with_defaults(self):
        user_config_path = os.path.join(
            "tests", "fixtures", "super_simple", "super_simple.yaml"
        )
        with open(user_config_path, "r") as config_file:
            user_config = _read_file(config_file, ".yaml")

        filepath = os.path.join("tests", "fixtures", "super_simple", "csv")
        reader = ReadCsv(user_config=user_config, write_defaults=True)
        actual, _ = reader.read(filepath)
        data = [
            ["BB", "gas_import", 2016, 0.0],
            ["BB", "gas_plant", 2016, 1.03456],
        ]
        expected = pd.DataFrame(
            data, columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"]
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        pd.testing.assert_frame_equal(actual["CapitalCost"], expected)


class TestReadTabular:
    """Methods shared for csv and excel"""

    test_data = [
        (True, ["REGION", "TECHNOLOGY"], {}),
        (
            False,
            ["REGION", "TECHNOLOGY"],
            {"REGION": str.strip, "TECHNOLOGY": str.strip},
        ),
    ]

    @mark.parametrize(
        "keep_whitespace, indices, expected",
        test_data,
        ids=["create_empty", "create_full"],
    )
    def test_whitespace_converter(
        self, user_config, keep_whitespace, indices, expected
    ):
        reader = ReadCsv(user_config=user_config, keep_whitespace=keep_whitespace)
        actual = reader._whitespace_converter(indices)
        assert actual == expected


class TestLongifyData:
    """Tests for the preprocess.longify_data module"""

    # example availability factor data
    data_valid = pd.DataFrame(
        [
            ["SIMPLICITY", "ETH", 2014, 1.0],
            ["SIMPLICITY", "RAWSUG", 2014, 0.5],
            ["SIMPLICITY", "ETH", 2015, 1.03],
            ["SIMPLICITY", "RAWSUG", 2015, 0.51],
            ["SIMPLICITY", "ETH", 2016, 1.061],
            ["SIMPLICITY", "RAWSUG", 2016, 0.519],
        ],
        columns=["REGION", "FUEL", "YEAR", "VALUE"],
    )

    data_invalid = pd.DataFrame(
        [
            ["SIMPLICITY", "ETH", "invalid", 1.0],
            ["SIMPLICITY", "RAWSUG", 2014, 0.5],
        ],
        columns=["REGION", "FUEL", "YEAR", "VALUE"],
    )

    def test_check_datatypes_valid(self, user_config):
        df = self.data_valid.astype(
            {"REGION": str, "FUEL": str, "YEAR": int, "VALUE": float}
        )
        actual = check_datatypes(df, user_config, "AvailabilityFactor")
        expected = df.copy()

        pd.testing.assert_frame_equal(actual, expected)

    def test_check_datatypes_invalid(self, user_config):
        df = self.data_invalid

        with raises(ValueError):
            check_datatypes(df, user_config, "AvailabilityFactor")


class TestExpandRequiredParameters:
    """Tests the expansion of required parameters for results processing"""

    region = pd.DataFrame(data=["SIMPLICITY"], columns=["VALUE"])

    technology = pd.DataFrame(data=["NGCC"], columns=["VALUE"])

    def test_no_expansion(self):

        user_config = {
            "REGION": {
                "dtype": "str",
                "type": "set",
            },
        }

        reader = DummyReadResults(user_config=user_config)
        defaults = {}
        input_data = {}

        actual = reader._expand_required_params(input_data, defaults)

        assert not actual

    def test_expansion(self, user_config, discount_rate_empty, discount_rate_idv_empty):

        user_config["DiscountRateIdv"] = {
            "indices": ["REGION", "TECHNOLOGY"],
            "type": "param",
            "dtype": "float",
            "default": 0.10,
        }

        reader = DummyReadResults(user_config=user_config)
        defaults = reader._read_default_values(user_config)
        input_data = {
            "REGION": self.region,
            "TECHNOLOGY": self.technology,
            "DiscountRate": discount_rate_empty,
            "DiscountRateIdv": discount_rate_idv_empty,
        }

        actual = reader._expand_required_params(input_data, defaults)

        actual_dr = actual["DiscountRate"]

        expected_dr = pd.DataFrame(
            data=[["SIMPLICITY", 0.05]],
            columns=["REGION", "VALUE"],
        ).set_index(["REGION"])

        pd.testing.assert_frame_equal(actual_dr, expected_dr)

        actual_dr_idv = actual["DiscountRateIdv"]

        expected_dr_idv = pd.DataFrame(
            data=[["SIMPLICITY", "NGCC", 0.10]],
            columns=["REGION", "TECHNOLOGY", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY"])

        pd.testing.assert_frame_equal(actual_dr_idv, expected_dr_idv)
