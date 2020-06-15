=======================================
otoole : OSeMOSYS tools for energy work
=======================================

.. image:: https://travis-ci.com/OSeMOSYS/otoole.svg?branch=master
    :target: https://travis-ci.com/OSeMOSYS/otoole

.. image:: https://coveralls.io/repos/github/OSeMOSYS/otoole/badge.svg?branch=master
    :target: https://coveralls.io/github/OSeMOSYS/otoole?branch=master

.. image:: https://readthedocs.org/projects/otoole/badge/?version=latest
    :target: https://otoole.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

A Python toolkit to support use of OSeMOSYS


Description
===========

**otoole** is a Python package which provides a command-line interface
for users of OSeMOSYS.

The aim of the package is to provide a community resource which
centralises the commonly used pre- and post-processing steps
around the use of OSeMOSYS.

.. image:: img/osemosys_dataflow.png

**otoole** aims to support different ways of storing input data and results,
including csv files, databases, datapackages and Excel workbooks,
as well as different implementations of the OSeMOSYS model.

Dependencies
------------

*otoole* requires a number of dependencies, including pygraphviz,
which can be difficult to install on Windows.

The easiest way to install the dependencies is to use miniconda.

1. Obtain the `miniconda package: <https://docs.conda.io/en/latest/miniconda.html>`_
2. Add the **conda-forge** channel ``conda config --add channels conda-forge``
3. Create a new Python environment
   ``conda create -n myenv python=3.7 networkx datapackage
   pandas graphviz xlrd``
4. Activate the new environment ``conda activate myenv``
5. Use pip to install otoole ``pip install otoole``


Installation
============

Install **otoole** using pip::

    pip install otoole


To upgrade **otoole** using pip::

    pip install otoole --upgrade


Usage
=====

For detailed instructions of the use of the tool, run the command line
help function::

    otoole --help


Contributing
============

New ideas and bugs are found on the repository Issue Tracker.
Please do contribute by discussing and developing these ideas further,
or by developing the codebase.

To contribute directly to the documentation of code development, you
first need to install the package in *develop mode*::

    git clone http://github.com/OSeMOSYS/otoole
    cd otoole
    git checkout <branch you wish to use>
    python setup.py develop

Now, all changes made in the codebase will automatically be reflected
in the installed Python version accessible on the command line or from
importing otoole modules into other Python packages.
