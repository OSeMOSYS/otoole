#!/usr/bin/env python
# coding: utf-8
"""Extract data from spreadsheets and write to an OSeMOSYS datafile

"""
import csv
import logging
import os
import sys

import pandas as pd
import xlrd

logger = logging.getLogger(__name__)


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
            result += _insert_variables(contents, 2)
        # all the parameters that have 2 variables
        elif (sheet_name in ['VariableCost']):
            result += 'param ' + sheet_name + ' default 9999999 := \n'
            result += _insert_variables(contents, 2)
        # all the parameters that have 2 variables
        elif (sheet_name in ['CapacityFactor']):
            result += 'param ' + sheet_name + ' default 1 := \n'
            result += _insert_variables(contents, 2)
        # all the parameters that have 3 variables
        elif (sheet_name in ['EmissionActivityRatio', 'InputActivityRatio',
                             'OutputActivityRatio']):
            result += 'param ' + sheet_name + ' default 0 := \n'
            result += _insert_variables(contents, 3)
        # 8 #all the parameters that do not have variables
        elif (sheet_name in ['TotalTechnologyModelPeriodActivityUpperLimit']):
            result += 'param ' + sheet_name + ' default 9999999 : \n'
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
        elif (sheet_name in ['ModelPeriodExogenousEmission', 'AnnualExogenousEmission', 'OperationalLifeStorage']):
            result += 'param ' + sheet_name + ' default 0 :=\n'
            result += _insert_variables(contents, 1)
        elif (sheet_name in []):  # 8 #all the parameters that do not have variables
            result += 'param ' + sheet_name + ' default 0 := ;\n'
        # 8 #all the parameters that do not have variables
        elif (sheet_name in ['TotalTechnologyModelPeriodActivityLowerLimit']):
            result += 'param ' + sheet_name + ' default 0 := ;\n'
        # 8 #all the parameters that do not have variables
        elif (sheet_name in ['DepreciationMethod']):
            result += 'param ' + sheet_name + ' default 1 := ;\n'
        # 8 #all the parameters that do not have variables
        elif (sheet_name in ['OperationalLife']):
            result += 'param ' + sheet_name + ' default 1 : \n'
            result += _insert_no_variables(contents)
        elif (sheet_name in ['DiscountRate']):  # default value
            for row in contents:
                result += 'param ' + sheet_name + ' default 0.1 := ;\n'
        else:
            logger.debug("No code found for parameter %s", sheet_name)
    return result


def _insert_no_variables(data):

    result = ""

    if data:
        df = pd.DataFrame(data[1:])
        df = df.T

        table = df.values

        result += " ".join([str(x) for x in table[0]]) + ':=\n'
        result += "SIMPLICITY " + " ".join([str(x) for x in table[1]]) + '\n;\n'

    return result


def _insert_variables(contents: list, number_indices: int):
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
            result += '= [SIMPLICITY, *, *]:\n'

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
