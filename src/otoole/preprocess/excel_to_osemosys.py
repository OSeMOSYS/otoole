#!/usr/bin/env python
# coding: utf-8
"""Extract data from spreadsheets and write to an OSeMOSYS datafile

Reads and writes the following OSeMOSYS parameters and sets to and from
files on disk.

Notes
=====

Sets
~~~~
set YEAR;
set TECHNOLOGY;
set TIMESLICE;
set FUEL;
set EMISSION;
set MODE_OF_OPERATION;
set REGION;
set SEASON;
set DAYTYPE;
set DAILYTIMEBRACKET;
set FLEXIBLEDEMANDTYPE;
set STORAGE;

All sets are written in a CSV file in one column of values with no header.
For example, the CSV file for set YEAR::

    2015
    2016
    2017
    2018
    2019
    2020

Sets are written into the OSeMOSYS data file using the following syntax::

    set YEAR := 2014 2015 2016 2017 2018 2019 2020 ;

Parameters
~~~~~~~~~~

In general, parameters can be written into CSV files in narrow or wide
formats. In narrow format, the CSV file should look as follows::

    TIMESLICE,YEAR,VALUE
    ID,2014,0.1667
    IN,2014,0.0833
    SD,2014,0.1667
    SN,2014,0.0833
    WD,2014,0.3333
    WN,2014,0.1667

In wide format, the final index is transposed::

    TIMESLICE,2014,2015,...
    ID,0.1667,0.1667
    IN,0.0833,0.0833
    SD,0.1667,0.1667
    SN,0.0833,0.0833
    WD,0.3333,0.3333
    WN,0.1667,0.1667

Wide format is a bit nicer to use with spreadsheets,
as it allows you to more easily plot graphs of values, but narrow
format is a more flexible and easily manipulated data format.

Writing parameteters:

1-dimensional e.g. DiscountRate{r in REGION}

2-dimension e.g. YearSplit{l in TIMESLICE, y in YEAR}

n-dimensional e.g. DaysInDayType{ls in SEASON, ld in DAYTYPE, y in YEAR}



Global
------
param YearSplit{l in TIMESLICE, y in YEAR};
param DiscountRate{r in REGION};
param DaySplit{lh in DAILYTIMEBRACKET, y in YEAR};
param Conversionls{l in TIMESLICE, ls in SEASON};
param Conversionld{l in TIMESLICE, ld in DAYTYPE};
param Conversionlh{l in TIMESLICE, lh in DAILYTIMEBRACKET};
param DaysInDayType{ls in SEASON, ld in DAYTYPE, y in YEAR};
param TradeRoute{r in REGION, rr in REGION, f in FUEL, y in YEAR};
param DepreciationMethod{r in REGION};

Demands
-------
param SpecifiedAnnualDemand{r in REGION, f in FUEL, y in YEAR};
param SpecifiedDemandProfile{r in REGION, f in FUEL, l in TIMESLICE, y in YEAR};
param AccumulatedAnnualDemand{r in REGION, f in FUEL, y in YEAR};

Performance
-----------

param CapacityToActivityUnit{r in REGION, t in TECHNOLOGY};
param TechWithCapacityNeededToMeetPeakTS{r in REGION, t in TECHNOLOGY};
param CapacityFactor{r in REGION, t in TECHNOLOGY, l in TIMESLICE, y in YEAR};
param AvailabilityFactor{r in REGION, t in TECHNOLOGY, y in YEAR};
param OperationalLife{r in REGION, t in TECHNOLOGY};
param ResidualCapacity{r in REGION, t in TECHNOLOGY, y in YEAR};
param InputActivityRatio{r in REGION, t in TECHNOLOGY, f in FUEL, m in MODE_OF_OPERATION, y in YEAR};
param OutputActivityRatio{r in REGION, t in TECHNOLOGY, f in FUEL, m in MODE_OF_OPERATION, y in YEAR};

Technology Costs
----------------
param CapitalCost{r in REGION, t in TECHNOLOGY, y in YEAR};
param VariableCost{r in REGION, t in TECHNOLOGY, m in MODE_OF_OPERATION, y in YEAR};
param FixedCost{r in REGION, t in TECHNOLOGY, y in YEAR};

Storage
-------
param TechnologyToStorage{r in REGION, t in TECHNOLOGY, s in STORAGE, m in MODE_OF_OPERATION};
param TechnologyFromStorage{r in REGION, t in TECHNOLOGY, s in STORAGE, m in MODE_OF_OPERATION};
param StorageLevelStart{r in REGION, s in STORAGE};
param StorageMaxChargeRate{r in REGION, s in STORAGE};
param StorageMaxDischargeRate{r in REGION, s in STORAGE};
param MinStorageCharge{r in REGION, s in STORAGE, y in YEAR};
param OperationalLifeStorage{r in REGION, s in STORAGE};
param CapitalCostStorage{r in REGION, s in STORAGE, y in YEAR};
param ResidualStorageCapacity{r in REGION, s in STORAGE, y in YEAR};

Capacity Constraints
--------------------
param CapacityOfOneTechnologyUnit{r in REGION, t in TECHNOLOGY, y in YEAR};
param TotalAnnualMaxCapacity{r in REGION, t in TECHNOLOGY, y in YEAR};
param TotalAnnualMinCapacity{r in REGION, t in TECHNOLOGY, y in YEAR};

Investment Constraints
----------------------
param TotalAnnualMaxCapacityInvestment{r in REGION, t in TECHNOLOGY, y in YEAR};
param TotalAnnualMinCapacityInvestment{r in REGION, t in TECHNOLOGY, y in YEAR};

Activity Constraints
--------------------
param TotalTechnologyAnnualActivityUpperLimit{r in REGION, t in TECHNOLOGY, y in YEAR};
param TotalTechnologyAnnualActivityLowerLimit{r in REGION, t in TECHNOLOGY, y in YEAR};
param TotalTechnologyModelPeriodActivityUpperLimit{r in REGION, t in TECHNOLOGY};
param TotalTechnologyModelPeriodActivityLowerLimit{r in REGION, t in TECHNOLOGY};

Reserve Margin
--------------
param ReserveMarginTagTechnology{r in REGION, t in TECHNOLOGY, y in YEAR};
param ReserveMarginTagFuel{r in REGION, f in FUEL, y in YEAR};
param ReserveMargin{r in REGION, y in YEAR};

RE Generation Target
--------------------
param RETagTechnology{r in REGION, t in TECHNOLOGY, y in YEAR};
param RETagFuel{r in REGION, f in FUEL, y in YEAR};
param REMinProductionTarget{r in REGION, y in YEAR};

Emissions & Penalties
---------------------
param EmissionActivityRatio{r in REGION, t in TECHNOLOGY, e in EMISSION, m in MODE_OF_OPERATION, y in YEAR};
param EmissionsPenalty{r in REGION, e in EMISSION, y in YEAR};
param AnnualExogenousEmission{r in REGION, e in EMISSION, y in YEAR};
param AnnualEmissionLimit{r in REGION, e in EMISSION, y in YEAR};
param ModelPeriodExogenousEmission{r in REGION, e in EMISSION};
param ModelPeriodEmissionLimit{r in REGION, e in EMISSION};


"""
import csv
import logging
import os
import sys

