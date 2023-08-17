import pandas as pd
from pandas.testing import assert_frame_equal

from otoole.preprocess.setup import get_csv_setup_data


def test_get_csv_setup_data():
    config = {
        "AccumulatedAnnualDemand": {
            "indices": ["REGION", "FUEL", "YEAR"],
            "type": "param",
            "dtype": "float",
            "default": 0,
        },
        "REGION": {
            "dtype": "str",
            "type": "set",
        },
        "FUEL": {
            "dtype": "str",
            "type": "set",
        },
        "YEAR": {
            "dtype": "int",
            "type": "set",
        },
        "Demand": {
            "indices": ["REGION", "TIMESLICE", "FUEL", "YEAR"],
            "type": "result",
            "dtype": "float",
            "default": 0,
        },
    }

    accumulated_annual_demand = pd.DataFrame(
        columns=["REGION", "FUEL", "YEAR", "VALUE"]
    ).astype(
        {
            "REGION": "str",
            "FUEL": "str",
            "YEAR": "int64",
            "VALUE": "float",
        }
    )
    expected_inputs = {
        "AccumulatedAnnualDemand": accumulated_annual_demand.set_index(
            ["REGION", "FUEL", "YEAR"]
        ),
        "REGION": pd.DataFrame(columns=["VALUE"]),
        "FUEL": pd.DataFrame(columns=["VALUE"]),
        "YEAR": pd.DataFrame(columns=["VALUE"]),
    }
    expected_defaults = {
        "AccumulatedAnnualDemand": 0,
        "Demand": 0,
    }
    actual_inputs, actual_defaults = get_csv_setup_data(config)

    assert_frame_equal(
        actual_inputs["AccumulatedAnnualDemand"],
        expected_inputs["AccumulatedAnnualDemand"],
    )
    assert_frame_equal(actual_inputs["REGION"], expected_inputs["REGION"])
    assert "Demand" not in actual_inputs
    assert actual_defaults == expected_defaults
