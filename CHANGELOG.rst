=========
Changelog
=========

Version 1.1.4
=============
- Add result calculations for ``DiscountedCapitalInvestment``, ``DiscountedCostByTechnology``, and ``DiscountedOperationalCost``
- Add result calculations for ``CapitalInvestmentStorage``, ``DiscountedCapitalInvestmentStorage``, ``DiscountedCostByStorage`` and ``DiscountedSalvageValueStorage``
- Correct ``TotalDiscountedCost`` calculation to account for storage costs

Version 1.1.3
===========================
- Lock pandas to 2.1.4 or later
- Capital Investment result calculation fixed
- Defults expansion moved to ReadStrategy
- Adds Python 3.12 support
- Add HiGHS as a solver

Version 1.1.2
=============
- Update zenodo metadata for JOSS

Version 1.1.1
=============
- Fixes CPLEX result processing docs
- Added joss status badge to readme
- Fix Tests on Windows
- Update graphviz install instructions

Version 1.1.0
=============
- Public Python API added to call otoole directly in Python files
- ReadCplex directly reads in CPLEX solution files. Drops the need to transform and sort solution files
- ReadGlpk class added to process GLPK solution files
- Update to Pydantic v2.0
- ReadResultsCbc renamed to ReadWideResults
- Model validation instructions updated in documentation
- The ``--input_datafile`` argument is deprecated, and the user now must supply the input data to process results
- Locks pandas to <2.1

Version 1.0.4
=============
- Fixed issue with pydantic v2.0.0
- Dropped support for Python 3.8. Otoole now requires Python 3.9 or later

Version 1.0.3
=============
- Improved error message for multiple names mismatches
- Fix for excel pivoting bug (issue 171)
- Fix data type casting issue for floats to ints (issue 167)
- Deprecates calculated field for Result definitions in config file (issue 173)
- Minor documentation updates

Version 1.0.2
=============
- Fix of pandas version in setup.cfg

Version 1.0.1
=============
- Updates to citation file
- Relink to coveralls
- Upgrade to pandas 2.0
- Add issue and PR templates
- Add reading checks between config file and input data

Version 1.0.0
=============
- Requires explicit provision of a user-defined configuration file for otoole to workbook
- Deprecates datapackage fuctionality
- Adds setup command to generate template config.yaml and csv files
- Documentation update
- Bumped pyscaffold to 4.2
- Otoole now requires Python 3.8 or later

Version 0.11.0
==============
- Foundation for user defined configuration
- Fix for issue #101
- Better writing of floating point numbers as text

Version 0.10.0
==============
- Adds support for OSeMOSYS v1.0, Gurobi and CBC

Version 0.9
===========
- Adds support for processing Gurobi solution files
- Better handling of datatypes when converting datapackages
- Fixing bugs on Windows where empty lines were written out during conversion to datapackage

Version 0.8
===========
- Behind-the-scenes reorganisation of code to use `ReadStrategies` and `WriteStrategies`
  pattern. This enables much cleaner structuring of the code and more reusability of
  modular blocks.
- Updates to documentation with clearer explaination of how to perform conversions
- Otoole now requires Python 3.7 or later
- Harmonisation of results and pre-processing using the strategies mentioned above
- Bugfixes for #61, #63, #65, #70

Version 0.7
===========
- Adds results processing and conversion of results
- CBC results are transformed into a folder of CSV files
- Missing intermediate results parameters are automatically generated
- Adds command ``otoole results cbc csv simplicity.sol ./results --input_datafile simplicity.txt``
- Removes dependency upon PuLP now that amply is available separately on PyPi
- Fixed bug with parameter names >31 characters in converting to Excel and fixed round trip
- Added conversions from Excel to datafile and datapackage to avoid intermediate commands so
  ``otoole convert excel datapackage <> <>`` and ``otoole convert excel datafile <> <>``
  are both now legal

Version 0.6
===========
- Fixes bug in writing to datafile where any values that matched the default were
  ignored
- Adds CLI command to convert to Excel from datapackage e.g.
  ``otoole convert datapackage excel <datapackage.json> <to.xlsx>``
- Uses black code style and uses mypy and black for syntax checking and formatting

Version 0.5
===========
- Add validation of names and fuels in datapackage
  - Adds ``validate`` command to the command-line interface
  - Define a validation config as a YAML file for names

Version 0.4
===========
- Tidy up the command line interface
- Convert to/from SQLite database from/to datapackage
- Remove rotten pygraphviz dependency

Version 0.3
===========

- Create a Tabular Data Package from an OSeMOSYS datafile

Version 0.2
===========

- Visualise a reference energy system from a Tabular Data Package

Version 0.1
===========

- Add CPLEX to csv or CBC solution file conversion script
- Create CSV files in a folder from an excel workbook
- Create a Tabular Data Package from a folder of CSVs
- Create an OSeMOSYS datafile from a Tabular Data Package
- Adds a command line interface to access these tools
