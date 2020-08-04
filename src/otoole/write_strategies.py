import logging
import os
from typing import Any, TextIO

import pandas as pd

from otoole import read_packaged_file
from otoole.input import WriteStrategy
from otoole.read_strategies import CSV_TO_EXCEL

logger = logging.getLogger(__name__)


class WriteExcel(WriteStrategy):
    def _header(self):
        return pd.ExcelWriter(self.filepath, mode="w")

    def _form_parameter(
        self, df: pd.DataFrame, parameter_name: str, default: float
    ) -> pd.DataFrame:
        """Converts data into wide format

        Arguments
        ---------
        df: pd.DataFrame
        parameter_name: str
        default: float

        Returns
        -------
        pandas.DataFrame
        """

        if not df.empty:

            names = df.columns.to_list()
            if len(names) > 2:
                logger.debug(
                    "More than 2 columns for {}: {}".format(parameter_name, names)
                )
                rows = names[0:-2]
                columns = names[-2]
                values = names[-1]
                logger.debug("Rows: %s; columns: %s; values: %s", rows, columns, values)
                logger.debug("dtypes: {}".format(df.dtypes))
                pivot = pd.pivot_table(
                    df, index=rows, columns=columns, values=values, fill_value=default
                )
            elif len(names) == 2:
                logger.debug("Two columns for {}: {}".format(parameter_name, names))
                rows = names[0]
                values = names[1]
                logger.debug("Rows: %s; values: %s", rows, values)
                pivot = pd.pivot_table(
                    df, index=rows, values=values, fill_value=default
                )
            else:
                logger.debug("One column for {}: {}".format(parameter_name, names))
                pivot = df.copy()
                pivot = pivot.reset_index(drop=True)

        else:
            logger.debug("Dataframe {} is empty".format(parameter_name))
            pivot = df.copy()

        return pivot

    def _write_parameter(
        self,
        df: pd.DataFrame,
        parameter_name: str,
        handle: pd.ExcelWriter,
        default: float,
    ):
        try:
            name = CSV_TO_EXCEL[parameter_name]
        except KeyError:
            name = parameter_name
        df = self._form_parameter(df, parameter_name, default)
        df.to_excel(handle, sheet_name=name, merge_cells=False)

    def _write_set(self, df: pd.DataFrame, set_name, handle: pd.ExcelWriter):
        df.to_excel(handle, sheet_name=set_name, merge_cells=False, index=False)

    def _footer(self, handle=pd.ExcelWriter):
        handle.close()


class WriteDatafile(WriteStrategy):
    def _header(self):
        filepath = open(self.filepath, "w")
        msg = "# Model file written by *otoole*\n"
        filepath.write(msg)
        return filepath

    def _form_parameter(self, df: pd.DataFrame, default: float):

        df = df[df.VALUE != default]
        return df

    def _write_parameter(
        self, df: pd.DataFrame, parameter_name: str, handle: TextIO, default: float
    ):
        """Write parameter data to a GMPL datafile, omitting data with default value

        Arguments
        ---------
        filepath : StreamIO
        df : pandas.DataFrame
        parameter_name : str
        handle: TextIO
        default : int
        """
        df = self._form_parameter(df, default)
        handle.write("param default {} : {} :=\n".format(default, parameter_name))
        df.to_csv(path_or_buf=handle, sep=" ", header=False, index=False)
        handle.write(";\n")

    def _write_set(self, df: pd.DataFrame, set_name, handle: TextIO):
        """Write set data to a GMPL datafile

        Arguments
        ---------
        df : pandas.DataFrame
        set_name : str
        handle: TextIO
        """
        handle.write("set {} :=\n".format(set_name))
        df.to_csv(path_or_buf=handle, sep=" ", header=False, index=False)
        handle.write(";\n")

    def _footer(self, handle: TextIO):
        handle.write("end;\n")
        handle.close()


class WriteCsv(WriteStrategy):
    def _header(self) -> Any:
        os.makedirs(os.path.join(self.filepath), exist_ok=True)
        return None

    def _write_parameter(
        self, df: pd.DataFrame, parameter_name: str, handle: TextIO, default: float
    ) -> pd.DataFrame:
        """Write parameter data"""
        self._write_out_dataframe(self.filepath, parameter_name, df)

    def _write_out_dataframe(self, folder, parameter, df):
        """Writes out a dataframe as a csv into the data subfolder of a datapackage

        Arguments
        ---------
        folder : str
        parameter : str
        df : pandas.DataFrame

        """
        filepath = os.path.join(folder, parameter + ".csv")
        with open(filepath, "w") as csvfile:
            logger.info(
                "Writing %s rows into narrow file for %s", df.shape[0], parameter
            )
            df.to_csv(csvfile, index=False)

    def _write_set(self, df: pd.DataFrame, set_name, handle: TextIO) -> pd.DataFrame:
        """Write set data"""
        self._write_out_dataframe(self.filepath, set_name, df)

    def _footer(self, handle: TextIO):
        pass


class WriteDatapackage(WriteCsv):
    def _header(self) -> Any:
        os.makedirs(os.path.join(self.filepath, "data"), exist_ok=True)
        return None

    def _write_out_dataframe(self, folder, parameter, df):
        """Writes out a dataframe as a csv into the data subfolder of a datapackage

        Arguments
        ---------
        folder : str
        parameter : str
        df : pandas.DataFrame

        """
        filepath = os.path.join(folder, "data", parameter + ".csv")
        with open(filepath, "w") as csvfile:
            logger.info(
                "Writing %s rows into narrow file for %s", df.shape[0], parameter
            )
            df.to_csv(csvfile, index=False)

    def _footer(self, handle: TextIO):
        datapackage = read_packaged_file("datapackage.json", "otoole.preprocess")
        filepath = os.path.join(self.filepath, "datapackage.json")
        with open(filepath, "w") as destination:
            destination.writelines(datapackage)
        self._write_default_values()

    def _write_default_values(self):

        default_values_path = os.path.join(self.filepath, "data", "default_values.csv")
        with open(default_values_path, "w") as csv_file:
            csv_file.write("name,default_value\n")

            for name, contents in self.config.items():
                if contents["type"] == "param":
                    csv_file.write("{},{}\n".format(name, contents["default"]))