import pandas as pd
import xlrd
from yaml import SafeLoader, load

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources


logger = logging.getLogger(__name__)


def read_config():

    with pkg_resources.open_text('otoole.preprocess', 'config.yaml') as config_file:
        config = load(config_file, Loader=SafeLoader)
    return config


def generate_csv_from_excel(input_workbook, output_folder):
    """Generate a folder of CSV files from a spreadsheet

    Arguments
    ---------
    input_workbook : str
        Path to spreadsheet containing OSeMOSYS data
    output_folder : str
        Path of the folder containing the csv files

    """
    work_book = xlrd.open_workbook(os.path.join(input_workbook))

    _csv_from_excel(work_book, output_folder)
    work_book.release_resources()  # release the workbook-resources
    del work_book


def write_datafile(output_folder, output_file):
    """Create an OSeMOSYS datafile from a folder of CSV files

    Arguments
    ---------
    output_folder : str
        Path of the folder containing the csv files
    output_file
        Path to datafile to be written
    """
    sheet_names = [os.path.splitext(x)[0] for x in os.listdir(output_folder)]

    sorted_names = sorted(sheet_names)

    results = build_results_dictionary(sorted_names, output_folder)
    fileOutput = _build_result_string(results)
    with open(output_file, "w") as text_file:
        text_file.write(fileOutput)
        text_file.write("end;\n")


