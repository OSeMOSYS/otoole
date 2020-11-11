import pytest

from yaml import FullLoader, load

from otoole.validate import (
    compose_expression,
    compose_multi_expression,
    create_schema,
    read_validation_config,
    validate,
)


@pytest.mark.parametrize(
    "name,expected",
    [
        ("DZAETH", True),
        ("AGOCR1", True),
        ("CO1AGO", False),
        ("AGOETHETH", False),
        ("   ETH", False),
        ("DVA", False),
    ],
)
def test_validate_fuel_code_true(name, expected):

    actual = validate("^(DZA|AGO)(ETH|CR1)", name)
    assert actual == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("DZAETH", True),
        ("AGOCR1", True),
        ("CO1AGO", True),
        ("AGOETHETH", False),
        ("   ETH", False),
        ("DVA", False),
    ],
)
def test_validate_fuel_code_true_multi(name, expected):

    actual = validate("^(DZA|AGO)(ETH|CR1)|^(CO1)(AGO)", name)
    assert actual == expected


def test_compose_expression():

    schema = [
        {"name": "countries", "valid": ["DZA", "AGO"], "position": (1, 3)},
        {"name": "fuels", "valid": ["ETH", "CR1"], "postion": (4, 6)},
    ]

    actual = compose_expression(schema)
    expected = "^(DZA|AGO)(ETH|CR1)"
    assert actual == expected


def test_compose_multi_expression():
    resource = load(
        """
- name: technology_name
  items:
  - name: countries
    valid:
      - DZA
      - AGO
    position: (1, 3)
  - name: fuels
    valid:
      - ETH
      - CR1
    position: (4, 6)
- name: trade_link
  items:
  - name: countries
    valid:
      - DZA
      - AGO
    position: (1, 3)
  - name: tradelink
    valid:
      - EL1EX
      - NG1EX
    position: (4, 8)
      """,
        Loader=FullLoader,
    )
    actual = compose_multi_expression(resource)
    expected = "^(DZA|AGO)(ETH|CR1)|^(DZA|AGO)(EL1EX|NG1EX)"
    assert actual == expected


def test_read_packaged_validation():

    actual = read_validation_config()
    expected = ["codes", "schema"]
    assert list(actual.keys()) == expected
    expected_codes = [
        "fuels",
        "technologies",
        "cooling",
        "tradelink",
        "age",
        "countries",
    ]
    assert list(actual["codes"].keys()) == expected_codes
    assert list(actual["codes"]["technologies"].keys()) == [
        "CH",
        "SC",
        "CV",
        "GC",
        "LS",
        "MS",
        "SS",
        "SA",
        "RC",
        "CC",
        "PW",
        "CN",
        "CS",
        "PU",
        "PV",
        "PS",
        "ON",
        "OF",
        "IM",
        "PR",
        "EX",
        "TR",
        "DI",
    ]


def test_create_schema():

    schema = {
        "codes": {"countries": {"DZA": "Algeria", "AGO": "Angola"}},
        "schema": {
            "FUEL": [
                {
                    "items": [
                        {"name": "countries", "valid": "countries", "position": (1, 3)}
                    ],
                    "name": "fuels",
                }
            ]
        },
    }
    actual = create_schema(schema)
    expected = {
        "FUEL": [
            {
                "items": [
                    {"name": "countries", "valid": ["DZA", "AGO"], "position": (1, 3)}
                ],
                "name": "fuels",
            }
        ]
    }
    assert actual == expected


def test_create_schema_two_items():

    schema = {
        "codes": {
            "countries": {"DZA": "Algeria", "AGO": "Angola"},
            "other_countries": {"ELC": "Electricity"},
        },
        "schema": {
            "FUEL": [
                {
                    "items": [
                        {"name": "countries", "valid": "countries", "position": (1, 3)}
                    ],
                    "name": "countries",
                },
                {
                    "items": [
                        {
                            "name": "other_countries",
                            "valid": "other_countries",
                            "position": (1, 3),
                        }
                    ],
                    "name": "other_countries",
                },
            ]
        },
    }
    actual = create_schema(schema)
    expected = {
        "FUEL": [
            {
                "items": [
                    {"name": "countries", "valid": ["DZA", "AGO"], "position": (1, 3)}
                ],
                "name": "countries",
            },
            {
                "items": [
                    {"name": "other_countries", "valid": ["ELC"], "position": (1, 3)}
                ],
                "name": "other_countries",
            },
        ]
    }
    assert actual == expected


def test_create_schema_duplicate_raises():

    schema = {
        "schema": {
            "FUEL": [
                {
                    "items": [
                        {
                            "name": "countries",
                            "valid": ["DZA", "DZA"],
                            "position": (1, 3),
                        }
                    ],
                    "name": "country",
                }
            ]
        }
    }
    with pytest.raises(ValueError):
        create_schema(schema)
