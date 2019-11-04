"""Ensures that technology and fuel names match the convention

For example, to validate the following list of names, you would use the
config shown below::

    theseUNIQUE_ENTRY1
    are__UNIQUE_ENTRY2
    all__UNIQUE_ENTRY1
    validUNIQUE_ENTRY2
    entryUNIQUE_ENTRY1
    in__UNIQUE_ENTRY2
    a____UNIQUE_ENTRY1
    list_UNIQUE_ENTRY2

Create a yaml validation config with the following format::

    codes:
      some_valid_codes:
        UNIQUE_ENTRY1: Description of unique entry 1
        UNIQUE_ENTRY2: Description of unique entry 2
    schema:
      schema_name:
      - name: first_entry_in_schema
        valid: ['these', 'are__', 'all__', 'valid', 'entry', 'in__', 'a____', 'list_']
        position: (1, 5) # a tuple representing the start and end position
      - name: second_entry_in_schema
        valid: some_valid_codes  # references an entry in the codes section of the config
        position: (6, 19) # a tuple representing the start and end position

"""

import logging
import re
from typing import Dict, List

from otoole import read_datapackage, read_packaged_file

logger = logging.getLogger(__name__)


def read_validation_config():
    return read_packaged_file('validate.yaml', 'otoole')


def check_for_duplicates(codes: List) -> bool:
    duplicate_values = len(codes) != len(set(codes))
    return duplicate_values


def create_schema(config: Dict = None):
    """Populate the dict of schema with codes from the validation config

    Arguments
    ---------
    config : dict, default=None
        A configuration dictionary containing ``codes`` and ``schema`` keys
    """
    if config is None:
        config = read_validation_config()

    for _, schema in config['schema'].items():
        for name in schema:
            if isinstance(name['valid'], str):
                name['valid'] = list(config['codes'][name['valid']].keys())
                logger.debug("create_schema: %s", name['valid'])
            elif isinstance(name['valid'], list):
                pass
            else:
                raise ValueError("Entry {} is not correct".format(name['name']))
            if check_for_duplicates(name['valid']):
                raise ValueError("There are duplicate values in codes for {}", name['name'])
    return config['schema']


def compose_expression(schema: List) -> str:
    """Generates a regular expression from a schema

    Returns
    -------
    str
    """
    expression = "^"
    for x in schema:
        logger.debug("compose_expression: %s", x['valid'])
        valid_entries = "|".join(x['valid'])
        expression += "({})".format(valid_entries)
    return expression


def validate(expression: str, name: str) -> bool:
    """Determine if ``name`` matches the ``expression``

    Arguments
    ---------
    expression : str
    name : str

    Returns
    -------
    bool
    """
    logger.debug("Running validation for %s", name)

    valid = False

    pattern = re.compile(expression)

    if pattern.fullmatch(name):
        msg = "{} is valid"
        valid = True
    else:
        msg = "{} is invalid"
        valid = False

    logger.info(msg.format(name))
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


def validate_resource(package, schema, resource):

    logger.debug(schema)

    expression = compose_expression(schema)
    resources = package.get_resource(resource).read(keyed=True)
    for row in resources:
        validate(expression, row['VALUE'])


def main(file_format: str, filepath: str):

    if file_format == 'datapackage':
        package = read_datapackage(filepath)
    elif file_format == 'sql':
        package = read_datapackage(filepath, sql=True)

    schema = create_schema()
    validate_resource(package, schema['technology_name'], 'TECHNOLOGY')
    validate_resource(package, schema['fuel_name'], 'FUEL')
