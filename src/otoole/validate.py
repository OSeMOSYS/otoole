"""Ensures that technology and fuel names match the convention

"""

import logging
import re
from typing import List

logger = logging.getLogger(__name__)


def validate_fuel_name(name: str, country_codes: List[str], fuel_codes: List[str]) -> bool:
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

    valid = False

    expression = '^({country})({fuel})'.format(
        country="|".join(country_codes),
        fuel="|".join(fuel_codes))

    pattern = re.compile(expression)

    if pattern.fullmatch(name):
        msg = "Fuel code {} is valid"
        valid = True
    else:
        msg = "Fuel code {} is invalid"
        valid = False

    logger.debug(msg.format(name))
    return valid
