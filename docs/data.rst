.. _dataformats:

============
Data Formats
============

This page explains the different data formatting options available in otoole. Firstly,
the format of the user configuration file is explained. Following this, the different
input data formats are explained.

.. SEEALSO::
   See the Simplicity_ repository for a full example of these formats

User Configuration File
-----------------------

.. versionadded:: v1.0.0
    The user configuration file is now required for data conversion

Overview
~~~~~~~~

Most commands in ``otoole`` require the user to specify a configuration file that describes
the ``parameters``, ``sets``, and ``results`` in the model. This configuration file is
written in ``yaml`` and is typically saved as ``config.yaml``. This section will cover how to
format the user configuration file. If the user incorrectly enters data, validation checks in
``otoole`` should catch this.

Information Required
~~~~~~~~~~~~~~~~~~~~

The table below highlights what information is required for each ``Set``,
``Parameter`` and ``Result`` definition in the configuration file. Required values are
given by **X**, while optional values are given by **(X)**.

+-------------+------+------------+---------+
|             | Set  | Parameter  | Result  |
+=============+======+============+=========+
| name        | X    | X          | X       |
+-------------+------+------------+---------+
| short_name  | (X\) | (X\)       | (X\)    |
+-------------+------+------------+---------+
| dtype       | X    | X          | X       |
+-------------+------+------------+---------+
| type        | X    | X          | X       |
+-------------+------+------------+---------+
| default     |      | X          | X       |
+-------------+------+------------+---------+

.. deprecated:: v1.0.3
    The ``Calculated`` keyword is no longer needed for Result definitions

.. WARNING::
   Names longer than 31 characters require a ``short_name`` field. This is due
   to character limits on excel sheet names. ``otoole`` will raise an error if a
   ``short_name`` is not provided in these instances.

Sets Format
~~~~~~~~~~~

Sets are defined as follows::

    SETNAME:
        short_name: SET (Optional)
        dtype: "int" or "string"
        type: set

.. NOTE::
   It's convention in OSeMOSYS to capitalize set names

Parameters Format
~~~~~~~~~~~~~~~~~

Parameters are defined as follows. When referencing set indices use the full
name, **not** the ``short_name``::

    ParameterName:
        short_name: ParamName (Optional)
        indices: [SETNAME, SETNAME, ...]
        type: param
        dtype: "int" or "float"
        default: 0

.. NOTE::
   It's convention in OSeMOSYS to use Pascal case for parameter names

Results Format
~~~~~~~~~~~~~~

Results are defined as follows. When referencing set indices use the full
name, **not** the ``short_name``::

    AnnualEmissions:
        short_name: ParamName (Optional)
        indices: [SETNAME, SETNAME, ...]
        type: result
        dtype: "int" or "float"
        default: 0

.. NOTE::
   It's convention in OSeMOSYS to use Pascal case for result names

Examples
~~~~~~~~

Below are examples of correctly formatted configuration file values. See the Simplicity_
repository for a complete example.

1. Set definition of ``TECHNOLOGY``::

    TECHNOLOGY:
        dtype: str
        type: set

2. Parameter definition of ``AccumulatedAnnualDemand``::

    AccumulatedAnnualDemand:
        short_name: AccAnnualDemand
        indices: [REGION,FUEL,YEAR]
        type: param
        dtype: float
        default: 0

3. Result definition of ``AnnualEmissions``::

    AnnualEmissions:
        indices: [REGION,EMISSION,YEAR]
        type: result
        dtype: float
        default: 0

.. TIP::
   See the :ref:`examples` page to create a template configuration file

Input Data
----------

.. deprecated:: v1.0.0
    The ``datapackage`` format is no longer supported

Overview
~~~~~~~~

This section will describe how to format data for ``excel``, ``csv``, and ``datafile``
formats.

Excel
~~~~~

Interfacing with ``otoole`` through excel is a very user-friendly method to handle OSeMOSYS
input data. In the excel workbook (an ``*.xlsx`` file), each sheet will correspond to a
single parameter or set. Parameters that are indexed over years are pivoted on the ``YEAR``
index. This creates a wide formatted dataset, where each year is the column header, with
the first columns holding the remaining indices.

