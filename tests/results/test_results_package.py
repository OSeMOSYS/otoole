import pandas as pd
from pandas.testing import assert_frame_equal
from pytest import fixture, raises

from otoole.results.result_package import (
    ResultsPackage,
    capital_recovery_factor,
    discount_factor,
    discount_factor_storage,
    pv_annuity,
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
        """ """
        package = null
        with raises(KeyError) as ex:
            package.annual_emissions()
        assert "Cannot calculate AnnualEmissions due to missing data" in str(ex.value)

    def test_minimal(self, minimal: ResultsPackage):
        """ """
        package = minimal
        actual = package.annual_emissions()

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "CO2", 2014, 1.0]],
            columns=["REGION", "EMISSION", "YEAR", "VALUE"],
        ).set_index(["REGION", "EMISSION", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_missing_tech(self, two_tech):
        """ """
        package = two_tech
        actual = package.annual_emissions()

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "CO2", 2014, 1.0]],
            columns=["REGION", "EMISSION", "YEAR", "VALUE"],
        ).set_index(["REGION", "EMISSION", "YEAR"])
        assert_frame_equal(actual, expected)


class TestCalculateAnnualTechnologyEmissions:
    def test_null(self, null: ResultsPackage):
        """ """
        package = null
        with raises(KeyError) as ex:
            package.annual_technology_emissions()
        assert "Cannot calculate AnnualTechnologyEmission due to missing data" in str(
            ex
        )

    def test_minimal(self, two_tech):
        """ """
        package = two_tech
        actual = package.annual_technology_emissions()

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "GAS_EXTRACTION", "CO2", 2014, 1.0]],
            columns=["REGION", "TECHNOLOGY", "EMISSION", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "EMISSION", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_no_zeros(self, two_tech_emission_activity):
        """ """
        package = two_tech_emission_activity
        actual = package.annual_technology_emissions()

        expected = pd.DataFrame(
            data=[["SIMPLICITY", "GAS_EXTRACTION", "CO2", 2014, 1.0]],
            columns=["REGION", "TECHNOLOGY", "EMISSION", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "EMISSION", "YEAR"])

        assert_frame_equal(actual, expected)


class TestCalculateAnnualTechnologyEmissionsByMode:
    def test_null(self, null):
        """ """
        package = null

        with raises(KeyError) as ex:
            package.annual_technology_emission_by_mode()
        assert (
            "Cannot calculate AnnualTechnologyEmissionByMode due to missing data"
            in str(ex.value)
        )

    def test_minimal(self, two_tech):
        """ """
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
        """ """
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
    def test_crf(self, region, discount_rate_idv, operational_life):

        technologies = ["GAS_EXTRACTION", "DUMMY"]
        regions = region["VALUE"].to_list()
        actual = capital_recovery_factor(
            regions, technologies, discount_rate_idv, operational_life
        )

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "GAS_EXTRACTION", 0.512195121],
                ["SIMPLICITY", "DUMMY", 0.349722442],
            ],
            columns=["REGION", "TECHNOLOGY", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY"])

        assert_frame_equal(actual, expected)

    def test_crf_null(self, discount_rate_idv, operational_life):

        actual = capital_recovery_factor([], [], discount_rate_idv, operational_life)

        expected = pd.DataFrame(
            data=[],
            columns=["REGION", "TECHNOLOGY", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY"])

        assert_frame_equal(actual, expected)


class TestPvAnnuity:
    def test_pva(self, region, discount_rate, operational_life):

        technologies = ["GAS_EXTRACTION", "DUMMY"]
        regions = region["VALUE"].to_list()
        actual = pv_annuity(regions, technologies, discount_rate, operational_life)

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "GAS_EXTRACTION", 1.952380952],
                ["SIMPLICITY", "DUMMY", 2.859410430],
            ],
            columns=["REGION", "TECHNOLOGY", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY"])

        assert_frame_equal(actual, expected)

    def test_pva_null(self, discount_rate):

        actual = pv_annuity([], [], discount_rate, operational_life)

        expected = pd.DataFrame(
            data=[],
            columns=["REGION", "TECHNOLOGY", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY"])

        assert_frame_equal(actual, expected)


class TestDiscountFactor:
    def test_df_start(self, region, year, discount_rate):

        regions = region["VALUE"].to_list()
        years = year["VALUE"].to_list()
        actual = discount_factor(regions, years, discount_rate, 0.0)

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", 2014, 1],
                ["SIMPLICITY", 2015, 1.05],
                ["SIMPLICITY", 2016, 1.1025],
                ["SIMPLICITY", 2017, 1.157625],
                ["SIMPLICITY", 2018, 1.21550625],
                ["SIMPLICITY", 2019, 1.276281562],
                ["SIMPLICITY", 2020, 1.340095640],
            ],
            columns=["REGION", "YEAR", "VALUE"],
        ).set_index(["REGION", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_df_mid(self, region, year, discount_rate):

        regions = region["VALUE"].to_list()
        years = year["VALUE"].to_list()
        actual = discount_factor(regions, years, discount_rate, 0.5)

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", 2014, 1.024695076],
                ["SIMPLICITY", 2015, 1.075929830],
                ["SIMPLICITY", 2016, 1.129726321],
                ["SIMPLICITY", 2017, 1.186212638],
                ["SIMPLICITY", 2018, 1.245523269],
                ["SIMPLICITY", 2019, 1.307799433],
                ["SIMPLICITY", 2020, 1.373189405],
            ],
            columns=["REGION", "YEAR", "VALUE"],
        ).set_index(["REGION", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_df_end(self, region, year, discount_rate):

        regions = region["VALUE"].to_list()
        years = year["VALUE"].to_list()
        actual = discount_factor(regions, years, discount_rate, 1.0)

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", 2014, 1.05],
                ["SIMPLICITY", 2015, 1.1025],
                ["SIMPLICITY", 2016, 1.157625],
                ["SIMPLICITY", 2017, 1.21550625],
                ["SIMPLICITY", 2018, 1.276281562],
                ["SIMPLICITY", 2019, 1.340095640],
                ["SIMPLICITY", 2020, 1.407100422],
            ],
            columns=["REGION", "YEAR", "VALUE"],
        ).set_index(["REGION", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_df_null(self, discount_rate):

        actual = discount_factor([], [], discount_rate, 0.0)

        expected = pd.DataFrame(
            data=[],
            columns=["REGION", "YEAR", "VALUE"],
        ).set_index(["REGION", "YEAR"])

        assert_frame_equal(actual, expected)


class TestDiscountFactorStorage:
    def test_dfs_start(self, region, year, discount_rate_storage):

        storages = ["DAM"]
        regions = region["VALUE"].to_list()
        years = year["VALUE"].to_list()
        actual = discount_factor_storage(
            regions, storages, years, discount_rate_storage, 0.0
        )

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DAM", 2014, 1],
                ["SIMPLICITY", "DAM", 2015, 1.05],
                ["SIMPLICITY", "DAM", 2016, 1.1025],
                ["SIMPLICITY", "DAM", 2017, 1.157625],
                ["SIMPLICITY", "DAM", 2018, 1.21550625],
                ["SIMPLICITY", "DAM", 2019, 1.276281562],
                ["SIMPLICITY", "DAM", 2020, 1.340095640],
            ],
            columns=["REGION", "STORAGE", "YEAR", "VALUE"],
        ).set_index(["REGION", "STORAGE", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_dfs_mid(self, region, year, discount_rate_storage):

        storages = ["DAM"]
        regions = region["VALUE"].to_list()
        years = year["VALUE"].to_list()
        actual = discount_factor_storage(
            regions, storages, years, discount_rate_storage, 0.5
        )

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DAM", 2014, 1.024695076],
                ["SIMPLICITY", "DAM", 2015, 1.075929830],
                ["SIMPLICITY", "DAM", 2016, 1.129726321],
                ["SIMPLICITY", "DAM", 2017, 1.186212638],
                ["SIMPLICITY", "DAM", 2018, 1.245523269],
                ["SIMPLICITY", "DAM", 2019, 1.307799433],
                ["SIMPLICITY", "DAM", 2020, 1.373189405],
            ],
            columns=["REGION", "STORAGE", "YEAR", "VALUE"],
        ).set_index(["REGION", "STORAGE", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_dfs_end(self, region, year, discount_rate_storage):

        storages = ["DAM"]
        regions = region["VALUE"].to_list()
        years = year["VALUE"].to_list()
        actual = discount_factor_storage(
            regions, storages, years, discount_rate_storage, 1.0
        )

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DAM", 2014, 1.05],
                ["SIMPLICITY", "DAM", 2015, 1.1025],
                ["SIMPLICITY", "DAM", 2016, 1.157625],
                ["SIMPLICITY", "DAM", 2017, 1.21550625],
                ["SIMPLICITY", "DAM", 2018, 1.276281562],
                ["SIMPLICITY", "DAM", 2019, 1.340095640],
                ["SIMPLICITY", "DAM", 2020, 1.407100422],
            ],
            columns=["REGION", "STORAGE", "YEAR", "VALUE"],
        ).set_index(["REGION", "STORAGE", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_df_null(self, discount_rate_storage):

        actual = discount_factor_storage([], [], [], discount_rate_storage, 0.0)

        expected = pd.DataFrame(
            data=[],
            columns=["REGION", "STORAGE", "YEAR", "VALUE"],
        ).set_index(["REGION", "STORAGE", "YEAR"])

        assert_frame_equal(actual, expected)


class TestResultsPackage:
    def test_results_package_init(self):

        package = ResultsPackage({})

        with raises(KeyError):
            package["BlaBla"]

    def test_results_package_dummy_results(self):
        """Access results using dictionary keys"""
        package = ResultsPackage({"BlaBla": pd.DataFrame()})

        pd.testing.assert_frame_equal(package["BlaBla"], pd.DataFrame())
