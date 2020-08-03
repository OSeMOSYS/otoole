import logging
from typing import TextIO

import pandas as pd

from otoole.input import WriteStrategy
from otoole.preprocess.excel_to_osemosys import CSV_TO_EXCEL

logger = logging.getLogger(__name__)


class WriteExcel(WriteStrategy):
    def _header(self):
        return pd.ExcelWriter(self.datafilepath, mode="w")

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
                logger.debug("Rows: {}; columns: {}; values: {}", rows, columns, values)
                logger.debug("dtypes: {}".format(df.dtypes))
                pivot = pd.pivot_table(
                    df, index=rows, columns=columns, values=values, fill_value=default
                )
            elif len(names) == 2:
                logger.debug("Two columns for {}: {}".format(parameter_name, names))
                values = names[-1]
                rows = names[0:-2]
                logger.debug("Rows: {}; values: {}", rows, values)
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
        filepath = open(self.datafilepath, "w")
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
