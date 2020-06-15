=========
Changelog
=========

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
