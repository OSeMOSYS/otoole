.. _functionality:

Introduction
------------

*otoole* is a command-line tool written in Python. By writing commands in a terminal
window, you can tell *otoole* to perform certain tedious tasks for you to turbo-charge
your OSeMOSYS modelling.

Initially, *otoole* only supports the GNU MathProg version of OSeMOSYS. We hope to build
support for other implementations of OSeMOSYS soon. In fact, this is one of the key aims
of *otoole* - to better link the various OSeMOSYS communities and their implementations
through common data standards and useful scripts and tools that we can work on together.

Core Functionality
------------------

.. image:: img/osemosys_dataflow.png

As shown in the diagram, *otoole* deals primarily with data before and after OSeMOSYS.
We call the data work upto the generation of a datafile which is read in by GLPK
pre-processing.  Anything that happens with the immediate outputs of a solver, such as
the recommended open-source solvers GLPK, CBC, or the proprietary solvers CPLEX and Gurobi,
is called results and post-processing. You can find more information in the sections below.

Pre-processing
~~~~~~~~~~~~~~

*otoole* supports many data pre-processing conversions so as to ease the tasks of
the OSeMOSYS modeller.

At the centre of *otoole*'s recommended workflow is the use of the Tabular DataPackage
format (referred to as a ``datapackage`` to store the data for a model.
However, it is not required to use the datapackage format,
and instead *otoole* can be used to, for example,
convert an Excel workbook into a GNU MathProg datafile ready for processing with GLPK.
Note, however, that often the datapackage is used as a min-way conversion point for more
complex format transformations.

*otoole* currently supports conversion between the following formats:

- Excel
- Tabular DataPackage
- a folder of CSV files (identical to a datapackage, but without the metadata file)
- GNU MathProg datafile

Results and Post-processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

*otoole* currently supports three versions of GNU MathProg OSeMOSYS
- the long, short and fast versions.

The long version includes all results as variables within the formulation,
so the `otoole results` command parses a solvers solution file (e.g. CBC),
extracts the required variables, and produces a folder of CSV files containing the results.

The short and fast versions omit a large number of these calculated result variables
so as to speed up the model matrix generation and solution times.
As of PR #40 *otoole* now supports the majority of these calculated results so as to match
those produced by the long version of the code.
