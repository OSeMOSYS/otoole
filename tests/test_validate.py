import pytest

from otoole.validate import validate_fuel_code


@pytest.mark.parametrize(
    "fuel_code,expected",
    [("DZAETH", True),
     ("AGOCO1", True),
     ("CO1AGO", False)]
    )
def test_validate_fuel_code_true(fuel_code, expected):

    actual = validate_fuel_code(fuel_code)
    assert actual == expected
