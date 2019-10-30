import io
import logging
import sys

import pandas as pd
from datapackage import Package
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


def write_parameter(filepath: io.TextIOBase, df: pd.DataFrame, parameter_name, default):
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


def write_set(filepath: io.TextIOBase, df: pd.DataFrame, set_name):
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


def main(datapackage, datafilepath, sql=False):

    if sql:
        engine = create_engine('sqlite:///{}'.format(datapackage))
        package = Package(storage='sql', engine=engine)
    else:
        package = Package(datapackage)

    with open(datafilepath, 'w') as filepath:

        for resource in package.resources:
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

                default_value = resource.descriptor['schema']['missingValues'][0]
                if len(headers) > 1:
                    write_parameter(filepath, df, resource.name, default=default_value)
                else:
                    write_set(filepath, df, resource.name)
            else:
                logger.warning("Validation error in %s", resource.name)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    path_to_datapackage = sys.argv[1]
    path_to_datafile = sys.argv[2]
    main(path_to_datapackage, path_to_datafile)
