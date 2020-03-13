from pytest import fixture

import pandas as pd
from pandas.testing import assert_frame_equal

from otoole.results.calculate import (
    compute_accumulated_new_capacity,
    compute_annual_emissions,
    compute_annual_technology_emission_by_mode,
    compute_annual_technology_emissions,
)


@fixture
def emission_activity_ratio():
    df = pd.DataFrame(
        data=[["SIMPLICITY", "GAS_EXTRACTION", "CO2", 1, 2014, 1.0]],
        columns=[
            "REGION",
            "TECHNOLOGY",
            "EMISSION",
            "MODE_OF_OPERATION",
            "YEAR",
            "VALUE",
        ],
    )
    return df.set_index(
        ["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"]
    )


@fixture
def emission_activity_ratio_two_techs():
    df = pd.DataFrame(
        data=[
            ["SIMPLICITY", "GAS_EXTRACTION", "CO2", 1, 2014, 1.0],
            ["SIMPLICITY", "DUMMY", "CO2", 1, 2014, 0.0],
        ],
        columns=[
            "REGION",
            "TECHNOLOGY",
            "EMISSION",
            "MODE_OF_OPERATION",
            "YEAR",
            "VALUE",
        ],
    )
    return df.set_index(
        ["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"]
    )


@fixture
def new_capacity():
    df = pd.DataFrame(
        data=[
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 1.3],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 1.6],
            ["SIMPLICITY", "DUMMY", 2014, 0.9],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    )
    return df.set_index(["REGION", "TECHNOLOGY", "YEAR"])


@fixture
def operational_life():
    df = pd.DataFrame(
        data=[["SIMPLICITY", "GAS_EXTRACTION", 2], ["SIMPLICITY", "DUMMY", 3]],
        columns=["REGION", "TECHNOLOGY", "VALUE"],
    )
    return df.set_index(["REGION", "TECHNOLOGY"])


@fixture
def rate_of_activity():
    df = pd.DataFrame(
        data=[
            ["SIMPLICITY", "ID", "GAS_EXTRACTION", 1, 2014, 1],
            ["SIMPLICITY", "IN", "GAS_EXTRACTION", 1, 2014, 1],
            ["SIMPLICITY", "SD", "GAS_EXTRACTION", 1, 2014, 1],
            ["SIMPLICITY", "SN", "GAS_EXTRACTION", 1, 2014, 1],
            ["SIMPLICITY", "WD", "GAS_EXTRACTION", 1, 2014, 1],
            ["SIMPLICITY", "WN", "GAS_EXTRACTION", 1, 2014, 1],
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
    return df.set_index(
        ["REGION", "TIMESLICE", "TECHNOLOGY", "MODE_OF_OPERATION", "YEAR"]
    )


@fixture
def rate_of_activity_two_tech():
    df = pd.DataFrame(
        data=[
            ["SIMPLICITY", "ID", "GAS_EXTRACTION", 1, 2014, 1],
            ["SIMPLICITY", "IN", "GAS_EXTRACTION", 1, 2014, 1],
            ["SIMPLICITY", "SD", "GAS_EXTRACTION", 1, 2014, 1],
            ["SIMPLICITY", "SN", "GAS_EXTRACTION", 1, 2014, 1],
            ["SIMPLICITY", "WD", "GAS_EXTRACTION", 1, 2014, 1],
            ["SIMPLICITY", "WN", "GAS_EXTRACTION", 1, 2014, 1],
            ["SIMPLICITY", "ID", "DUMMY", 1, 2014, 1],
            ["SIMPLICITY", "IN", "DUMMY", 1, 2014, 1],
            ["SIMPLICITY", "SD", "DUMMY", 1, 2014, 1],
            ["SIMPLICITY", "SN", "DUMMY", 1, 2014, 1],
            ["SIMPLICITY", "WD", "DUMMY", 1, 2014, 1],
            ["SIMPLICITY", "WN", "DUMMY", 1, 2014, 1],
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
    return df.set_index(
        ["REGION", "TIMESLICE", "TECHNOLOGY", "MODE_OF_OPERATION", "YEAR"]
    )


@fixture
def yearsplit():
    df = pd.DataFrame(
        data=[
            ["ID", 2014, 0.1667],
            ["IN", 2014, 0.0833],
            ["SD", 2014, 0.1667],
            ["SN", 2014, 0.0833],
            ["WD", 2014, 0.3333],
            ["WN", 2014, 0.1667],
        ],
        columns=["TIMESLICE", "YEAR", "VALUE"],
    )
    return df.set_index(["TIMESLICE", "YEAR"])


@fixture
def year():
    return pd.DataFrame(
        data=[2014, 2015, 2016, 2017, 2018, 2019, 2020], columns=["VALUE"]
    )


class TestCalculateAnnualEmissions:
    def test_null(self):
        """
        """
        emission_activity_ratio = pd.DataFrame()
        yearsplit = pd.DataFrame()
        rate_of_activity = pd.DataFrame()

        actual = compute_annual_emissions(
            emission_activity_ratio, yearsplit, rate_of_activity
        )

        expected = pd.DataFrame()

        assert_frame_equal(actual, expected)

    def test_minimal(self, emission_activity_ratio, yearsplit, rate_of_activity):
        """
        """
        actual = compute_annual_emissions(
            emission_activity_ratio, yearsplit, rate_of_activity
        )

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "CO2", 2014, 1.0]],
            columns=["REGION", "EMISSION", "YEAR", "VALUE"],
        )

        assert_frame_equal(actual, expected)

    def test_missing_tech(
        self, emission_activity_ratio, yearsplit, rate_of_activity_two_tech
    ):
        """
        """
        actual = compute_annual_emissions(
            emission_activity_ratio, yearsplit, rate_of_activity_two_tech
        )

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "CO2", 2014, 1.0]],
            columns=["REGION", "EMISSION", "YEAR", "VALUE"],
        )

        assert_frame_equal(actual, expected)