def main(input_workbook, output_file, output_folder):
    """Creates a model file from an Excel workbook containing OSeMOSYS data

    Arguments
    ---------
    input_workbook : str
        Path to spreadsheet containing OSeMOSYS data
    output_file
        Path to datafile to be written
    output_folder : str
        Path of the folder containing the csv files

    """
    generate_csv_from_excel(input_workbook, output_folder)
    write_datafile(output_folder, output_file)


def _csv_from_excel(workbook, output_folder):
    """Creates csv files from all sheets in a workbook

    Arguments
    ---------
    workbook :
    output_folder : str
    """

    logger.debug("Generating CSVs from Excel %s", workbook)
    # Create all the csv files in a new folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # creates the csv folder

    # Iterate over each sheet in the workbook
    for sheet in workbook.sheets():  # typing: xlrd.book.Sheet

        name = sheet.name
        mod_name = _modify_names([name])

        # Open the sheet name in the xlsx file and write it in csv format]
        filepath = os.path.join(output_folder, mod_name[0] + '.csv')
        with open(filepath, 'w', newline='') as your_csv_file:
            wr = csv.writer(your_csv_file, quoting=csv.QUOTE_NONNUMERIC)

            for rownum in range(sheet.nrows):  # reads each row in the csv file
                row = _cast_to_integer(sheet.row_values(rownum))
                wr.writerow(row)


def _cast_to_integer(row):
    """function to convert all float numbers to integers....need to check it!!
    """
    if all(isinstance(n, float) for n in row):
        converted_row = list(map(int, row))
    else:
        converted_row = row
    return converted_row


def read_file_into_memory(sheet_name, output_folder):
    filepath = os.path.join(output_folder, sheet_name + '.csv')
    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        return list(reader)


def build_results_dictionary(sheet_names, output_folder):
    results = dict()
    for sheet_name in sheet_names:

        results[sheet_name] = read_file_into_memory(sheet_name, output_folder)

    return results