For example, referencing the Simplicity_ model, the ``AccumulatedAnnualDemand`` parameter
data will be under the ``AccumulatedAnnualDemand`` sheet and contain the data

+-------------+-------------+---------+---------+---------+---------+---------+---------+---------+
| REGION      | TECHNOLOGY  | 2014    | 2015    | 2016    | 2017    | 2018    | 2019    | 2020    |
+=============+=============+=========+=========+=========+=========+=========+=========+=========+
| SIMPLICITY  | BACKSTOP1   | 999999  | 999999  | 999999  | 999999  | 999999  | 999999  | 999999  |
+-------------+-------------+---------+---------+---------+---------+---------+---------+---------+
| SIMPLICITY  | BACKSTOP2   | 999999  | 999999  | 999999  | 999999  | 999999  | 999999  | 999999  |
+-------------+-------------+---------+---------+---------+---------+---------+---------+---------+
| SIMPLICITY  | ETHPLANT    | 25      | 25      | 25      | 25      | 25      | 25      | 25      |
+-------------+-------------+---------+---------+---------+---------+---------+---------+---------+
| SIMPLICITY  | GRID_EXP    | 4000    | 4000    | 4000    | 4000    | 4000    | 4000    | 4000    |
+-------------+-------------+---------+---------+---------+---------+---------+---------+---------+
| SIMPLICITY  | HYD1        | 4500    | 4500    | 4500    | 4500    | 4500    | 4500    | 4500    |
+-------------+-------------+---------+---------+---------+---------+---------+---------+---------+
| SIMPLICITY  | HYD2        | 3500    | 3500    | 3500    | 3500    | 3500    | 3500    | 3500    |
+-------------+-------------+---------+---------+---------+---------+---------+---------+---------+
| ...         | ...         | ...     | ...     | ...     | ...     | ...     | ...     | ...     |
+-------------+-------------+---------+---------+---------+---------+---------+---------+---------+

Parameters that are not indexed over years will have an extra column titled ``VALUE``.
This column will hold the input value for that parameter. For example, the
``OperationalLife`` parameter in the Simplicity_ example will be formatted
as shown

+-------------+-----------------+--------+
| REGION      | TECHNOLOGY      | VALUE  |
+=============+=================+========+
| SIMPLICITY  | BACKSTOP1       | 1      |
+-------------+-----------------+--------+
| SIMPLICITY  | BACKSTOP2       | 1      |
+-------------+-----------------+--------+
| SIMPLICITY  | ETHPLANT        | 30     |
+-------------+-----------------+--------+
| SIMPLICITY  | GAS_EXTRACTION  | 1      |
+-------------+-----------------+--------+
| SIMPLICITY  | GAS_IMPORT      | 1      |
+-------------+-----------------+--------+
| SIMPLICITY  | GRID_EXP        | 50     |
+-------------+-----------------+--------+
| SIMPLICITY  | HYD1            | 80     |
+-------------+-----------------+--------+
| SIMPLICITY  | HYD2            | 80     |
+-------------+-----------------+--------+
| ...         | ...             | ...    |
+-------------+-----------------+--------+

Set definitions will have a single column, titled ``VALUE``. For example, the set
``TECHNOLOGY`` will be formatted as shown

+-----------------+
| VALUE           |
+=================+
| BACKSTOP1       |
+-----------------+
| BACKSTOP2       |
+-----------------+
| ETHPLANT        |
+-----------------+
| GAS_EXTRACTION  |
+-----------------+
| GAS_IMPORT      |
+-----------------+
| GRID_EXP        |
+-----------------+
| HYD1            |
+-----------------+
| HYD2            |
+-----------------+
| ...             |
+-----------------+

CSV
~~~

Interfacing with ``otoole`` through a folder of CSV files is the most "computer friendly"
way to handle input data. This is due to csv files being easy to read and write, and
independent of the program, programming language, and operating system. This allows
``otoole`` to easily integrate into workflows.

When working with CSV data, all parameters and sets are saved under their name given in the
configuration file, and nested in a single directory. CSV data will follow long formatting
standards, where each column is the name of the index, and the final column is titled
``VALUE``.