class TestCalculateAnnualTechnologyEmissions:
    def test_null(self):
        """
        """
        emission_activity_ratio = pd.DataFrame()
        yearsplit = pd.DataFrame()
        rate_of_activity = pd.DataFrame()

        actual = compute_annual_technology_emissions(
            emission_activity_ratio, yearsplit, rate_of_activity
        )

        expected = pd.DataFrame()

        assert_frame_equal(actual, expected)

    def test_minimal(
        self, emission_activity_ratio, yearsplit, rate_of_activity_two_tech
    ):
        """
        """
        actual = compute_annual_technology_emissions(
            emission_activity_ratio, yearsplit, rate_of_activity_two_tech
        )

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "GAS_EXTRACTION", "CO2", 2014, 1.0]],
            columns=["REGION", "TECHNOLOGY", "EMISSION", "YEAR", "VALUE"],
        )

        assert_frame_equal(actual, expected)

    def test_no_zeros(
        self, emission_activity_ratio_two_techs, yearsplit, rate_of_activity_two_tech
    ):
        """
        """
        actual = compute_annual_technology_emissions(
            emission_activity_ratio_two_techs, yearsplit, rate_of_activity_two_tech
        )

        expected = pd.DataFrame(
            data=[
                # ['SIMPLICITY', 'DUMMY', 'CO2', 2014, 0.0],
                ["SIMPLICITY", "GAS_EXTRACTION", "CO2", 2014, 1.0]
            ],
            columns=["REGION", "TECHNOLOGY", "EMISSION", "YEAR", "VALUE"],
        )

        assert_frame_equal(actual, expected)


class TestCalculateAnnualTechnologyEmissionsByMode:
    def test_null(self):
        """
        """
        emission_activity_ratio = pd.DataFrame()
        yearsplit = pd.DataFrame()
        rate_of_activity = pd.DataFrame()

        actual = compute_annual_technology_emission_by_mode(
            emission_activity_ratio, yearsplit, rate_of_activity
        )

        expected = pd.DataFrame()

        assert_frame_equal(actual, expected)

    def test_minimal(
        self, emission_activity_ratio, yearsplit, rate_of_activity_two_tech
    ):
        """
        """
        actual = compute_annual_technology_emission_by_mode(
            emission_activity_ratio, yearsplit, rate_of_activity_two_tech
        )

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "GAS_EXTRACTION", "CO2", 1, 2014, 1.0]],
            columns=[
                "REGION",
                "TECHNOLOGY",
                "EMISSION",
                "MODE_OF_OPERATION",
                "YEAR",
                "VALUE",
            ],
        )

        assert_frame_equal(actual, expected)

    def test_no_zeros(
        self, emission_activity_ratio_two_techs, yearsplit, rate_of_activity_two_tech
    ):
        """
        """
        actual = compute_annual_technology_emission_by_mode(
            emission_activity_ratio_two_techs, yearsplit, rate_of_activity_two_tech
        )

        expected = pd.DataFrame(
            data=[
                # ['SIMPLICITY', 'DUMMY', 'CO2', 2014, 0.0],
                ["SIMPLICITY", "GAS_EXTRACTION", "CO2", 1, 2014, 1.0]
            ],
            columns=[
                "REGION",
                "TECHNOLOGY",
                "EMISSION",
                "MODE_OF_OPERATION",
                "YEAR",
                "VALUE",
            ],
        )

        assert_frame_equal(actual, expected)


class TestAccumulatedNewCapacity:
    def test_compute_accumulated_new_capacity(
        self, new_capacity, operational_life, year
    ):
        actual = compute_accumulated_new_capacity(operational_life, new_capacity, year)
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, 1.3],
                ["SIMPLICITY", "GAS_EXTRACTION", 2015, 1.3],
                ["SIMPLICITY", "GAS_EXTRACTION", 2016, 1.6],
                ["SIMPLICITY", "GAS_EXTRACTION", 2017, 1.6],
                ["SIMPLICITY", "DUMMY", 2014, 0.9],
                ["SIMPLICITY", "DUMMY", 2015, 0.9],
                ["SIMPLICITY", "DUMMY", 2016, 0.9],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        )

        assert_frame_equal(actual, expected)
