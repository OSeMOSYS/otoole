from pytest import fixture

import pandas as pd
from pandas.testing import assert_frame_equal

from otoole.results.calculate import (
    compute_accumulated_new_capacity,
    compute_annual_emissions,
    compute_annual_fixed_operating_cost,
    compute_annual_technology_emission_by_mode,
    compute_annual_technology_emissions,
    compute_total_capacity_annual,
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
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return df


@fixture
def new_capacity_bitty():
    df = pd.DataFrame(
        data=[
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 0.0300000000000001],
            ["SIMPLICITY", "GAS_EXTRACTION", 2015, 0.0309999999999999],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 0.032],
            ["SIMPLICITY", "GAS_EXTRACTION", 2017, 0.0329999999999999],
            ["SIMPLICITY", "GAS_EXTRACTION", 2018, 0.0330000000000002],
            ["SIMPLICITY", "DUMMY", 2014, 0.9],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return df


@fixture
def operational_life():
    df = pd.DataFrame(
        data=[["SIMPLICITY", "GAS_EXTRACTION", 2], ["SIMPLICITY", "DUMMY", 3]],
        columns=["REGION", "TECHNOLOGY", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY"])
    return df


@fixture
def operational_life_overlap():
    df = pd.DataFrame(
        data=[["SIMPLICITY", "GAS_EXTRACTION", 30], ["SIMPLICITY", "DUMMY", 30]],
        columns=["REGION", "TECHNOLOGY", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY"])
    return df


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
    return pd.Index(data=[2014, 2015, 2016, 2017, 2018, 2019, 2020])


@fixture
def accumulated_new_capacity():
    data = pd.DataFrame(
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
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return data


@fixture
def residual_capacity():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 1],
            ["SIMPLICITY", "GAS_EXTRACTION", 2015, 1],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 0],
            ["SIMPLICITY", "GAS_EXTRACTION", 2017, 0],
            ["SIMPLICITY", "DUMMY", 2014, 0.1],
            ["SIMPLICITY", "DUMMY", 2015, 0.2],
            ["SIMPLICITY", "DUMMY", 2016, 0.3],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return data


@fixture
def total_capacity():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 2.3],
            ["SIMPLICITY", "GAS_EXTRACTION", 2015, 2.3],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 1.6],
            ["SIMPLICITY", "GAS_EXTRACTION", 2017, 1.6],
            ["SIMPLICITY", "DUMMY", 2014, 1.0],
            ["SIMPLICITY", "DUMMY", 2015, 1.1],
            ["SIMPLICITY", "DUMMY", 2016, 1.2],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return data


@fixture
def fixed_cost():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 1],
            ["SIMPLICITY", "GAS_EXTRACTION", 2015, 1],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 1],
            ["SIMPLICITY", "GAS_EXTRACTION", 2017, 1],
            ["SIMPLICITY", "DUMMY", 2014, 0.5],
            ["SIMPLICITY", "DUMMY", 2015, 0.5],
            ["SIMPLICITY", "DUMMY", 2016, 0.5],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return data


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
        ).set_index(["REGION", "EMISSION", "YEAR"])

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
        ).set_index(["REGION", "EMISSION", "YEAR"])

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
        ).set_index(["REGION", "TECHNOLOGY", "EMISSION", "YEAR"])

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
        ).set_index(["REGION", "TECHNOLOGY", "EMISSION", "YEAR"])

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
        ).set_index(["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"])

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
        ).set_index(["REGION", "TECHNOLOGY", "EMISSION", "MODE_OF_OPERATION", "YEAR"])

        assert_frame_equal(actual, expected)


