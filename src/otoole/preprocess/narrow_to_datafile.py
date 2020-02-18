import logging
import sys
from typing import TextIO

import pandas as pd
from datapackage import Package
from sqlalchemy import create_engine
from tableschema.exceptions import RelationError, ValidationError

from otoole.exceptions import OtooleRelationError, OtooleValidationError

logger = logging.getLogger(__name__)


def write_parameter(filepath: TextIO, df: pd.DataFrame, parameter_name, default):
    """

    Arguments
    ---------
    filepath : StreamIO
    df : pandas.DataFrame
    parameter_name : str
    default : int
    """
    filepath.write('param default {} : {} :=\n'.format(default, parameter_name))
    df.to_csv(path_or_buf=filepath, sep=" ", header=False, index=False)
    filepath.write(';\n')
    return filepath


def write_set(filepath: TextIO, df: pd.DataFrame, set_name):
    """

    Arguments
    ---------
    filepath : StreamIO
    df : pandas.DataFrame
    parameter_name : str
    """
    filepath.write('set {} :=\n'.format(set_name))
    df.to_csv(path_or_buf=filepath, sep=" ", header=False, index=False)
    filepath.write(';\n')
    return filepath


def read_narrow_csv(filepath):

    df = pd.read_csv(filepath)
    return df


def main(datapackage: str, datafilepath: str, sql: bool = False):

    if sql:
        engine = create_engine('sqlite:///{}'.format(datapackage))
        package = Package(storage='sql', engine=engine)
    else:
        package = Package(datapackage)  # typing: datapackage.Package

    with open(datafilepath, 'w') as filepath:

        default_resource = package.get_resource('default_values')
        default_values = {x[0]: float(x[1]) for x in default_resource.read()}

        for resource in package.resources:

            try:
                if resource.check_relations():
                    logger.info("%s is valid", resource.name)

                    data = resource.read()
                    resource.infer()

                    if data:
                        headers = resource.headers
                    else:
                        fields = resource.descriptor['schema']['fields']
                        headers = [x['name'] for x in fields]
                    df = pd.DataFrame(data, columns=headers)
                    default_value = default_values[resource.name]
                    if len(headers) > 1:
                        write_parameter(filepath, df, resource.name, default=default_value)
                    else:
                        write_set(filepath, df, resource.name)
            except ValidationError as ex:
                raise OtooleValidationError(resource.name, "in resource '{}' - {}".format(resource.name, str(ex)))
            except RelationError as ex:
                raise OtooleRelationError(resource.name, "", "in resource '{}': {}".format(resource.name, str(ex)))
            except KeyError:
                logger.info("KeyError caused by {}".format(resource.name))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    path_to_datapackage = sys.argv[1]
    path_to_datafile = sys.argv[2]
    main(path_to_datapackage, path_to_datafile)
