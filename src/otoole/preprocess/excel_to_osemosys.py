#!/usr/bin/env python
# coding: utf-8
"""
Extract data from Excel spreadsheets (.xls and .xlsx)
Import the csv file that I want as an output, need to convert the xls format to csv format
To create the csv outputs (per sheet) in a folder called CSV files
"""
import csv
import os
import sys

import xlrd


def main(input_workbook, output_file, output_folder='CSVFiles'):
    """Creates a model file from an Excel workbook containing OSeMOSYS data
    """
    work_book = xlrd.open_workbook(os.path.join(input_workbook))

    csv_from_excel(work_book, output_folder)

    # I create a txt file - string that contains the csv files
    fileOutput = parseCSVFilesAndConvert(sheet_names)
    with open(output_file, "w") as text_file:
        text_file.write(fileOutput)
        text_file.write("end;\n")

    work_book.release_resources()  # release the workbook-resources
    del work_book

def csv_from_excel(workbook, output_folder):
    """Creates csv files from all sheets in a workbook

    Arguments
    ---------
    workbook :
    output_folder : str
    """
    # Create all the csv files in a new folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # creates the csv folder

    # Iterate over each sheet in the workbook
    for sheet in workbook.sheets():  # typing: xlrd.book.Sheet

        name = sheet.name
        modified_name = modified_name([name])

        # Open the sheet name in the xlsx file and write it in csv format]
        filepath = os.path.join(output_folder, modified_name[0] + '.csv')
        with open(filepath, 'w', newline='') as your_csv_file:
            wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

            for rownum in range(sheet.nrows):  # reads each row in the csv file
                row = cast_to_integer(sheet.row_values(rownum))
                wr.writerow(row)

def cast_to_integer(row):
    """function to convert all float numbers to integers....need to check it!!
    """
    if all(isinstance(n, float) for n in row):
        converted_row = list(map(int, sh.row_values(rownum)))
    else:
        converted_row = row
    return converted_row


