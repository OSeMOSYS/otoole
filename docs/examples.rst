.. _examples:

--------
Examples
--------

This page will present example to show the full functionality of ``otoole``.
To follow these examples, clone the Simplicity_ repository and run all commands
from the ``simplicity/`` directory.

Example One
-----------

Objective
~~~~~~~~~

Use a folder of CSV data to build and solve an OSeMOSYS model with CBC. Generate the full
suite of results and visualize the referecne energy system.

Step One: ``otoole`` Convert
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We first want to convert the folder of Simplicity_ CSVs (``data/``) into
an OSeMOSYS datafile (``simplicity.txt``)::

    $ otoole convert csv datafile data simplicity.txt config.yaml

Step Two: Build the Model
~~~~~~~~~~~~~~~~~~~~~~~~~
Use GLPK_ to build the model and save it as ``simplicity.lp``::

    $ glpsol -m osemosys.txt -d simplicity.txt --wlp simplicity.lp --check

.. TIP::
    See the `GLPK Wiki`_ for more information on the ``glpsol`` command

Step Three: Solve the Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use CBC_ to solve the model and save the solution file as ``simplicity.sol``::

    $ cbc simplicity.lp solve -solu simplicity.sol

Step Four: Generate the full set of results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create a folder to hold the results::

    $ mkdir results

Use ``otoole``'s ``result`` package to generate the results file::

    $ otoole results cbc csv simplicity.sol results config.yaml

Step Five: Visualise the Reference Energy System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use ``otoole``'s ``vis`` package to generate the RES::

    $ otoole vis res simplicity.txt res.png

.. image:: _static/simplicity_res.png

Example Two
-----------

Objective
~~~~~~~~~

Use an excel worksheet to build and solve an OSeMOSYS model with CPLEX. Only
generate the results for ``TotalDiscountedCost`` and ``TotalCapacityAnnual``.

Step One: ``otoole`` Convert
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We first want to convert the excel workbook (``simplicity.xlsx``) into
an OSeMOSYS datafile (``simplicity.txt```)::

    $ otoole convert excel datafile data simplicity.xlsx config.yaml

Step Two: Build the Model
~~~~~~~~~~~~~~~~~~~~~~~~~
Use GLPK_ to build the model and save it as ``simplicity.lp``::

    $ glpsol -m osemosys.txt -d simplicity.txt --wlp simplicity.lp --check

Step Three: Solve the Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use CPLEX_ to solve the model and save the solution file as ``simplicity.sol``::

    $ cplex -c "read simplicity.sol" "optimize" "write simplicity.sol"

Step Four: Modify the Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Change the ``calcualted`` fields for the ``TotalDiscountedCost`` and ``TotalCapacityAnnual``
values to ``True``, and set all other ``calcualted`` filds to ``False``::

    TotalCapacityAnnual:
        indices: [REGION, TECHNOLOGY, YEAR]
        type: result
        dtype: float
        default: 0
        calculated: True

Step Five: Generate the selected results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create a folder to hold the results::

    $ mkdir results

Sort the solution file::

    $ simplicity.sol sort > simplicity_sorted.sol

Use ``otoole``'s ``result`` package to generate the result CSVs::

    $ otoole results cplex csv simplicity_sorted.sol results config.yaml

.. _Simplicity: https://github.com/OSeMOSYS/simplicity
.. _GLPK: https://www.gnu.org/software/glpk/
.. _GLPK Wiki: https://en.wikibooks.org/wiki/GLPK/Using_GLPSOL
.. _CBC: https://github.com/coin-or/Cbc
.. _CPLEX: https://www.ibm.com/products/ilog-cplex-optimization-studio/cplex-optimizer
