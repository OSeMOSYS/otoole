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
for users of OSeMOSYS.The aim of the package is to provide commonly used pre-
and post-processing steps for OSeMOSYS.

.. image:: img/osemosys_dataflow.png

**otoole** aims to support different ways of storing input data and results,
including csv files, databases, datapackages and Excel workbooks,
as well as different implementations of the OSeMOSYS model.
This improves interoperability of analyses and
generally makes life a little bit easier.

Installation
============

``otoole`` can be installed through ``pip``::

    pip install otoole

For instructions of the use of the tool, run the command line help function::

    otoole --help

Documentation
=============
A more detailed documentation of otoole can be found here:
https://otoole.readthedocs.io/en/stable/index.html

Contributing
============

New ideas and bugs `should be submitted: <https://github.com/OSeMOSYS/otoole/issues/new>`_
to the repository Issue Tracker. Please do contribute by discussing and developing these
ideas further, or by developing the codebase.

To contribute directly to the documentation of code development, you
first need to install the package in *develop mode*::

    git clone http://github.com/OSeMOSYS/otoole
    cd otoole
    git checkout <branch you wish to use>
    python setup.py develop

Alternatively, use pip to install otoole from git in editable mode

    pip install -e git+http://github.com/OSeMOSYS/otoole@master#egg=otoole

Now, all changes made in the codebase will automatically be reflected
in the installed Python version accessible on the command line or from
importing otoole modules into other Python packages.
