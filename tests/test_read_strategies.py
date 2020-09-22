from io import StringIO
from textwrap import dedent
from typing import List

from pytest import mark

import pandas as pd
from amply import Amply

from otoole import ReadDatafile, ReadMemory
from otoole.results.results import ReadCbc


class TestReadCbc:

    test_data = [
        (
            dedent(
                """Optimal - objective value 4483.96932237
                             1 TotalDiscountedCost(SIMPLICITY,2015)                                                   187.01576                       0
                             2 TotalDiscountedCost(SIMPLICITY,2016)                                                   183.30788                       0
                             3 TotalDiscountedCost(SIMPLICITY,2017)                                                   181.05465                       0
                             4 TotalDiscountedCost(SIMPLICITY,2018)                                                   218.08923                       0
                             5 TotalDiscountedCost(SIMPLICITY,2019)                                                   193.85792                       0
                             6 TotalDiscountedCost(SIMPLICITY,2020)                                                   233.79202                       0

                         """
            ),
            pd.DataFrame(
                data=[
                    ["TotalDiscountedCost", "SIMPLICITY,2015", 187.01576],
                    ["TotalDiscountedCost", "SIMPLICITY,2016", 183.30788],
                    ["TotalDiscountedCost", "SIMPLICITY,2017", 181.05465],
                    ["TotalDiscountedCost", "SIMPLICITY,2018", 218.08923],
                    ["TotalDiscountedCost", "SIMPLICITY,2019", 193.85792],
                    ["TotalDiscountedCost", "SIMPLICITY,2020", 233.79202],
                ],
                columns=["Variable", "Index", "Value"],
            ),
        )
    ]

    @mark.parametrize("cbc_input,expected", test_data, ids=["TotalDiscountedCost"])
    def test_read_cbc_to_dataframe(self, cbc_input, expected):
        cbc_reader = ReadCbc()
        with StringIO(cbc_input) as file_buffer:
            actual = cbc_reader._convert_cbc_to_dataframe(file_buffer)
        pd.testing.assert_frame_equal(actual, expected)

    test_data_2 = [
        # First case
        (
            pd.DataFrame(
                data=[
                    ["TotalDiscountedCost", "SIMPLICITY,2015", 187.01576],
                    ["TotalDiscountedCost", "SIMPLICITY,2016", 183.30788],
                    ["TotalDiscountedCost", "SIMPLICITY,2017", 181.05465],
                    ["TotalDiscountedCost", "SIMPLICITY,2018", 218.08923],
                    ["TotalDiscountedCost", "SIMPLICITY,2019", 193.85792],
                    ["TotalDiscountedCost", "SIMPLICITY,2020", 233.79202],
                ],
                columns=["Variable", "Index", "Value"],
            ),
            {},
            (
                {
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
            ),
        ),
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
            {},
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
        "results,cbc_input,expected",
        test_data_2,
        ids=["TotalDiscountedCost", "AnnualEmissions1"],
    )
    def test_convert_cbc_to_csv_long(self, results, cbc_input, expected):
        cbc_reader = ReadCbc()
        actual = cbc_reader._convert_dataframe_to_csv(results, cbc_input)
        assert isinstance(actual, dict)
        for name, df in actual.items():
            pd.testing.assert_frame_equal(df, expected[name])

    def test_convert_cbc_to_csv_short(self):
        cbc_results = pd.DataFrame(
            data=[
                ["RateOfActivity", "SIMPLICITY,ID,GAS_EXTRACTION,1,2014", 1],
                ["RateOfActivity", "SIMPLICITY,IN,GAS_EXTRACTION,1,2014", 1],
                ["RateOfActivity", "SIMPLICITY,SD,GAS_EXTRACTION,1,2014", 1],
                ["RateOfActivity", "SIMPLICITY,SN,GAS_EXTRACTION,1,2014", 1],
                ["RateOfActivity", "SIMPLICITY,WD,GAS_EXTRACTION,1,2014", 1],
                ["RateOfActivity", "SIMPLICITY,WN,GAS_EXTRACTION,1,2014", 1],
                ["RateOfActivity", "SIMPLICITY,ID,DUMMY,1,2014", 1],
                ["RateOfActivity", "SIMPLICITY,IN,DUMMY,1,2014", 1],
                ["RateOfActivity", "SIMPLICITY,SD,DUMMY,1,2014", 1],
                ["RateOfActivity", "SIMPLICITY,SN,DUMMY,1,2014", 1],
                ["RateOfActivity", "SIMPLICITY,WD,DUMMY,1,2014", 1],
                ["RateOfActivity", "SIMPLICITY,WN,DUMMY,1,2014", 1],
            ],
            columns=["Variable", "Index", "Value"],
        )
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
        actual = cbc_reader._convert_dataframe_to_csv(cbc_results, input_data)
        assert isinstance(actual, dict)
        pd.testing.assert_frame_equal(actual["AnnualEmissions"], expected)


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
        print(actual, expected)
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
        config = read.config
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
