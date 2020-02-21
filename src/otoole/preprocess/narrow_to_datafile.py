import logging
import sys
from abc import abstractmethod
from typing import Dict

import pandas as pd
from datapackage import Package
from pandas_datapackage_reader import read_datapackage
from sqlalchemy import create_engine

from otoole import read_packaged_file

logger = logging.getLogger(__name__)


class DataPackageTo(object):
    """Convert a data package to another format

    Arguments
    ---------
    datapackage: str
        The path to the databackage
    datafilepath: str
        The path to the destination file or folder
    sql: bool, default=False
        Flag to set whether the source datapackage is in sqlite format
    """

    def __init__(self, datapackage: str, datafilepath: str, sql: bool = False):

        self.datapackage = datapackage
        self.datafilepath = datafilepath
        self.sql = sql
        self.package = self._get_package()
        self.default_values = self._get_default_values()
        self.config = read_packaged_file('config.yaml', 'otoole.preprocess')

    def _get_package(self):

        if self.sql:
            engine = create_engine('sqlite:///{}'.format(self.datapackage))
            package = Package(storage='sql', engine=engine)
        else:
            package = read_datapackage(self.datapackage)  # typing: datapackage.Package

        return package

    def _get_default_values(self):
        default_resource = self.package.pop('default_values').set_index('name').to_dict()
        return default_resource['default_value']

    def convert(self):
        """Perform the conversion from datapackage to destination format
        """

        self.header()
        logger.debug(self.default_values)

        writable = {}

        for name, df in self.package.items():
            logger.debug(name)

            if df.empty:
                columns = [x['name'] for x in df._metadata['schema']['fields']]
                df = pd.DataFrame(columns=columns)

            df = df.reset_index()
            if 'index' in df.columns:
                df = df.drop(columns='index')

            logger.debug("Number of columns: %s, %s", len(df.columns), df.columns)
            if len(df.columns) > 1:
                default_value = self.default_values[name]
                writable[name] = self.write_parameter(df, name, default=default_value)

            else:
                writable[name] = self.write_set(df, name)

        self.footer(writable)

    @abstractmethod
    def header(self):
        raise NotImplementedError()

    @abstractmethod
    def write_parameter(self, df: pd.DataFrame, parameter_name: str, default: float) -> pd.DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def write_set(self, df: pd.DataFrame, set_name) -> pd.DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def footer(self, dataframes: Dict[str, pd.DataFrame]):
        raise NotImplementedError()


class DataPackageToCsv(DataPackageTo):

    def header(self):
        with open(self.datafilepath, 'w') as filepath:
            msg = "# Model file written by *otoole*\n"
            filepath.write(msg)

    def write_parameter(self, df: pd.DataFrame, parameter_name: str, default: float):
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

    def write_set(self, df: pd.DataFrame, set_name):
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

    def footer(self, writable):

        with open(self.datafilepath, 'a') as filepath:
            filepath.write('end;\n')


class DataPackageToExcel(DataPackageTo):

    def header(self):
        pass

    def write_parameter(self, df: pd.DataFrame, parameter_name: str, default: float):

        if not df.empty:

            names = df.columns.to_list()
            if len(names) > 2:
                logger.debug("More than 2 columns for {}: {}".format(parameter_name, names))
                rows = names[0:-2]
                columns = names[-2]
                values = names[-1]
                logger.debug("Rows: {}; columns: {}; values: {}", rows, columns, values)
                logger.debug("dtypes: {}".format(df.dtypes))
                pivot = pd.pivot_table(df, index=rows, columns=columns, values=values, fill_value=default)
            elif len(names) == 2:
                logger.debug("Two columns for {}: {}".format(parameter_name, names))
                values = names[-1]
                rows = names[0:-2]
                logger.debug("Rows: {}; values: {}", rows, values)
                pivot = pd.pivot_table(df, index=rows, values=values, fill_value=default)
            else:
                logger.debug("One column for {}: {}".format(parameter_name, names))
                pivot = df.copy()

        else:
            logger.debug("Dataframe {} is empty".format(parameter_name))
            pivot = df.copy()

        return pivot

    def write_set(self, df: pd.DataFrame, set_name):
        return df

    def footer(self, dataframes: Dict[str, pd.DataFrame]):
        with pd.ExcelWriter(self.datafilepath, mode='w') as writer:
            for name, df in dataframes.items():
                df.to_excel(writer, sheet_name=name, merge_cells=False)


def convert_datapackage_to_datafile(path_to_datapackage, path_to_datafile):
    dp = DataPackageToCsv(path_to_datapackage, path_to_datafile)
    dp.convert()


def convert_datapackage_to_excel(path_to_datapackage, path_to_excel):
    dp = DataPackageToExcel(path_to_datapackage, path_to_excel)
    dp.convert()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    path_to_datapackage = sys.argv[1]
    path_to_datafile = sys.argv[2]

    DataPackageToCsv(path_to_datapackage, path_to_datafile)
