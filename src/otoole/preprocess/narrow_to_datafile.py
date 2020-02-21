import logging
import sys
from abc import abstractmethod
from typing import TextIO

import pandas as pd
from datapackage import Package
from sqlalchemy import create_engine
from tableschema.exceptions import RelationError, ValidationError

from otoole.exceptions import OtooleRelationError, OtooleValidationError

logger = logging.getLogger(__name__)


class DataPackageTo(object):

    def __init__(self, datapackage: str, datafilepath: str, sql: bool = False):

        self.datapackage = datapackage
        self.datafilepath = datafilepath
        self.sql = sql
        self.package = self.get_package()
        self.default_values = self.get_default_values()

    def get_package(self):

        if self.sql:
            engine = create_engine('sqlite:///{}'.format(self.datapackage))
            package = Package(storage='sql', engine=engine)
        else:
            package = Package(self.datapackage)  # typing: datapackage.Package

        return package

    def get_default_values(self):
        default_resource = self.package.get_resource('default_values')
        return {x[0]: float(x[1]) for x in default_resource.read()}

    def convert(self):

        self.header()

        for resource in self.package.resources:

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

            except ValidationError as ex:
                raise OtooleValidationError(resource.name, "in resource '{}' - {}".format(resource.name, str(ex)))
            except RelationError as ex:
                raise OtooleRelationError(resource.name, "", "in resource '{}': {}".format(resource.name, str(ex)))

            if resource.name == 'default_values':
                pass
            else:
                df = pd.DataFrame(data, columns=headers)
                if len(headers) > 1:
                    default_value = self.default_values[resource.name]
                    self.write_parameter(self.datafilepath, df, resource.name, default=default_value)

                else:
                    self.write_set(self.datafilepath, df, resource.name)

        self.footer()

    @abstractmethod
    def header():
        raise NotImplementedError()

    @abstractmethod
    def write_parameter(self, filepath: TextIO, df: pd.DataFrame, parameter_name: str, default: float):
        raise NotImplementedError()

    @abstractmethod
    def write_set(self, filepath: TextIO, df: pd.DataFrame, set_name):
        raise NotImplementedError()

    @abstractmethod
    def footer():
        raise NotImplementedError()


class DataPackageToCsv(DataPackageTo):

    def header(self):
        with open(self.datafilepath, 'w') as filepath:
            msg = "# Model file written by *otoole* using datapackage {}\n"
            filepath.write(msg.format(self.package.descriptor['name']))

    def write_parameter(self, filepath: TextIO, df: pd.DataFrame, parameter_name: str, default: float):
        """Write parameter data to a csv file, omitting data which matches the default value

        Arguments
        ---------
        filepath : StreamIO
        df : pandas.DataFrame
        parameter_name : str
        default : int
        """
        with open(self.datafilepath, 'a') as filepath:
            filepath.write('param default {} : {} :=\n'.format(default, parameter_name))

            df = df[df.VALUE != default]

            df.to_csv(path_or_buf=filepath, sep=" ", header=False, index=False)
            filepath.write(';\n')

    def write_set(self, filepath: TextIO, df: pd.DataFrame, set_name):
        """

        Arguments
        ---------
        filepath : StreamIO
        df : pandas.DataFrame
        parameter_name : str
        """
        with open(self.datafilepath, 'a') as filepath:
            filepath.write('set {} :=\n'.format(set_name))
            df.to_csv(path_or_buf=filepath, sep=" ", header=False, index=False)
            filepath.write(';\n')

    def footer(self):
        with open(self.datafilepath, 'a') as filepath:
            filepath.write('end;\n')


def convert_datapackage_to_datafile(path_to_datapackage, path_to_datafile):
    dp = DataPackageToCsv(path_to_datapackage, path_to_datafile)
    dp.convert()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    path_to_datapackage = sys.argv[1]
    path_to_datafile = sys.argv[2]

    DataPackageToCsv(path_to_datapackage, path_to_datafile)
