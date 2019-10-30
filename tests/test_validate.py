import pytest

from otoole.validate import compose_expression, create_schema, read_validation_config, validate_fuel_name


@pytest.mark.parametrize(
    "name,expected",
    [("DZAETH", True),
     ("AGOCR1", True),
     ("CO1AGO", False),
     ("AGOETHETH", False),
     ("   ETH", False),
     ("DVA", False)]
    )
def test_validate_fuel_code_true(name, expected):

    actual = validate_fuel_name(name)
    assert actual == expected


def test_compose_expression():

    schema = [{'name': 'countries',
               'valid': ['DZA', 'AGO'],
               'position': (1, 3)
               },
              {'name': 'fuels',
               'valid': ['ETH', 'CO1'],
               'postion': (4, 6)
               }]

    actual = compose_expression(schema)
    expected = "^(DZA|AGO)(ETH|CO1)"
    assert actual == expected


def test_read_packaged_validation():

    actual = read_validation_config()
    expected = ['codes', 'schema']
    assert list(actual.keys()) == expected
    expected_codes = ['emissions', 'fuels', 'technologies', 'trade', 'process',
                      'cooling', 'age', 'countries']
    assert list(actual['codes'].keys()) == expected_codes


def test_create_schema():

    schema = {
        'codes': {'countries': {'DZA': 'Algeria', 'AGO': 'Angola'}},
        'schema': {'fuel_name': [{'name': 'countries',
                                  'valid': 'countries',
                                  'position': (1, 3)}]
                   }
               }
    actual = create_schema(schema)
    expected = {'fuel_name':
                [{'name': 'countries',
                  'valid': ['DZA', 'AGO'],
                  'position': (1, 3)}]
                }
    assert actual == expected
