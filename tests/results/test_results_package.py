from pytest import fixture, raises

import pandas as pd
from pandas.testing import assert_frame_equal

from otoole.results.result_package import ResultsPackage, capital_recovery_factor


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
def year():
    return pd.DataFrame(
        data=[2014, 2015, 2016, 2017, 2018, 2019, 2020], columns=["VALUE"]
    )


@fixture
def region():
    return pd.DataFrame(data=["SIMPLICITY"], columns=["VALUE"])


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


@fixture
def variable_cost():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "GAS_EXTRACTION", 1, 2014, 1],
            ["SIMPLICITY", "GAS_EXTRACTION", 1, 2015, 1],
            ["SIMPLICITY", "GAS_EXTRACTION", 1, 2016, 1],
            ["SIMPLICITY", "GAS_EXTRACTION", 1, 2017, 1],
            ["SIMPLICITY", "DUMMY", 1, 2014, 0.5],
            ["SIMPLICITY", "DUMMY", 1, 2015, 0.5],
            ["SIMPLICITY", "DUMMY", 1, 2016, 0.5],
        ],
        columns=["REGION", "TECHNOLOGY", "MODE_OF_OPERATION", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "MODE_OF_OPERATION", "YEAR"])
    return data


@fixture(scope="function")
def null() -> ResultsPackage:
    package = ResultsPackage({})
    return package


@fixture(scope="function")
def minimal(emission_activity_ratio, yearsplit, rate_of_activity) -> ResultsPackage:

    dummy_results = {
        "EmissionActivityRatio": emission_activity_ratio,
        "YearSplit": yearsplit,
        "RateOfActivity": rate_of_activity,
    }
    package = ResultsPackage(dummy_results)
    return package


@fixture(scope="function")
def two_tech(
    emission_activity_ratio, yearsplit, rate_of_activity_two_tech
) -> ResultsPackage:
    dummy_results = {
        "EmissionActivityRatio": emission_activity_ratio,
        "YearSplit": yearsplit,
        "RateOfActivity": rate_of_activity_two_tech,
    }
    package = ResultsPackage(dummy_results)
    return package


@fixture(scope="function")
def two_tech_emission_activity(
    emission_activity_ratio_two_techs, yearsplit, rate_of_activity_two_tech
) -> ResultsPackage:
    dummy_results = {
        "EmissionActivityRatio": emission_activity_ratio_two_techs,
        "YearSplit": yearsplit,
        "RateOfActivity": rate_of_activity_two_tech,
    }
    package = ResultsPackage(dummy_results)
    return package


class TestCalculateAnnualEmissions:
    def test_null(self, null: ResultsPackage):
        """
        """
        package = null
        with raises(KeyError) as ex:
            package.annual_emissions()
        assert "Cannot calculate AnnualEmissions due to missing data" in str(ex.value)

    def test_minimal(self, minimal: ResultsPackage):
        """
        """
        package = minimal
        actual = package.annual_emissions()

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "CO2", 2014, 1.0]],
            columns=["REGION", "EMISSION", "YEAR", "VALUE"],
        ).set_index(["REGION", "EMISSION", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_missing_tech(self, two_tech):
        """
        """
        package = two_tech
        actual = package.annual_emissions()

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "CO2", 2014, 1.0]],
            columns=["REGION", "EMISSION", "YEAR", "VALUE"],
        ).set_index(["REGION", "EMISSION", "YEAR"])
        assert_frame_equal(actual, expected)


class TestCalculateAnnualTechnologyEmissions:
    def test_null(self, null: ResultsPackage):
        """
        """
        package = null
        with raises(KeyError) as ex:
            package.annual_technology_emissions()
        assert "Cannot calculate AnnualTechnologyEmission due to missing data" in str(
            ex
        )

    def test_minimal(self, two_tech):
        """
        """
        package = two_tech
        actual = package.annual_technology_emissions()

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "GAS_EXTRACTION", "CO2", 2014, 1.0]],
            columns=["REGION", "TECHNOLOGY", "EMISSION", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "EMISSION", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_no_zeros(self, two_tech_emission_activity):
        """
        """
        package = two_tech_emission_activity
        actual = package.annual_technology_emissions()

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "GAS_EXTRACTION", "CO2", 2014, 1.0]],
            columns=["REGION", "TECHNOLOGY", "EMISSION", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "EMISSION", "YEAR"])

        assert_frame_equal(actual, expected)


class TestCalculateAnnualTechnologyEmissionsByMode:
    def test_null(self, null):
        """
        """
        package = null

        with raises(KeyError) as ex:
            package.annual_technology_emission_by_mode()
        assert (
            "Cannot calculate AnnualTechnologyEmissionByMode due to missing data"
            in str(ex.value)
        )

    def test_minimal(self, two_tech):
        """
        """
        package = two_tech
        actual = package.annual_technology_emission_by_mode()
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

    def test_no_zeros(self, two_tech_emission_activity):
        """
        """
        package = two_tech_emission_activity
        actual = package.annual_technology_emission_by_mode()

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


