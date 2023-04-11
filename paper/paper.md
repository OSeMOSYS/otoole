---
title: 'otoole: OSeMOSYS Tools for Energy Work'
tags:
  - python
  - energy
  - energy-system
  - energy-system-modelling
  - osemosys
authors:
  - name: Trevor Barnes
    orcid: 0000-0003-2458-2968
    equal-contrib: true
    corresponding: true
    affiliation: 1
  - name: Will Usher
    orcid: 0000-0001-9367-1791
    equal-contrib: true
    affiliation: 2
affiliations:
 - name: School of Sustainable Energy Engineering, Simon Fraser University, Vancouver, Canada
   index: 1
 - name: Energy Technology, KTH Royal Institute of Technology, Stockholm, Sweden
   index: 2
date: 11 April 2023
bibliography: paper.bib
---

# Summary

Data handling for energy system optimisation models is a necessary but tedious task. Depending on the workflow, user skill level, and model implementation, the data interfacing requirements can be significantly different. OSeMOSYS Tools for Energy Work, or otoole is a Python package providing OSeMOSYS energy modellers with options to use different input data formats, visualize and validate input data, and process result data. otoole exposes three different input data formats and structures to the user, can process results from three popular solvers, and is designed to be modular and extensible to enable interoperability between OSeMOSYS models developed in different programming languages.

# Statement of need

The Open Source energy MOdelling SYStem, or OSeMOSYS [@howells2011], is a highly cited and reputable open-source framework for conducting long-term energy system planning studies. The original, and still highly used, implementation of OSeMOSYS is formulated in the mathematical programming language, [GNU MathProg](https://github.com/OSeMOSYS/OSeMOSYS_GNU_MathProg). While MathProg[@GNULinearProgramming2012] is open-source, fitting with the ethos of OSeMOSYS, it requires all data to be stored in a single large and unwieldy text file. This results in data edits being tedious, error-prone, and difficult to integrate into automated workflows. Furthermore, model result files are often difficult to interface with unless processing work is performed first. The OSeMOSYS formulation has also been implemented in [PuLP]( https://github.com/OSeMOSYS/OSeMOSYS_PuLP), [Pyomo](https://github.com/OSeMOSYS/OSeMOSYS_Pyomo), [Julia JUMP](https://github.com/sei-international/NemoMod.jl) and [GAMS](https://github.com/OSeMOSYS/OSeMOSYS_GAMS). A software gap exists to provide OSeMOSYS modellers with an easy way to work with different input data formats and process result files.

otoole supports three different input file formats: wide-format Excel files (pivoted on the year index), long-format CSV files, and GNU MathProg files. With otoole, users can convert between any of these formats to meet their skill level and workflow requirements. Furthermore, otoole can process result solution files from the open-source solver CBC [@forrest2022], and the commercial solvers Gurobi and CPLEX, into tabulated CSV results.

Additionally, otoole can visualize and validate input data. Through the visualization function, users can create a reference energy system from their input data (Figure 1); this is a common step in energy modelling where a schematic is used to visualize the energy flow. Moreover, if the input data follows a standardized naming scheme, the user can validate input data to quickly identify improperly named technologies and commodities and ensure energy flow paths are complete.


![otoole Reference Energy System Example. \label{fig:Reference Energy System}](images/res.png)

# Publications

The development of otoole was originally mentioned in [@niet2021] through discussion on how to consolidate and standardize scripts and data formats within the OSeMOSYS community. Since then, otoole has grown and been implemented in various published research projects. A pedagogical paper on conducting global sensitivity analysis in the context of energy systems [@usher2023] uses otoole to convert data for hundreds of simultaneous model runs automatically. OSeMOSYS Global [@barnes2022], an open-source global electricity system model generator, uses otoole in its workflow to programmatically create unique OSeMOSYS models based on user inputs. Finally, [@Ramos2022] uses otoole in a paper discussing how to use OSeMOSYS to perform climate, land, energy, and water system modelling.

# Extendability

While otoole was originally created to assist MathProg OSeMOSYS modellers, its functionality can easily extend to other implementations of OSeMOSYS and any workflow that uses non-OSeMOSYS MathProg data files.

otoole follows a strategy-based software design pattern. Two abstract base classes define how otoole reads and writes data, respectively named ReadStrategy and WriteStrategy. The ReadStrategy reads model data or results data into an internal data structure (currently a dictionary of pandas DataFrames). The WriteStrategy writes out data to a format specified by the user. The ReadResults abstract class is responsible for calculating intermediate results if required. A schematic of this design pattern is shown in Figure 2.

![otoole Design Pattern. \label{fig:otoole}](images/class-diagram.png)

The advantage of designing otoole around a strategy pattern is that it allows for the easy addition of new file formats and model implementations. For example, there are existing OSeMOSYS implementations written in Python and GAMS, and new implementations may be created in the future. New reading and writing classes can easily add data conversion into and out of these formats. This is especially useful for benchmarking each implementation against one another to check for inconsistencies, measure performance, or to migrate OSeMOSYS models from one format to another. This same extensibility logic applies to the reading of results. For example, adding support for the new open-source solver HiGHS [@huangfu2018] can be implemented simply through a new class that inherits from ReadResults and implements reading logic specific to HiGHS.

When converting between formats, the user supplies otoole with a configuration file that describes the parameters, sets, and variables in the model. This allows otoole to work with any version of OSeMOSYS regardless of the parameters, variables, or sets. This is particularly useful for extensions of OSeMOSYS, such of the Climate, Land, Energy, and Water framework [@bazilian2011], which adds parameters to OSeMOSYS to include other energy sectors. Moreover, describing the model through a configuration file allows otoole to work with any MathProg model file; not just OSeMOSYS models.

# Installation and Example

otoole is [deployed](https://pypi.org/project/otoole/) to the Python Packaging Index (PyPI) and can be installed via pip

```bash
pip install otoole
```
A sample repository, titled [Simplicity](https://github.com/OSeMOSYS/simplicity), holds a simple sample OSeMOSYS model to demonstrate the functionalities of otoole. Instructions on the core functions of otoole, in addition to full examples, can be found on under the [documentation site]( https://otoole.readthedocs.io/en/latest/).


# References