def _build_result_string(results: dict):
    """Holds the logic for writing out model entities in a certain format
    """
    result = ''
    for sheet_name, contents in results.items():

        # all the sets
        if (sheet_name in ['DAYTYPE', 'DAILYTIMEBRACKET', 'STORAGE', 'EMISSION',
                           'MODE_OF_OPERATION', 'REGION', 'FUEL', 'TIMESLICE',
                           'SEASON', 'TECHNOLOGY', 'YEAR']):
            result += 'set ' + sheet_name + ' := '
            for row in contents:
                result += " ".join(row) + " "
            result += ";\n"
        # all the parameters that have one variable
        elif (sheet_name in ['AccumulatedAnnualDemand', 'CapitalCost',
                             'FixedCost', 'ResidualCapacity',
                             'SpecifiedAnnualDemand',
                             'TotalAnnualMinCapacity',
                             'TotalAnnualMinCapacityInvestment',
                             'TotalTechnologyAnnualActivityLowerLimit']):
            result += _insert_table(sheet_name, contents, default=0, region=True)
        # all the parameters that have one variable
        elif (sheet_name in ['TotalAnnualMaxCapacityInvestment']):
            result += _insert_table(sheet_name, contents, default=99999, region=True)
        elif (sheet_name in ['AvailabilityFactor']):
            result += _insert_table(sheet_name, contents, 1)
        elif (sheet_name in ['TotalAnnualMaxCapacity',
                             'TotalTechnologyAnnualActivityUpperLimit']):
            result += _insert_table(sheet_name, contents, default=999999, region=True)
        elif (sheet_name in ['AnnualEmissionLimit']):
            result += _insert_table(sheet_name, contents, default=99999, region=True)
        elif (sheet_name in ['YearSplit', 'CapacityOfOneTechnologyUnit', 'CapitalCostStorage']):
            result += _insert_table(sheet_name, contents, 0)
        elif (sheet_name in ['EmissionsPenalty', 'REMinProductionTarget',
                             'RETagFuel', 'RETagTechnology',
                             'ReserveMargin', 'ReserveMarginTagFuel',
                             'ReserveMarginTagTechnology', 'TradeRoute']):
            result += _insert_table(sheet_name, contents, default=0, region=True)
        # all the parameters that have 2 variables
        elif (sheet_name in ['SpecifiedDemandProfile']):
            result += 'param ' + sheet_name + ' default 0 := \n'
            result += _insert_parameter_table(contents, 2)
        # all the parameters that have 2 variables
        elif (sheet_name in ['VariableCost']):
            result += 'param ' + sheet_name + ' default 9999999 := \n'
            result += _insert_parameter_table(contents, 2)
        # all the parameters that have 2 variables
        elif (sheet_name in ['CapacityFactor']):
            result += 'param ' + sheet_name + ' default 1 := \n'
            result += _insert_parameter_table(contents, 2)
        # all the parameters that have 3 variables
        elif (sheet_name in ['EmissionActivityRatio', 'InputActivityRatio',
                             'OutputActivityRatio']):
            result += 'param ' + sheet_name + ' default 0 := \n'
            result += _insert_parameter_table(contents, 3)
        # 8 #all the parameters that do not have variables
        elif (sheet_name in ['TotalTechnologyModelPeriodActivityUpperLimit']):
            result += 'param ' + sheet_name + ' default 9999999 :'
            result += _insert_no_variables(contents)
        elif (sheet_name in ['CapacityToActivityUnit']):
            result += 'param ' + sheet_name + ' default 1 : \n'
            result += _insert_no_variables(contents)
        # 8 #all the parameters that do not have variables
        elif (sheet_name in ['TotalTechnologyAnnualActivityLowerLimit']):
            result += 'param ' + sheet_name + ' default 0 := \n'
            result += _insert_no_variables(contents)
        # 8 #all the parameters that do not have variables
        elif (sheet_name in ['ModelPeriodEmissionLimit']):
            result += 'param ' + sheet_name + ' default 999999 := ;\n'
        # 8 #all the   parameters   that do not have variables
        elif (sheet_name in ['ModelPeriodExogenousEmission', 'AnnualExogenousEmission']):
            result += 'param ' + sheet_name + ' default 0 :=\n'
            result += _insert_parameter_table(contents, 1)
        elif (sheet_name in []):  # 8 #all the parameters that do not have variables
            result += 'param ' + sheet_name + ' default 0 := ;\n'
        # 8 #all the parameters that do not have variables
        elif (sheet_name in ['TotalTechnologyModelPeriodActivityLowerLimit']):
            result += 'param ' + sheet_name + ' default 0 := ;\n'
        # 8 #all the parameters that do not have variables
        elif (sheet_name in ['DepreciationMethod']):
            result += 'param ' + sheet_name + ' default 1 := ;\n'
        # 8 #all the parameters that do not have variables
        elif (sheet_name in ['OperationalLife', 'OperationalLifeStorage']):
            result += 'param ' + sheet_name + ' default 1 :'
            result += _insert_no_variables(contents)
        elif (sheet_name in ['DiscountRate']):  # default value
            for row in contents:
                result += 'param ' + sheet_name + ' default 0.1 := ;\n'
        else:
            logger.debug("No code found for parameter %s", sheet_name)
    return result


