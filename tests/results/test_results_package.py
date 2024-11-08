import pandas as pd
from pandas.testing import assert_frame_equal
from pytest import fixture, raises

from otoole.results.result_package import (
    ResultsPackage,
    capital_recovery_factor,
    discount_factor,
    discount_factor_storage,
    discount_factor_storage_salvage,
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
def storage():
    return pd.DataFrame(data=["DAM"], columns=["VALUE"])


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
def capital_cost():
    df = pd.DataFrame(
        data=[
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 1.23],
            ["SIMPLICITY", "GAS_EXTRACTION", 2015, 2.34],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 3.45],
            ["SIMPLICITY", "DUMMY", 2014, 4.56],
            ["SIMPLICITY", "DUMMY", 2015, 5.67],
            ["SIMPLICITY", "DUMMY", 2016, 6.78],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return df


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


@fixture
def undiscounted_capital_investment():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DUMMY", 2014, 10],
            ["SIMPLICITY", "DUMMY", 2015, 0],
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 123],
            ["SIMPLICITY", "GAS_EXTRACTION", 2015, 456],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 789],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return data


@fixture
def annual_fixed_operating_cost():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DUMMY", 2014, 10],
            ["SIMPLICITY", "DUMMY", 2015, 0],
            ["SIMPLICITY", "DUMMY", 2016, 10],
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 123],
            ["SIMPLICITY", "GAS_EXTRACTION", 2015, 456],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 789],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return data


@fixture
def annual_variable_operating_cost():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DUMMY", 2014, 10],
            ["SIMPLICITY", "DUMMY", 2015, 10],
            ["SIMPLICITY", "DUMMY", 2016, 0],
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 321],
            ["SIMPLICITY", "GAS_EXTRACTION", 2015, 654],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 987],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return data


@fixture
def discounted_capital_costs():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DUMMY", 2014, 10],
            ["SIMPLICITY", "DUMMY", 2015, 0],
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 111],
            ["SIMPLICITY", "GAS_EXTRACTION", 2015, 222],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 333],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return data


@fixture
def discounted_operational_costs():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DUMMY", 2014, 5],
            ["SIMPLICITY", "DUMMY", 2015, 10],
            ["SIMPLICITY", "DUMMY", 2016, 20],
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 444],
            ["SIMPLICITY", "GAS_EXTRACTION", 2015, 555],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 666],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return data


@fixture
def discounted_emissions_penalty():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DUMMY", 2014, 10],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 777],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return data


@fixture
def discounted_salvage_value():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DUMMY", 2014, 1],
            ["SIMPLICITY", "DUMMY", 2015, 2],
            ["SIMPLICITY", "DUMMY", 2016, 3],
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 888],
            ["SIMPLICITY", "GAS_EXTRACTION", 2015, 999],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 1],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return data


@fixture
def discounted_technology_cost():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DUMMY", 2014, 111],
            ["SIMPLICITY", "DUMMY", 2015, 222],
            ["SIMPLICITY", "DUMMY", 2016, 333],
            ["SIMPLICITY", "GAS_EXTRACTION", 2014, 444],
            ["SIMPLICITY", "GAS_EXTRACTION", 2015, 555],
            ["SIMPLICITY", "GAS_EXTRACTION", 2016, 666],
        ],
        columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
    ).set_index(["REGION", "TECHNOLOGY", "YEAR"])
    return data


@fixture
def capital_cost_storage():
    df = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DAM", 2014, 1.23],
            ["SIMPLICITY", "DAM", 2015, 2.34],
            ["SIMPLICITY", "DAM", 2016, 3.45],
            ["SIMPLICITY", "BATTERY", 2014, 4.56],
            ["SIMPLICITY", "BATTERY", 2015, 5.67],
            ["SIMPLICITY", "BATTERY", 2016, 6.78],
        ],
        columns=["REGION", "STORAGE", "YEAR", "VALUE"],
    ).set_index(["REGION", "STORAGE", "YEAR"])
    return df


@fixture
def new_storage_capacity():
    df = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DAM", 2014, 1.3],
            ["SIMPLICITY", "DAM", 2016, 1.6],
            ["SIMPLICITY", "BATTERY", 2014, 0.9],
        ],
        columns=["REGION", "STORAGE", "YEAR", "VALUE"],
    ).set_index(["REGION", "STORAGE", "YEAR"])
    return df


@fixture
def undiscounted_capital_investment_storage():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DAM", 2014, 1.23],
            ["SIMPLICITY", "DAM", 2015, 2.34],
        ],
        columns=["REGION", "STORAGE", "YEAR", "VALUE"],
    ).set_index(["REGION", "STORAGE", "YEAR"])
    return data