For example, the following data for ``AccumulatedAnnualDemand`` will be under
the file ``data/AccumulatedAnnualDemand.csv``

+-------------+---------+-------+--------+
| REGION      | FUEL    | YEAR  | VALUE  |
+=============+=========+=======+========+
| SIMPLICITY  | ETH     | 2014  | 1      |
+-------------+---------+-------+--------+
| SIMPLICITY  | RAWSUG  | 2014  | 0.5    |
+-------------+---------+-------+--------+
| SIMPLICITY  | ETH     | 2015  | 1.03   |
+-------------+---------+-------+--------+
| SIMPLICITY  | RAWSUG  | 2015  | 0.51   |
+-------------+---------+-------+--------+
| SIMPLICITY  | ETH     | 2016  | 1.061  |
+-------------+---------+-------+--------+
| SIMPLICITY  | RAWSUG  | 2016  | 0.519  |
+-------------+---------+-------+--------+
| SIMPLICITY  | ETH     | 2017  | 1.093  |
+-------------+---------+-------+--------+
| SIMPLICITY  | RAWSUG  | 2017  | 0.529  |
+-------------+---------+-------+--------+
| SIMPLICITY  | ETH     | 2018  | 1.126  |
+-------------+---------+-------+--------+
| ...         | ...     | ...   | ...    |
+-------------+---------+-------+--------+

While the ``TECHNOLOGY`` set data will be under the file ``data/TECHNOLOGY.csv``` and
formatted as shown with a single ``VALUE`` column.

+-----------------+
| VALUE           |
+=================+
| BACKSTOP1       |
+-----------------+
| BACKSTOP2       |
+-----------------+
| ETHPLANT        |
+-----------------+
| GAS_EXTRACTION  |
+-----------------+
| GAS_IMPORT      |
+-----------------+
| GRID_EXP        |
+-----------------+
| HYD1            |
+-----------------+
| HYD2            |
+-----------------+
| ...             |
+-----------------+

Datafile
~~~~~~~~

Datafiles are the least user-friendly method of handling data, however, they are required
for the OSeMOSYS GNU MathProg version of OSeMOSYS. Datafiles are written in MathProg_, which
shares syntax with the AMPL_ programming language.

Datafiles contain all model data in one file (often a ``*.txt`` file), and will follow
a similar data standard to long formatted CSV data. However, the default value for the
parameter is included in its declaration statement.

For example, in the file ``data.txt``, the parameter ``AccumulatedAnnualDemand`` will
be defined as follows::

    param default 0.0 : AccumulatedAnnualDemand :=
        SIMPLICITY ETH 2014 1
        SIMPLICITY RAWSUG 2014 0.5
        SIMPLICITY ETH 2015 1.03
        SIMPLICITY RAWSUG 2015 0.51
        SIMPLICITY ETH 2016 1.061
        SIMPLICITY RAWSUG 2016 0.519
        SIMPLICITY ETH 2017 1.093
        SIMPLICITY RAWSUG 2017 0.529
        SIMPLICITY ETH 2018 1.126
        SIMPLICITY RAWSUG 2018 0.538
        SIMPLICITY ETH 2019 1.159
        SIMPLICITY RAWSUG 2019 0.548
        SIMPLICITY ETH 2020 1.194
        SIMPLICITY RAWSUG 2020 0.558
        ...

And in the same ``data.txt`` file, the set ``TECHNOLOGY`` will be defined as follows::

    set TECHNOLOGY :=
        BACKSTOP1
        BACKSTOP2
        ETHPLANT
        GAS_EXTRACTION
        GAS_IMPORT
        GRID_EXP
        HYD1
        HYD2
        ...

.. SEEALSO::
   For reading and writing between Python and AMPL_, see the amply_ Python package.

.. _MathProg: https://en.wikibooks.org/wiki/GLPK/GMPL_(MathProg)
.. _AMPL: https://ampl.com/
.. _amply: https://github.com/willu47/amply
.. _Simplicity: https://github.com/OSeMOSYS/simplicity
