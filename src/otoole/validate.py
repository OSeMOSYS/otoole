"""Ensures that technology and fuel names match the convention

"""

import logging
import re

logger = logging.getLogger(__name__)


def validate_fuel_code(fuel_code):

    valid = False

    country_codes = ['DZA', 'AGO']
    fuel_codes = ['ETH', 'CO1', 'CO2', 'BIO', 'COA', 'LFO', 'GAS', 'HFO', 'SOL']

    expression = '^({country})({fuel})'.format(country="|".join(country_codes),
                                               fuel="|".join(fuel_codes))

    pattern = re.compile(expression)

    if pattern.fullmatch(fuel_code):
        msg = "Fuel code {} is valid"
        valid = True
    else:
        msg = "Fuel code {} is invalid"
        valid = False

    logger.debug(msg.format(fuel_code))
    return valid
