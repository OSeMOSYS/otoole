import pytest

from otoole.validate import validate_fuel_name


@pytest.mark.parametrize(
    "name,expected",
    [("DZAETH", True),
     ("AGOCO1", True),
     ("CO1AGO", False),
     ("AGOETHETH", False),
     ("   ETH", False),
     ("DVA", False)]
    )
def test_validate_fuel_code_true(name, expected):

    countries = ['DZA', 'AGO']
    fuels = ['ETH', 'CO1']

    actual = validate_fuel_name(name, countries, fuels)
    assert actual == expected