class TestAccumulatedNewCapacity:
    def test_individual(self, new_capacity, operational_life, year):
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
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_overlapping(self, new_capacity, operational_life_overlap, year):
        actual = compute_accumulated_new_capacity(
            operational_life_overlap, new_capacity, year
        )
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, 1.3],
                ["SIMPLICITY", "GAS_EXTRACTION", 2015, 1.3],
                ["SIMPLICITY", "GAS_EXTRACTION", 2016, 2.9],
                ["SIMPLICITY", "GAS_EXTRACTION", 2017, 2.9],
                ["SIMPLICITY", "GAS_EXTRACTION", 2018, 2.9],
                ["SIMPLICITY", "GAS_EXTRACTION", 2019, 2.9],
                ["SIMPLICITY", "GAS_EXTRACTION", 2020, 2.9],
                ["SIMPLICITY", "DUMMY", 2014, 0.9],
                ["SIMPLICITY", "DUMMY", 2015, 0.9],
                ["SIMPLICITY", "DUMMY", 2016, 0.9],
                ["SIMPLICITY", "DUMMY", 2017, 0.9],
                ["SIMPLICITY", "DUMMY", 2018, 0.9],
                ["SIMPLICITY", "DUMMY", 2019, 0.9],
                ["SIMPLICITY", "DUMMY", 2020, 0.9],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_overlapping_bitty(
        self, new_capacity_bitty, operational_life_overlap, year
    ):
        actual = compute_accumulated_new_capacity(
            operational_life_overlap, new_capacity_bitty, year
        )
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, 0.0300000000000001],
                ["SIMPLICITY", "GAS_EXTRACTION", 2015, 0.0609999999999999],
                ["SIMPLICITY", "GAS_EXTRACTION", 2016, 0.093],
                ["SIMPLICITY", "GAS_EXTRACTION", 2017, 0.126],
                ["SIMPLICITY", "GAS_EXTRACTION", 2018, 0.159],
                ["SIMPLICITY", "GAS_EXTRACTION", 2019, 0.159],
                ["SIMPLICITY", "GAS_EXTRACTION", 2020, 0.159],
                ["SIMPLICITY", "DUMMY", 2014, 0.9],
                ["SIMPLICITY", "DUMMY", 2015, 0.9],
                ["SIMPLICITY", "DUMMY", 2016, 0.9],
                ["SIMPLICITY", "DUMMY", 2017, 0.9],
                ["SIMPLICITY", "DUMMY", 2018, 0.9],
                ["SIMPLICITY", "DUMMY", 2019, 0.9],
                ["SIMPLICITY", "DUMMY", 2020, 0.9],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)


class TestComputeFixedOperatingCost:
    """

    Notes
    -----
    1.3 + 1.0 * 1.0 = 2.3
    1.3 + 1.0 * 1.0 = 2.3
    1.6 + 0.0 * 1.0 = 1.6
    1.6 + 0.0 * 1.0 = 1.6
    0.9 + 0.1 * 0.5 = 0.5
    0.9 + 0.2 * 0.5 = 0.55
    0.9 + 0.3 * 0.5 = 0.6
    """

    def test_compute(self, total_capacity, fixed_cost):
        actual = compute_annual_fixed_operating_cost(total_capacity, fixed_cost)
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, 2.3],
                ["SIMPLICITY", "GAS_EXTRACTION", 2015, 2.3],
                ["SIMPLICITY", "GAS_EXTRACTION", 2016, 1.6],
                ["SIMPLICITY", "GAS_EXTRACTION", 2017, 1.6],
                ["SIMPLICITY", "DUMMY", 2014, 0.5],
                ["SIMPLICITY", "DUMMY", 2015, 0.55],
                ["SIMPLICITY", "DUMMY", 2016, 0.6],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_compute_null(self):
        actual = compute_annual_fixed_operating_cost(pd.DataFrame(), pd.DataFrame())
        expected = pd.DataFrame()
        assert_frame_equal(actual, expected)


class TestComputeTotalAnnualCapacity:
    """

    Notes
    -----
    1.3 + 1.0
    1.3 + 1.0
    1.6 + 0.0
    1.6 + 0.0
    0.9 + 0.1
    0.9 + 0.2
    0.9 + 0.3
    """

    def test_compute(self, accumulated_new_capacity, residual_capacity):
        actual = compute_total_capacity_annual(
            residual_capacity, accumulated_new_capacity
        )
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, 2.3],
                ["SIMPLICITY", "GAS_EXTRACTION", 2015, 2.3],
                ["SIMPLICITY", "GAS_EXTRACTION", 2016, 1.6],
                ["SIMPLICITY", "GAS_EXTRACTION", 2017, 1.6],
                ["SIMPLICITY", "DUMMY", 2014, 1.0],
                ["SIMPLICITY", "DUMMY", 2015, 1.1],
                ["SIMPLICITY", "DUMMY", 2016, 1.2],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_compute_null(self):
        actual = compute_total_capacity_annual(pd.DataFrame(), pd.DataFrame())
        expected = pd.DataFrame()
        assert_frame_equal(actual, expected)