@fixture
def salvage_value_storage():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DAM", 2014, 1.23],
            ["SIMPLICITY", "DAM", 2015, 2.34],
            ["SIMPLICITY", "DAM", 2016, 3.45],
        ],
        columns=["REGION", "STORAGE", "YEAR", "VALUE"],
    ).set_index(["REGION", "STORAGE", "YEAR"])
    return data


@fixture
def discounted_capital_costs_storage():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "BATTERY", 2014, 11.1],
            ["SIMPLICITY", "BATTERY", 2016, 22.2],
            ["SIMPLICITY", "DAM", 2014, 33.3],
            ["SIMPLICITY", "DAM", 2015, 44.4],
            ["SIMPLICITY", "DAM", 2016, 55.5],
        ],
        columns=["REGION", "STORAGE", "YEAR", "VALUE"],
    ).set_index(["REGION", "STORAGE", "YEAR"])
    return data


@fixture
def discounted_salvage_value_storage():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DAM", 2014, 1.23],
            ["SIMPLICITY", "DAM", 2015, 2.34],
            ["SIMPLICITY", "DAM", 2016, 3.45],
            ["SIMPLICITY", "BATTERY", 2014, 4.56],
            ["SIMPLICITY", "BATTERY", 2015, 5.67],
            ["SIMPLICITY", "BATTERY", 2016, 6.78],
        ],
        columns=["REGION", "STORAGE", "YEAR", "VALUE"],
    ).set_index(["REGION", "STORAGE", "YEAR"])
    return data


@fixture
def discounted_storage_cost():
    data = pd.DataFrame(
        data=[
            ["SIMPLICITY", "DAM", 2014, 11.1],
            ["SIMPLICITY", "DAM", 2015, 22.2],
            ["SIMPLICITY", "DAM", 2016, 33.3],
            ["SIMPLICITY", "BATTERY", 2014, 44.4],
            ["SIMPLICITY", "BATTERY", 2015, 55.5],
            ["SIMPLICITY", "BATTERY", 2016, 66.6],
        ],
        columns=["REGION", "STORAGE", "YEAR", "VALUE"],
    ).set_index(["REGION", "STORAGE", "YEAR"])
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


class TestCapitalInvestment:
    def test_calculate_captital_investment_with_dr_idv(
        self,
        capital_cost,
        new_capacity,
        operational_life,
        region,
        year,
        discount_rate,
        discount_rate_idv,
    ):

        results = {
            "CapitalCost": capital_cost,
            "NewCapacity": new_capacity,
            "OperationalLife": operational_life,
            "REGION": region,
            "YEAR": year,
            "DiscountRate": discount_rate,
            "DiscountRateIdv": discount_rate_idv,
        }

        package = ResultsPackage(results)
        actual = package.capital_investment()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DUMMY", 2014, 4.2898413],
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, 1.6352585],
                ["SIMPLICITY", "GAS_EXTRACTION", 2016, 5.6451702],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_calculate_captital_investment_empty_dr_idv(
        self,
        capital_cost,
        new_capacity,
        operational_life,
        region,
        year,
        discount_rate,
        discount_rate_idv_empty,
    ):

        results = {
            "CapitalCost": capital_cost,
            "NewCapacity": new_capacity,
            "OperationalLife": operational_life,
            "REGION": region,
            "YEAR": year,
            "DiscountRate": discount_rate,
            "DiscountRateIdv": discount_rate_idv_empty,
        }

        package = ResultsPackage(results)
        actual = package.capital_investment()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DUMMY", 2014, 4.104],
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, 1.599],
                ["SIMPLICITY", "GAS_EXTRACTION", 2016, 5.52],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_calculate_captital_investment_no_dr_idv(
        self,
        capital_cost,
        new_capacity,
        operational_life,
        region,
        year,
        discount_rate,
    ):

        results = {
            "CapitalCost": capital_cost,
            "NewCapacity": new_capacity,
            "OperationalLife": operational_life,
            "REGION": region,
            "YEAR": year,
            "DiscountRate": discount_rate,
        }

        package = ResultsPackage(results)
        actual = package.capital_investment()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DUMMY", 2014, 4.104],
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, 1.599],
                ["SIMPLICITY", "GAS_EXTRACTION", 2016, 5.52],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_null(self, null: ResultsPackage):
        """ """
        package = null
        with raises(KeyError) as ex:
            package.capital_investment()
        assert "Cannot calculate CapitalInvestment due to missing data" in str(ex)