# for loop pou trexei ola ta sheet name kai paragei to format se csv
def parseCSVFilesAndConvert(original_sheet_names):
    """
    """

    sheet_names = modifyNames(original_sheet_names)

    result = ''
    for i in range(len(sheet_names)):
        # 8 #all the     parameters thad do not have variables
        if (sheet_names[i] in ['STORAGE', 'EMISSION', 'MODE_OF_OPERATION',
                              'REGION', 'FUEL', 'TIMESLICE', 'TECHNOLOGY',
                              'YEAR']):
            result += 'set ' + sheet_names[i] + ' := '
            with open('CSVFiles/' + sheet_names[i] + '.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    result += " ".join(row) + " "
                result += ";\n"
        # 24 #all the parameters that have one variable
        elif (sheet_names[i] in ['AccumulatedAnnualDemand', 'CapitalCost',
                                'FixedCost', 'ResidualCapacity',
                                'SpecifiedAnnualDemand',
                                'TotalAnnualMinCapacity',
                                'TotalAnnualMinCapacityInvestment',
                                'TotalTechnologyAnnualActivityLowerLimit']):
            result += 'param ' + sheet_names[i] + ' default 0 := '
            result += '\n[REGION, *, *]:\n'
            result += insert_table(sheet_names[i])
        # 24 #all the parameters that have one variable
        elif (sheet_names[i] in ['TotalAnnualMaxCapacityInvestment']):
            result += 'param ' + sheet_names[i] + ' default 99999 := '
            result += '\n[REGION, *, *]:\n'
            result += insert_table(sheet_names[i])
        elif (sheet_names[i] in ['AvailabilityFactor']):
            result += 'param ' + sheet_names[i] + ' default 1 := '
            result += '\n[REGION, *, *]:\n'
            result += insert_table(sheet_names[i])
        elif (sheet_names[i] in ['TotalAnnualMaxCapacity',
                                'TotalTechnologyAnnualActivityUpperLimit']):
            result += 'param ' + sheet_names[i] + ' default 9999999 := '
            result += '\n[REGION, *, *]:\n'
            result += insert_table(sheet_names[i])
        elif (sheet_names[i] in ['AnnualEmissionLimit']):
            result += 'param ' + sheet_names[i] + ' default 99999 := '
            result += '\n[REGION, *, *]:\n'
            result += insert_table(sheet_names[i])
        elif (sheet_names[i] in ['YearSplit']):
            result += 'param ' + sheet_names[i] + ' default 0 :\n'
            result += insert_table(sheet_names[i])
        elif (sheet_names[i] in ['CapacityOfOneTechnologyUnit',
                                'EmissionsPenalty', 'REMinProductionTarget',
                                'RETagFuel', 'RETagTechnology',
                                'ReserveMargin', 'ReserveMarginTagFuel',
                                'ReserveMarginTagTechnology', 'TradeRoute']):
            result += 'param ' + sheet_names[i] + ' default 0 := ;\n'
        # 3 #all the parameters that have 2 variables
        elif (sheet_names[i] in ['SpecifiedDemandProfile']):
            result += 'param ' + sheet_names[i] + ' default 0 := \n'
            result += insert_two_variables(sheet_names, i)
        # 3 #all the parameters that have 2 variables
        elif (sheet_names[i] in ['VariableCost']):
            result += 'param ' + sheet_names[i] + ' default 9999999 := \n'
            result += insert_two_variables(sheet_names, i)
        # 3 #all the parameters that have 2 variables
        elif (sheet_names[i] in ['CapacityFactor']):
            result += 'param ' + sheet_names[i] + ' default 1 := \n'
            result += insert_two_variables(sheet_names, i)
        # 3 #all the parameters that have 3     variables
        elif (sheet_names[i] in ['EmissionActivityRatio', 'InputActivityRatio',
                                'OutputActivityRatio']):
            result += 'param ' + sheet_names[i] + ' default 0 := \n'
            with open('CSVFiles/' + sheet_names[i] + '.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                newRow = next(reader)
                newRow.pop(0)
                newRow.pop(0)
                newRow.pop(0)
                year = newRow.copy()
                for row in reader:
                    result += '[REGION, ' + \
                        row.pop(0) + ', ' + row.pop(0) + ', *, *]:'
                    result += '\n'
                    result += " ".join(year) + " "
                    result += ':=\n'
                    result += " ".join(row) + " "
                    result += '\n'
                result += ';\n'
        # 8 #all the parameters that do not have variables
        elif (sheet_names[i] in ['TotalTechnologyModelPeriodActivityUpperLimit']):
            result += 'param ' + sheet_names[i] + ' default 9999999 : \n'
            result += insert_no_variables(sheet_names, i)
        elif (sheet_names[i] in ['CapacityToActivityUnit']):
            result += 'param ' + sheet_names[i] + ' default 1 : \n'
            result += insert_no_variables(sheet_names, i)
        # 8 #all the parameters that do not have variables
        elif (sheet_names[i] in ['TotalTechnologyAnnualActivityLowerLimit']):
            result += 'param ' + sheet_names[i] + ' default 0 := \n'
            result += insert_no_variables(sheet_names, i)
        # 8 #all the parameters that do not have variables
        elif (sheet_names[i] in ['ModelPeriodEmissionLimit']):
            result += 'param ' + sheet_names[i] + ' default 999999 := ;\n'
        # 8 #all the   parameters   that do not have variables
        elif (sheet_names[i] in ['ModelPeriodExogenousEmission', 'AnnualExogenousEmission', 'OperationalLifeStorage']):
            result += 'param ' + sheet_names[i] + ' default 0 := ;\n'
        elif (sheet_names[i] in []):  # 8 #all the parameters that do not have variables
            result += 'param ' + sheet_names[i] + ' default 0 := ;\n'
        # 8 #all the parameters that do not have variables
        elif (sheet_names[i] in ['TotalTechnologyModelPeriodActivityLowerLimit']):
            result += 'param ' + sheet_names[i] + ' default 0 := ;\n'
        # 8 #all the parameters that do not have variables
        elif (sheet_names[i] in ['DepreciationMethod']):
            result += 'param ' + sheet_names[i] + ' default 1 := ;\n'
        # 8 #all the parameters that do not have variables
        elif (sheet_names[i] in ['OperationalLife']):
            result += 'param ' + sheet_names[i] + ' default 1 : \n'
            result += insert_no_variables(sheet_names, i)
        elif (sheet_names[i] in ['DiscountRate']):  # default value
            with open('CSVFiles/' + sheet_names[i] + '.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    result += 'param ' + sheet_names[i] + ' default 0.1 := ;\n'
    return result


def insert_no_variables(sheet_names, i):
    result = ""
    with open('CSVFiles/' + sheet_names[i] + '.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        firstColumn = []
        secondColumn = []
        secondColumn.append('REGION')
        for row in reader:
            firstColumn.append(row[0])
            secondColumn.append(row[1])
        result += " ".join(firstColumn) + ' '
        result += ':=\n'
        result += " ".join(secondColumn) + ' '
        result += ';\n'
    return result


def insert_two_variables(sheet_names, i):
    result = ""
    with open('CSVFiles/' + sheet_names[i] + '.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        newRow = next(reader)
        newRow.pop(0)
        newRow.pop(0)
        year = newRow.copy()
        for row in reader:
            result += '[REGION, ' + row.pop(0) + ', *, *]:'
            result += '\n'
            result += " ".join(year) + " "
            result += ':=\n'
            result += " ".join(row) + " "
            result += '\n'
        result += ';\n'
    return result


def insert_table(name):
    result = ""
    with open('CSVFiles/' + name + '.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        newRow = next(reader)
        newRow.pop(0)  # removes the first element of the row
        result += " ".join(newRow) + " "
        result += ':=\n'
        for row in reader:
            result += " ".join(row) + " "
            result += '\n'
        result += ';\n'
    return result


def modifyNames(sheet_names):
    """I change the name of the sheets in the xlsx file to match with the csv
    actual ones
    """
    modifiedNames = sheet_names.copy()
    for i in range(len(modifiedNames)):
        if (modifiedNames[i] == "TotalAnnualMaxCapacityInvestmen"):
            modifiedNames[i] = "TotalAnnualMaxCapacityInvestment"
        elif (modifiedNames[i] == "TotalAnnualMinCapacityInvestmen"):
            modifiedNames[i] = "TotalAnnualMinCapacityInvestment"
        elif (modifiedNames[i] == "TotalTechnologyAnnualActivityLo"):
            modifiedNames[i] = "TotalTechnologyAnnualActivityLowerLimit"
        elif (modifiedNames[i] == "TotalTechnologyAnnualActivityUp"):
            modifiedNames[i] = "TotalTechnologyAnnualActivityUpperLimit"
        elif (modifiedNames[i] == "TotalTechnologyModelPeriodActLo"):
            modifiedNames[i] = "TotalTechnologyModelPeriodActivityLowerLimit"
        elif (modifiedNames[i] == "TotalTechnologyModelPeriodActUp"):
            modifiedNames[i] = "TotalTechnologyModelPeriodActivityUpperLimit"
    return modifiedNames


if __name__ == '__main__':
    if len(sys.argv) != 3:
        msg = "Usage: python {} <workbook_filename> <output_filepath>"
        print(msg.format(sys.argv[0]))
        sys.exit(1)
    else:
        try:
            main(sys.argv[1], sys.argv[2])
        except:
            sys.exit(1)
