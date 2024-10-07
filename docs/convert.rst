.. _convert:

==========
Python API
==========

otoole also provides a Python API to access all the features available from the command line tool.

Converting between formats
--------------------------

``otoole`` currently supports conversion between the following formats:

- Excel
- A folder of CSV files
- GNU MathProg datafile

>>> from otoole import convert
>>> convert('my_model.yaml', 'excel', 'csv', 'my_model.xlsx', 'my_model_csvs')

See :py:func:`otoole.convert.convert` for more details

Converting solver results to a folder of CSV files
--------------------------------------------------

The ``convert_results`` function creates a folder of CSV result files from a CBC_, CLP_, HiGHS_,
Gurobi_ or CPLEX_ solution file::

>>> from otoole import convert_results
>>> convert_results('my_model.yaml', 'cbc', 'csv', 'my_model.sol', 'my_model_csvs', 'datafile', 'my_model.dat')

See :func:`otoole.convert.convert_results` for more details

Reading solver results into a dict of Pandas DataFrames
-------------------------------------------------------

The ``read_results`` function reads a CBC_, CLP_, HiGHS_,
Gurobi_ or CPLEX_ solution file into memory::

>>> from otoole import read_results
>>> data, defaults = read_results('my_model.yaml', 'cbc', 'my_model.sol', 'datafile', 'my_model.dat')

See :func:`otoole.convert.read_results` for more details

Read in data from different Formats
-----------------------------------

You can use the :py:func:`otoole.convert.read` function to read data in from different formats to a Python object.
This allows you to then use all the features offered by Python to manipulate the data.

>>> from otoole import read
>>> data, defaults = read('my_model.yaml', 'csv', 'my_model_csvs') # read from a folder of csv files
>>> data, defaults = read('my_model.yaml', 'excel', 'my_model.xlsx') # read from an Excel file
>>> data, defaults = read('my_model.yaml', 'datafile', 'my_model.dat') # read from a GNU MathProg datafile

Write out data to different Formats
-----------------------------------

You can use the :py:func:`otoole.convert.write` function to write data out to different formats from a Python object.

>>> from otoole import read, write
>>> data, defaults = read('my_model.yaml', 'csv', 'my_model_csvs') # read from a folder of csv files
>>> write('my_model.yaml', 'excel', 'my_model.xlsx', data, defaults) # write to an Excel file
>>> write('my_model.yaml', 'datafile', 'my_model.dat', data, defaults) # write to a GNU MathProg datafile


.. _CBC: https://github.com/coin-or/Cbc
.. _CLP: https://github.com/coin-or/Clp
.. _CPLEX: https://www.ibm.com/products/ilog-cplex-optimization-studio/cplex-optimizer
.. _Gurobi: https://www.gurobi.com/
.. _HiGHS: https://ergo-code.github.io/HiGHS/dev/