class TestDiscountedTechnologyEmissionsPenalty:
    def test_calculate(
        self,
        emissions_penalty,
        region,
        year,
        discount_rate,
        annual_technology_emissions_by_mode,
    ):

        results = {
            "AnnualTechnologyEmissionByMode": annual_technology_emissions_by_mode,
            "EmissionsPenalty": emissions_penalty,
            "REGION": region,
            "YEAR": year,
            "DiscountRate": discount_rate,
        }
        package = ResultsPackage(results)
        actual = package.discounted_tech_emis_pen()

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "GAS_EXTRACTION", 2014, 1.2003570897266957]],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)


class TestAccumulatedNewCapacity:
    def test_individual(self, new_capacity, operational_life, year):

        results = {
            "NewCapacity": new_capacity,
            "OperationalLife": operational_life,
            "YEAR": year,
        }
        package = ResultsPackage(results)

        actual = package.accumulated_new_capacity()
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

        results = {
            "NewCapacity": new_capacity,
            "OperationalLife": operational_life_overlap,
            "YEAR": year,
        }
        package = ResultsPackage(results)

        actual = package.accumulated_new_capacity()
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
        results = {
            "NewCapacity": new_capacity_bitty,
            "OperationalLife": operational_life_overlap,
            "YEAR": year,
        }
        package = ResultsPackage(results)

        actual = package.accumulated_new_capacity()
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


class TestComputeFixedandVariableOperatingCost:
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

    def test_fixed(self, total_capacity, fixed_cost):

        results = {"TotalCapacityAnnual": total_capacity, "FixedCost": fixed_cost}
        package = ResultsPackage(results)
        actual = package.annual_fixed_operating_cost()
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

    def test_null_fixed(self, null):
        package = null
        with raises(KeyError) as ex:
            package.annual_fixed_operating_cost()
        assert "Cannot calculate AnnualFixedOperatingCost due to missing data" in str(
            ex.value
        )

    def test_variable(self, rate_of_activity_two_tech, yearsplit, variable_cost):
        """

        ["ID", 2014, 0.1667],
        ["IN", 2014, 0.0833],
        ["SD", 2014, 0.1667],
        ["SN", 2014, 0.0833],
        ["WD", 2014, 0.3333],
        ["WN", 2014, 0.1667],

        """
        results = {
            "RateOfActivity": rate_of_activity_two_tech,
            "YearSplit": yearsplit,
            "VariableCost": variable_cost,
        }
        package = ResultsPackage(results)
        actual = package.annual_variable_operating_cost()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DUMMY", 2014, 0.5],
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, 1.0],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
        assert_frame_equal(actual, expected)

    def test_null_variable(self, null):
        package = null
        with raises(KeyError) as ex:
            package.annual_variable_operating_cost()
        assert (
            "Cannot calculate AnnualVariableOperatingCost due to missing data"
            in str(ex.value)
        )


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

        results = {
            "AccumulatedNewCapacity": accumulated_new_capacity,
            "ResidualCapacity": residual_capacity,
        }
        package = ResultsPackage(results)

        actual = package.total_capacity_annual()
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

    def test_null(self, null):
        package = null
        with raises(KeyError) as ex:
            package.total_capacity_annual()
        assert "Cannot calculate TotalCapacityAnnual due to missing data" in str(
            ex.value
        )


class TestCapitalRecoveryFactor:
    def test_crf(self, discount_rate):

        regions = ["SIMPLICITY"]
        technologies = ["GAS_EXTRACTION"]
        years = [2010, 2011, 2012, 2013, 2014, 2015]
        actual = capital_recovery_factor(regions, technologies, years, discount_rate)

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "GAS_EXTRACTION", 2010, 1.0],
                ["SIMPLICITY", "GAS_EXTRACTION", 2011, 1.05],
                ["SIMPLICITY", "GAS_EXTRACTION", 2012, 1.1025],
                ["SIMPLICITY", "GAS_EXTRACTION", 2013, 1.1576250000000001],
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, 1.2155062500000002],
                ["SIMPLICITY", "GAS_EXTRACTION", 2015, 1.2762815625000004],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_crf_null(self, discount_rate):

        actual = capital_recovery_factor([], [], [], discount_rate)

        expected = pd.DataFrame(
            data=[], columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)


class TestResultsPackage:
    def test_results_package_init(self):

        package = ResultsPackage({})

        with raises(KeyError):
            package["BlaBla"]

    def test_results_package_dummy_results(self):
        """Access results using dictionary keys

        """
        package = ResultsPackage({"BlaBla": pd.DataFrame()})

        pd.testing.assert_frame_equal(package["BlaBla"], pd.DataFrame())
