#!/usr/bin/env python
# coding: utf-8
"""Extract data from spreadsheets and write to an OSeMOSYS datafile

Reads and writes the following OSeMOSYS parameters and sets to and from
files on disk.

Notes
=====

Sets
----
These are the standard sets::

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

All sets are written in a CSV file in one column of values with header of ``VALUE``.
For example, the CSV file for set YEAR::

    VALUE
    2015
    2016
    2017
    2018
    2019
    2020

Sets are written into the OSeMOSYS data file using the following syntax::

    set YEAR := 2014 2015 2016 2017 2018 2019 2020 ;


Parameters
----------
In general, parameters can be written into CSV files in narrow or wide
formats. In narrow format, the CSV file should look as follows::

    REGION,TIMESLICE,YEAR,VALUE
    SIMPLICITY,ID,2014,0.1667
    SIMPLICITY,IN,2014,0.0833
    SIMPLICITY,SD,2014,0.1667
    SIMPLICITY,SN,2014,0.0833
    SIMPLICITY,WD,2014,0.3333
    SIMPLICITY,WN,2014,0.1667


In wide format, the final index is transposed::

    REGION,TIMESLICE,2014,2015,...
    SIMPLICITY,ID,0.1667,0.1667
    SIMPLICITY,IN,0.0833,0.0833
    SIMPLICITY,SD,0.1667,0.1667
    SIMPLICITY,SN,0.0833,0.0833
    SIMPLICITY,WD,0.3333,0.3333
    SIMPLICITY,WN,0.1667,0.1667

Wide format is a bit nicer to use with spreadsheets,
as it allows you to more easily plot graphs of values, but narrow
format is a more flexible and easily manipulated data format.

Writing parameteters:

1-dimensional e.g. DiscountRate{r in REGION}

2-dimension e.g. YearSplit{l in TIMESLICE, y in YEAR}

n-dimensional e.g. DaysInDayType{ls in SEASON, ld in DAYTYPE, y in YEAR}


Global parameters::

    param YearSplit{l in TIMESLICE, y in YEAR};
    param DiscountRate{r in REGION};
    param DaySplit{lh in DAILYTIMEBRACKET, y in YEAR};
    param Conversionls{l in TIMESLICE, ls in SEASON};
    param Conversionld{l in TIMESLICE, ld in DAYTYPE};
    param Conversionlh{l in TIMESLICE, lh in DAILYTIMEBRACKET};
    param DaysInDayType{ls in SEASON, ld in DAYTYPE, y in YEAR};
    param TradeRoute{r in REGION, rr in REGION, f in FUEL, y in YEAR};
    param DepreciationMethod{r in REGION};


Demand parameters::

    param SpecifiedAnnualDemand{r in REGION, f in FUEL, y in YEAR};
    param SpecifiedDemandProfile{r in REGION, f in FUEL, l in TIMESLICE, y in YEAR};
    param AccumulatedAnnualDemand{r in REGION, f in FUEL, y in YEAR};


Performance parameters::

    param CapacityToActivityUnit{r in REGION, t in TECHNOLOGY};
    param TechWithCapacityNeededToMeetPeakTS{r in REGION, t in TECHNOLOGY};
    param CapacityFactor{r in REGION, t in TECHNOLOGY, l in TIMESLICE, y in YEAR};
    param AvailabilityFactor{r in REGION, t in TECHNOLOGY, y in YEAR};
    param OperationalLife{r in REGION, t in TECHNOLOGY};
    param ResidualCapacity{r in REGION, t in TECHNOLOGY, y in YEAR};
    param InputActivityRatio{r in REGION, t in TECHNOLOGY, f in FUEL, m in MODE_OF_OPERATION, y in YEAR};
    param OutputActivityRatio{r in REGION, t in TECHNOLOGY, f in FUEL, m in MODE_OF_OPERATION, y in YEAR};


Technology Costs parameters::

    param CapitalCost{r in REGION, t in TECHNOLOGY, y in YEAR};
    param VariableCost{r in REGION, t in TECHNOLOGY, m in MODE_OF_OPERATION, y in YEAR};
    param FixedCost{r in REGION, t in TECHNOLOGY, y in YEAR};


Storage parameters::

    param TechnologyToStorage{r in REGION, t in TECHNOLOGY, s in STORAGE, m in MODE_OF_OPERATION};
    param TechnologyFromStorage{r in REGION, t in TECHNOLOGY, s in STORAGE, m in MODE_OF_OPERATION};
    param StorageLevelStart{r in REGION, s in STORAGE};
    param StorageMaxChargeRate{r in REGION, s in STORAGE};
    param StorageMaxDischargeRate{r in REGION, s in STORAGE};
    param MinStorageCharge{r in REGION, s in STORAGE, y in YEAR};
    param OperationalLifeStorage{r in REGION, s in STORAGE};
    param CapitalCostStorage{r in REGION, s in STORAGE, y in YEAR};
    param ResidualStorageCapacity{r in REGION, s in STORAGE, y in YEAR};


Capacity Constraints parameters::

    param CapacityOfOneTechnologyUnit{r in REGION, t in TECHNOLOGY, y in YEAR};
    param TotalAnnualMaxCapacity{r in REGION, t in TECHNOLOGY, y in YEAR};
    param TotalAnnualMinCapacity{r in REGION, t in TECHNOLOGY, y in YEAR};


Investment Constraints parameters::

    param TotalAnnualMaxCapacityInvestment{r in REGION, t in TECHNOLOGY, y in YEAR};
    param TotalAnnualMinCapacityInvestment{r in REGION, t in TECHNOLOGY, y in YEAR};


Activity Constraints parameters::

    param TotalTechnologyAnnualActivityUpperLimit{r in REGION, t in TECHNOLOGY, y in YEAR};
    param TotalTechnologyAnnualActivityLowerLimit{r in REGION, t in TECHNOLOGY, y in YEAR};
    param TotalTechnologyModelPeriodActivityUpperLimit{r in REGION, t in TECHNOLOGY};
    param TotalTechnologyModelPeriodActivityLowerLimit{r in REGION, t in TECHNOLOGY};


Reserve Margin parameters::

    param ReserveMarginTagTechnology{r in REGION, t in TECHNOLOGY, y in YEAR};
    param ReserveMarginTagFuel{r in REGION, f in FUEL, y in YEAR};
    param ReserveMargin{r in REGION, y in YEAR};


RE Generation Target parameters::

    param RETagTechnology{r in REGION, t in TECHNOLOGY, y in YEAR};
    param RETagFuel{r in REGION, f in FUEL, y in YEAR};
    param REMinProductionTarget{r in REGION, y in YEAR};


Emissions & Penalties parameters::

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
from typing import Dict, List

import xlrd

from otoole import read_packaged_file

logger = logging.getLogger(__name__)


def read_config(path_to_user_config: str = None) -> Dict:
    """Reads the config file holding expected OSeMOSYS set and parameter dimensions

    Arguments
    ---------
    path_to_user_config : str, optional, default=None
        Optional path to a user defined configuration file

    Returns
    -------
    dict
    """
    if path_to_user_config:
        config = read_packaged_file(path_to_user_config, None)
    else:
        config = read_packaged_file('config.yaml', 'otoole.preprocess')
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


def _modify_names(sheet_names: List) -> List:
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


def _cast_to_integer(row):
    """function to convert all float numbers to integers....need to check it!!
    """
    if all(isinstance(n, float) for n in row):
        converted_row = list(map(int, row))
    else:
        converted_row = row
    return converted_row
