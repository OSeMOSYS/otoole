.. _functionality:

==================
Core Functionality
==================

``otoole``'s functionality includes converting between data formats, processing
solution files, and visualising the model. These core functions are described on the page.
``otoole`` is a command-line tool. By writing commands in a terminal window,
you can tell ``otoole`` to perform certain tedious tasks for you to turbo-charge
your OSeMOSYS modelling.

As shown in the diagram, ``otoole`` deals primarily with data before and after OSeMOSYS.
Data work prior to the generation of a datafile, which is read in by GLPK_, is called
pre-processing. Anything that happens with the immediate outputs of a solver, such as
the recommended open-source solvers GLPK_, CBC_, or the proprietary solvers CPLEX_ and
Gurobi_, is called results and post-processing.

.. image:: _static/osemosys_dataflow.png

Configuration File
------------------

When performing any operation with ``otoole``, the user must supply a configuration
file. This file specifies what ``sets``, ``parameters``, and ``results`` are in the
model. The configuration file allows modellers to eaisly switch between
OSeMOSYS versions that may have different structures.

.. TIP::
    The :ref:`dataformats` page provides information on how to format the configuration file

Pre-processing
--------------

Overview
~~~~~~~~

``otoole`` supports many data pre-processing conversions so as to ease the tasks of
the OSeMOSYS modeller. The modeller can generate data in any one of the formats and
convert it to another format through a ``convert`` command. ``otoole`` currently supports
conversion between the following formats:

- Excel
- A folder of CSV files
- GNU MathProg datafile

``otoole convert``
~~~~~~~~~~~~~~~~~~

THe ``otoole convert``` command allows you to convert between various different
input formats::

    $ otoole convert --help
    usage: otoole convert [-h --write_defaults] {csv,datafile,excel} {csv,datafile,excel} from_path to_path config

    positional arguments:
    {csv,datafile,excel}  Input data format to convert from
    {csv,datafile,excel}  Input data format to convert to
    from_path             Path to file or folder to convert from
    to_path               Path to file or folder to convert to
    config                Path to config YAML file

    optional arguments:
    -h, --help            Show this help message and exit
    --write_defaults      Write default parameters values from configuration file

.. NOTE::
    The ``config`` positional argument is required from version 1.0 and onwards

.. TIP::
    The :ref:`dataformats` page provides information on how to structure input data

Examples
~~~~~~~~

The examples below showcase the ``convert`` functionality of ``otoole``. These are
examples only, and users are able to freely convert between datafile, csv, and
excel formats.

1. Convert from an existing OSeMOSYS datafile (``simplicity.txt``) to an excel
file (``simplicity.xlsx``)::

    $ otoole convert datafile excel simplicity.txt simplicity.xlsx config.yaml

2. Convert from a folder of csvs (``data``) to a datafile (``simplicity.txt``).
Within the folder ``data`` are csvs that contain data for each parameter and set::

    $ otoole convert csv datafile data simplicity.txt config.yaml

3. Convert from an excel file (``simplicity.xlsx``) to a folder of csvs (``data``)::

    $ otoole convert excel csv simplicity.xlsx data config.yaml

Post-processing
---------------

Overview
~~~~~~~~

With small OSeMOSYS models, it is normally fine to use the free open-source GLPK_ solver.
If you do, then OSeMOSYS will write out a full set of results as a folder of CSV files.
As you progress to larger models, the performance constraints of GLPK_ quickly become
apparent. CBC_ is an alternative open-source solver which offers better performance than
GLPK_ and can handle much larger models. However, CBC_ has no way of knowing how to write
out the CSV files you were used to dealing with when using GLPK_. ``otoole`` to the rescue!

``otoole`` currently supports using CBC_, CPLEX_ or Gurobi_ with all three versions of
GNU MathProg OSeMOSYS - the long, short and fast versions.

The long version includes all results as variables within the formulation, so the
``otoole results`` command parses the solution file, extracts the required variables,
and produces a folder of CSV files containing the results in an identical format
to if you had used GLPK_.

The short and fast versions omit a large number of these calculated result variables
so as to speed up the model matrix generation and solution times.

``otoole results``
~~~~~~~~~~~~~~~~~~

The ``results`` command creates a folder of CSV result files from a CBC, CLP, Gurobi or CPLEX
solution file::

    $ otoole results --help
    usage: otoole results [-h, --write_defaults] [--input_datafile INPUT_DATAFILE] {cbc,cplex} {csv} from_path to_path

    positional arguments:
    {cbc,cplex,gurobi}    Result data format to convert from
    {csv}                 Result data format to convert to
    from_path             Path to file or folder to convert from
    to_path               Path to file or folder to convert to

    optional arguments:
    -h, --help            Show this help message and exit
    --input_datafile INPUT_DATAFILE
                          Input GNUMathProg datafile required for OSeMOSYS short
                          or fast results
    --write_defaults      Write default result values from configuration file

Examples
~~~~~~~~

The example below showcase the ``result`` functionality of ``otoole``.

1. Generate a folder of CSV files from a CBC solution file::

    otoole results cbc csv simplicity.sol ./results --input_datafile simplicity.txt

.. WARNING::
    If using CPLEX_, note that you need to first sort the CPLEX file which you can do from
    the command line e.g. ``sort cplex.sol > cplex_sorted.sol``. See the :ref:`examples`
    page for a full CPLEX_ workflow

Visualization
-------------

Overview
~~~~~~~~
The visualization module in ``otoole`` allows you to visualise the reference energy system.
(with more visualisations to come!)

``otoole viz``
~~~~~~~~~~~~~~

The ``viz`` command allows you to visualise aspects of the model. Currently, only
visualising the reference energy system through the ``vis res`` command is supported::

    $ otoole viz res --help

    usage: otoole viz res [-h] datafile resfile

    positional arguments:
    datafile  Path to model datafile
    resfile   Path to reference energy system

    optional arguments:
    -h, --help   show this help message and exit

.. NOTE::
    The ``resfile`` command should include a file ending used for images,
    including ``bmp``, ``jpg``, ``pdf``, ``png`` etc. The ``graphviz`` library used to layout the
    reference energy system will interpret the file ending.

Examples
~~~~~~~~

1. Create a reference energy system of a model with an input datafile called
``simplicity.txt``. Save the diagram as ``res.png``::

    $ otoole viz res simplicity.txt res.png

.. image:: _static/simplicity_res.png

.. _GLPK: https://www.gnu.org/software/glpk/
.. _CBC: https://github.com/coin-or/Cbc
.. _CPLEX: https://www.ibm.com/products/ilog-cplex-optimization-studio/cplex-optimizer
.. _Gurobi: https://www.gurobi.com/"