def _insert_no_variables(data):

    result = ""

    if data[1:]:
        df = pd.DataFrame(data[1:])
        df = df.T

        table = df.values

        result += "\n" + " ".join([str(x) for x in table[0]]) + ':=\n'
        result += "SIMPLICITY " + " ".join([str(x) for x in table[1]]) + '\n'
    else:
        result += '=\n'
    result += ';\n'

    return result


def _insert_parameter_table(contents: list, number_indices: int):
    """

    Arguments
    ---------
    contents : list
    number_indices : int
    """
    result = ""

    if contents:
        header = contents[0]
        df = pd.DataFrame(data=contents[1:], columns=header)  # typing: pandas.DataFrame
        if number_indices > 1:
            index = header[:number_indices - 1]
            df = df.set_index(index)
        else:
            index = None
        year = [str(x) for x in header[number_indices:]]

        if index:
            for idx, data in df.groupby(level=list(range(number_indices - 1))):
                logging.debug("Index: %s\n data: %s\n", idx, data)
                if isinstance(idx, str):
                    idx = [idx]
                result += '[SIMPLICITY, ' + ", ".join([str(x) for x in idx]) + ', *, *]:\n'
                result += " ".join(year) + " :=\n"
                for row in data.values:
                    stringify = [str(x) for x in list(row)]
                    result += " ".join(stringify) + '\n'
        else:
            result += '[SIMPLICITY, *, *]:\n'
            result += " ".join(year) + " :=\n"
            for row in df.values:
                stringify = [str(x) for x in list(row)]
                result += " ".join(stringify) + '\n'
    result += ';\n'
    return result


def _insert_table(name, data, default: int = 999999, region: bool = False):
    result = 'param ' + name + ' default ' + str(default) + ' :=\n'
    if data:
        if region:
            result += '[SIMPLICITY, *, *]:\n'

        header = data[0]
        header.pop(0)  # removes the first element of the row
        result += " ".join(([str(x) for x in header])) + " "

        result += ':=\n'
        for row in data[1:]:
            result += " ".join([str(x) for x in row]) + '\n'
    result += ';\n'

    return result


def _modify_names(sheet_names):
    """I change the name of the sheets in the xlsx file to match with the csv
    actual ones
    """
    modifiedNames = sheet_names.copy()
    for name in modifiedNames:
        if (name == "TotalAnnualMaxCapacityInvestmen"):
            name = "TotalAnnualMaxCapacityInvestment"
        elif (name == "TotalAnnualMinCapacityInvestmen"):
            name = "TotalAnnualMinCapacityInvestment"
        elif (name == "TotalTechnologyAnnualActivityLo"):
            name = "TotalTechnologyAnnualActivityLowerLimit"
        elif (name == "TotalTechnologyAnnualActivityUp"):
            name = "TotalTechnologyAnnualActivityUpperLimit"
        elif (name == "TotalTechnologyModelPeriodActLo"):
            name = "TotalTechnologyModelPeriodActivityLowerLimit"
        elif (name == "TotalTechnologyModelPeriodActUp"):
            name = "TotalTechnologyModelPeriodActivityUpperLimit"
    return modifiedNames


if __name__ == '__main__':
    if len(sys.argv) != 3:
        msg = "Usage: python {} <workbook_filename> <output_filepath> <output_folder>"
        print(msg.format(sys.argv[0]))
        sys.exit(1)
    else:
        try:
            main(sys.argv[1], sys.argv[2], sys.argv[3])
        except:
            sys.exit(1)
