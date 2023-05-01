==================================================
otoole: OSeMOSYS tools for energy work
==================================================

.. image:: https://coveralls.io/repos/github/OSeMOSYS/otoole/badge.svg?branch=master&kill_cache=1
    :target: https://coveralls.io/github/OSeMOSYS/otoole?branch=master

.. image:: https://readthedocs.org/projects/otoole/badge/?version=latest
    :target: https://otoole.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

A Python toolkit to support use of OSeMOSYS

Description
===========

OSeMOSYS tools for energy work, or otoole, is a Python package
which provides a command-line interface for users of OSeMOSYS. The aim of the
package is to provide commonly used pre- and post-processing steps for OSeMOSYS.

**otoole** aims to support different ways of storing input data and results,
including csv files and Excel workbooks, as well as different implementations
of the OSeMOSYS model. This improves interoperability of analyses and
generally makes life a little bit easier.

.. image:: docs/_static/workflow.png

Installation
============

``otoole`` can be installed through ``pip``::

    pip install otoole

For instructions of the use of the tool, run the command line help function::

    otoole --help

Documentation
=============
Detailed documentation of otoole, including examples, can be found here:
https://otoole.readthedocs.io/en/latest/

Contributing
============

New ideas and bugs `should be submitted <https://github.com/OSeMOSYS/otoole/issues/new>`_
to the repository issue tracker. Please do contribute by discussing and developing these
ideas further. To contribute directly to the documentation of code development, please see
the contribution guidelines document.