class TestCapitalInvestmentStorage:
    def test_capital_investment_storage(
        self, region, year, capital_cost_storage, new_storage_capacity
    ):

        results = {
            "REGION": region,
            "YEAR": year,
            "CapitalCostStorage": capital_cost_storage,
            "NewStorageCapacity": new_storage_capacity,
        }

        package = ResultsPackage(results)
        actual = package.capital_investment_storage()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "BATTERY", 2014, 4.104],
                ["SIMPLICITY", "DAM", 2014, 1.599],
                ["SIMPLICITY", "DAM", 2016, 5.52],
            ],
            columns=["REGION", "STORAGE", "YEAR", "VALUE"],
        ).set_index(["REGION", "STORAGE", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_null(self, null: ResultsPackage):
        """ """
        package = null
        with raises(KeyError) as ex:
            package.capital_investment_storage()
        assert "Cannot calculate CapitalInvestmentStorage due to missing data" in str(
            ex
        )


class TestDiscountedCapitalInvestment:
    def test_calculate_discounted_captital_investment(
        self,
        region,
        year,
        undiscounted_capital_investment,
        discount_rate,
    ):

        results = {
            "REGION": region,
            "YEAR": year,
            "DiscountRate": discount_rate,
            "CapitalInvestment": undiscounted_capital_investment,
        }

        package = ResultsPackage(results)
        actual = package.discounted_capital_investment()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DUMMY", 2014, 10],
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, 123],
                ["SIMPLICITY", "GAS_EXTRACTION", 2015, 434.28571428],
                ["SIMPLICITY", "GAS_EXTRACTION", 2016, 715.64625850],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_null(self, null: ResultsPackage):
        """ """
        package = null
        with raises(KeyError) as ex:
            package.discounted_capital_investment()
        assert (
            "Cannot calculate DiscountedCapitalInvestment due to missing data"
            in str(ex)
        )


class TestDiscountedCapitalInvestmentStorage:
    def test_calculate_discounted_captital_investment_storage(
        self,
        region,
        year,
        undiscounted_capital_investment_storage,
        discount_rate_storage,
    ):

        results = {
            "REGION": region,
            "YEAR": year,
            "DiscountRateStorage": discount_rate_storage,
            "CapitalInvestmentStorage": undiscounted_capital_investment_storage,
        }

        package = ResultsPackage(results)
        actual = package.discounted_capital_investment_storage()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DAM", 2014, 1.23],
                ["SIMPLICITY", "DAM", 2015, 2.22857143],
            ],
            columns=["REGION", "STORAGE", "YEAR", "VALUE"],
        ).set_index(["REGION", "STORAGE", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_null(self, null: ResultsPackage):
        """ """
        package = null
        with raises(KeyError) as ex:
            package.discounted_capital_investment_storage()
        assert (
            "Cannot calculate DiscountedCapitalInvestmentStorage due to missing data"
            in str(ex)
        )


class TestDiscountedOperationalCost:
    def test_calculate_discounted_operational_cost(
        self,
        region,
        year,
        discount_rate,
        annual_fixed_operating_cost,
        annual_variable_operating_cost,
    ):

        results = {
            "REGION": region,
            "YEAR": year,
            "DiscountRate": discount_rate,
            "AnnualFixedOperatingCost": annual_fixed_operating_cost,
            "AnnualVariableOperatingCost": annual_variable_operating_cost,
        }

        package = ResultsPackage(results)
        actual = package.discounted_operational_cost()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DUMMY", 2014, 19.51800146],
                ["SIMPLICITY", "DUMMY", 2015, 9.29428640],
                ["SIMPLICITY", "DUMMY", 2016, 8.85170134],
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, 433.29963238],
                ["SIMPLICITY", "GAS_EXTRACTION", 2015, 1031.66579140],
                ["SIMPLICITY", "GAS_EXTRACTION", 2016, 1572.06215832],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_null(self, null: ResultsPackage):
        """ """
        package = null
        with raises(KeyError) as ex:
            package.discounted_operational_cost()
        assert "Cannot calculate DiscountedOperationalCost due to missing data" in str(
            ex
        )


class TestDiscountedCostByTechnology:
    def test_calculate_discounted_cost_by_technology(
        self,
        discounted_capital_costs,
        discounted_operational_costs,
        discounted_emissions_penalty,
        discounted_salvage_value,
    ):

        results = {
            "DiscountedCapitalInvestment": discounted_capital_costs,
            "DiscountedOperationalCost": discounted_operational_costs,
            "DiscountedTechnologyEmissionsPenalty": discounted_emissions_penalty,
            "DiscountedSalvageValue": discounted_salvage_value,
        }

        package = ResultsPackage(results)
        actual = package.discounted_technology_cost()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DUMMY", 2014, 24.0],
                ["SIMPLICITY", "DUMMY", 2015, 8.0],
                ["SIMPLICITY", "DUMMY", 2016, 17.0],
                ["SIMPLICITY", "GAS_EXTRACTION", 2014, -333.0],
                ["SIMPLICITY", "GAS_EXTRACTION", 2015, -222.0],
                ["SIMPLICITY", "GAS_EXTRACTION", 2016, 1775.0],
            ],
            columns=["REGION", "TECHNOLOGY", "YEAR", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_null(self, null: ResultsPackage):
        """ """
        package = null
        with raises(KeyError) as ex:
            package.discounted_technology_cost()
        assert "Cannot calculate DiscountedCostByTechnology due to missing data" in str(
            ex
        )


class TestDiscountedCostByStorage:
    def test_calculate_discounted_cost_by_storage(
        self,
        discounted_capital_costs_storage,
        discounted_salvage_value_storage,
    ):

        results = {
            "DiscountedCapitalInvestmentStorage": discounted_capital_costs_storage,
            "DiscountedSalvageValueStorage": discounted_salvage_value_storage,
        }

        package = ResultsPackage(results)
        actual = package.discounted_storage_cost()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "BATTERY", 2014, 6.54],
                ["SIMPLICITY", "BATTERY", 2015, -5.67],
                ["SIMPLICITY", "BATTERY", 2016, 15.42],
                ["SIMPLICITY", "DAM", 2014, 32.07],
                ["SIMPLICITY", "DAM", 2015, 42.06],
                ["SIMPLICITY", "DAM", 2016, 52.05],
            ],
            columns=["REGION", "STORAGE", "YEAR", "VALUE"],
        ).set_index(["REGION", "STORAGE", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_null(self, null: ResultsPackage):
        """ """
        package = null
        with raises(KeyError) as ex:
            package.discounted_storage_cost()
        assert (
            "Cannot calculate TotalDiscountedCostByStorage due to missing data"
            in str(ex)
        )


class TestTotalDiscountedCost:
    def test_calculate_total_discounted_cost(
        self, discounted_technology_cost, discounted_storage_cost
    ):

        results = {
            "DiscountedCostByTechnology": discounted_technology_cost,
            "DiscountedCostByStorage": discounted_storage_cost,
        }

        package = ResultsPackage(results)
        actual = package.total_discounted_cost()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", 2014, 610.5],
                ["SIMPLICITY", 2015, 854.7],
                ["SIMPLICITY", 2016, 1098.9],
            ],
            columns=["REGION", "YEAR", "VALUE"],
        ).set_index(["REGION", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_calculate_total_discounted_cost_no_storage(
        self, discounted_technology_cost
    ):
        """Situations where NewStorageCapacity not available"""

        results = {
            "DiscountedCostByTechnology": discounted_technology_cost,
        }

        package = ResultsPackage(results)
        actual = package.total_discounted_cost()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", 2014, 555.0],
                ["SIMPLICITY", 2015, 777.0],
                ["SIMPLICITY", 2016, 999.0],
            ],
            columns=["REGION", "YEAR", "VALUE"],
        ).set_index(["REGION", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_null(self, null: ResultsPackage):
        """ """
        package = null
        with raises(KeyError) as ex:
            package.total_discounted_cost()
        assert "Cannot calculate TotalDiscountedCost due to missing data" in str(ex)


class TestDiscountedSalvageValueStorage:
    def test_calculate_discounted_salvage_value_storage(
        self, region, year, storage, salvage_value_storage, discount_rate_storage
    ):

        results = {
            "REGION": region,
            "YEAR": year,
            "STORAGE": storage,
            "DiscountRateStorage": discount_rate_storage,
            "SalvageValueStorage": salvage_value_storage,
        }

        package = ResultsPackage(results)
        actual = package.discounted_salvage_value_storage()
        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DAM", 2014, 0.87413804],
                ["SIMPLICITY", "DAM", 2015, 1.66299431],
                ["SIMPLICITY", "DAM", 2016, 2.45185059],
            ],
            columns=["REGION", "STORAGE", "YEAR", "VALUE"],
        ).set_index(["REGION", "STORAGE", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_null(self, null: ResultsPackage):
        """ """
        package = null
        with raises(KeyError) as ex:
            package.discounted_salvage_value_storage()
        assert (
            "Cannot calculate DiscountedSalvageValueStorage due to missing data"
            in str(ex)
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
                ["SIMPLICITY", "GAS_EXTRACTION", 0.523809523],
                ["SIMPLICITY", "DUMMY", 0.365558912],
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

    def test_crf_no_tech_discount_rate(self, region, discount_rate, operational_life):

        technologies = ["GAS_EXTRACTION", "DUMMY"]
        regions = region["VALUE"].to_list()
        actual = capital_recovery_factor(
            regions, technologies, discount_rate, operational_life
        )

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "GAS_EXTRACTION", 0.5121951219512197],
                ["SIMPLICITY", "DUMMY", 0.34972244250594786],
            ],
            columns=["REGION", "TECHNOLOGY", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY"])

        assert_frame_equal(actual, expected)

    def test_crf_empty_discount_rate(
        self, region, discount_rate_empty, operational_life
    ):
        technologies = ["GAS_EXTRACTION", "DUMMY"]
        regions = region["VALUE"].to_list()

        with raises(ValueError):
            capital_recovery_factor(
                regions, technologies, discount_rate_empty, operational_life
            )


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

    def test_pva_null(self, discount_rate, operational_life):

        actual = pv_annuity([], [], discount_rate, operational_life)

        expected = pd.DataFrame(
            data=[],
            columns=["REGION", "TECHNOLOGY", "VALUE"],
        ).set_index(["REGION", "TECHNOLOGY"])

        assert_frame_equal(actual, expected)

    def test_pva_empty_discount_rate(
        self, region, discount_rate_empty, operational_life
    ):
        technologies = ["GAS_EXTRACTION", "DUMMY"]
        regions = region["VALUE"].to_list()

        with raises(ValueError):
            pv_annuity(regions, technologies, discount_rate_empty, operational_life)


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

    def test_df_empty_discount_rate(self, region, year, discount_rate_empty):
        regions = region["VALUE"].to_list()
        years = year["VALUE"].to_list()

        with raises(ValueError):
            discount_factor(regions, years, discount_rate_empty, 1.0)


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

    def test_df_storage_empty_discount_rate(
        self, region, year, discount_rate_storage_empty
    ):
        storages = ["DAM"]
        regions = region["VALUE"].to_list()
        years = year["VALUE"].to_list()

        with raises(ValueError):
            discount_factor_storage(
                regions, storages, years, discount_rate_storage_empty, 1.0
            )


class TestDiscountFactorStorageSalvage:
    def test_discount_factor_storage_salvage(self, region, year, discount_rate_storage):

        storages = ["DAM"]
        regions = region["VALUE"].to_list()
        years = year["VALUE"].to_list()
        actual = discount_factor_storage_salvage(
            regions, storages, years, discount_rate_storage
        )

        expected = pd.DataFrame(
            data=[
                ["SIMPLICITY", "DAM", 2014, 1.40710042],
                ["SIMPLICITY", "DAM", 2015, 1.40710042],
                ["SIMPLICITY", "DAM", 2016, 1.40710042],
                ["SIMPLICITY", "DAM", 2017, 1.40710042],
                ["SIMPLICITY", "DAM", 2018, 1.40710042],
                ["SIMPLICITY", "DAM", 2019, 1.40710042],
                ["SIMPLICITY", "DAM", 2020, 1.40710042],
            ],
            columns=["REGION", "STORAGE", "YEAR", "VALUE"],
        ).set_index(["REGION", "STORAGE", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_df_null(self, discount_rate_storage):

        actual = discount_factor_storage_salvage([], [], [], discount_rate_storage)

        expected = pd.DataFrame(
            data=[],
            columns=["REGION", "STORAGE", "YEAR", "VALUE"],
        ).set_index(["REGION", "STORAGE", "YEAR"])

        assert_frame_equal(actual, expected)

    def test_df_storage_empty_discount_rate(
        self, region, year, discount_rate_storage_empty
    ):
        storages = ["DAM"]
        regions = region["VALUE"].to_list()
        years = year["VALUE"].to_list()

        with raises(ValueError):
            discount_factor_storage_salvage(
                regions, storages, years, discount_rate_storage_empty
            )


class TestResultsPackage:
    def test_results_package_init(self):

        package = ResultsPackage({})

        with raises(KeyError):
            package["BlaBla"]

    def test_results_package_dummy_results(self):
        """Access results using dictionary keys"""
        package = ResultsPackage({"BlaBla": pd.DataFrame()})

        pd.testing.assert_frame_equal(package["BlaBla"], pd.DataFrame())
