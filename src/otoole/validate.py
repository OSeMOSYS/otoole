"""Ensures that technology and fuel names match the convention

"""

import logging
import re
from typing import List

from otoole import read_packaged_file

logger = logging.getLogger(__name__)


def read_validation_config():

    return read_packaged_file('validate.yaml', 'otoole')


def create_schema(config=None):
    if config is None:
        config = read_validation_config()

    for _, schema in config['schema'].items():
        for name in schema:
            if isinstance(name['valid'], str):
                name['valid'] = list(config['codes'][name['valid']].keys())
    return config['schema']


def compose_expression(schema: List) -> str:
    """Generates a regular expression from a schema
    """
    expression = "^"
    for x in schema:
        valid_entries = "|".join(x['valid'])
        expression += "({})".format(valid_entries)
    return expression


def validate(expression, name):

    valid = False

    pattern = re.compile(expression)

    if pattern.fullmatch(name):
        msg = "{} is valid"
        valid = True
    else:
        msg = "{} is invalid"
        valid = False

    logger.debug(msg.format(name))
    return valid


def validate_fuel_name(name: str) -> bool:
    """Validate a fuel name

    Arguments
    ---------
    name : str
    country_codes : list
    fuel_codes : list

    Returns
    -------
    True if ``name`` is valid according to ``country_codes`` and ``fuel_codes``
    otherwise False
    """

    schema = create_schema()

    expression = compose_expression(schema['fuel_name'])

    valid = validate(expression, name)

    return valid
