import pytest

from otoole.validate import compose_expression, create_schema, read_validation_config, validate


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

    actual = validate("^(DZA|AGO)(ETH|CR1)", name)
    assert actual == expected


def test_compose_expression():

    schema = [{'name': 'countries',
               'valid': ['DZA', 'AGO'],
               'position': (1, 3)
               },
              {'name': 'fuels',
               'valid': ['ETH', 'CR1'],
               'postion': (4, 6)
               }]

    actual = compose_expression(schema)
    expected = "^(DZA|AGO)(ETH|CR1)"
    assert actual == expected


def test_read_packaged_validation():

    actual = read_validation_config()
    expected = ['codes', 'schema']
    assert list(actual.keys()) == expected
    expected_codes = ['fuels', 'technologies', 'cooling', 'age', 'countries']
    assert list(actual['codes'].keys()) == expected_codes
    assert list(actual['codes']['technologies'].keys()) == [
        'CH', 'SC', 'CV', 'GC', 'LS', 'MS', 'SS', 'SA', 'RC', 'CC', 'PW',
        'CN', 'CS', 'PU', 'PV', 'PS', 'ON', 'OF', 'IM', 'PR', 'EX', 'TR', 'DI'
    ]


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


def test_create_schema_duplicate_raises():

    schema = {
        'schema': {'fuel_name': [{'name': 'countries',
                                  'valid': ['DZA', 'DZA'],
                                  'position': (1, 3)}]
                   }
               }
    with pytest.raises(ValueError):
        create_schema(schema)
