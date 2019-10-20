======
otoole
======

**otoole** is a Python package which provides a command-line interface
for users of OSeMOSYS.

The aim of the package is to provide a community resource which
centralises the commonly used pre- and post-processing steps
around the use of OSeMOSYS.

.. image:: img/osemosys_dataflow.png

**otoole** aims to support different ways of storing input data and results,
including csv files, databases, datapackages and Excel workbooks,
as well as different implementations of the OSeMOSYS model.

Getting Started
===============

Install ``otoole`` using pip::

    pip install otoole

Download an OSeMOSYS datapackage and convert it to a modelfile::

    otoole prep datafile https://zenodo.org/record/3479823/files/KTH-dESA/simplicity-v0.1a0.zip ./simplicity.txt

Visualise the Reference Energy System::

    otoole viz res https://zenodo.org/record/3479823/files/KTH-dESA/simplicity-v0.1a0.zip res.png && open res.png

Run OSeMOSYS with the modelfile and place the results in a folder::

    otoole run --modelfile simplicity.txt --datapackage results

Contents
========

.. toctree::
   :maxdepth: 2

   License <license>
   Authors <authors>
   Changelog <changelog>
   Module Reference <api/modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _toctree: http://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
.. _reStructuredText: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _references: http://www.sphinx-doc.org/en/stable/markup/inline.html
.. _Python domain syntax: http://sphinx-doc.org/domains.html#the-python-domain
.. _Sphinx: http://www.sphinx-doc.org/
.. _Python: http://docs.python.org/
.. _Numpy: http://docs.scipy.org/doc/numpy
.. _SciPy: http://docs.scipy.org/doc/scipy/reference/
.. _matplotlib: https://matplotlib.org/contents.html#
.. _Pandas: http://pandas.pydata.org/pandas-docs/stable
.. _Scikit-Learn: http://scikit-learn.org/stable
.. _autodoc: http://www.sphinx-doc.org/en/stable/ext/autodoc.html
.. _Google style: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings
.. _NumPy style: https://numpydoc.readthedocs.io/en/latest/format.html
.. _classical style: http://www.sphinx-doc.org/en/stable/domains.html#info-field-lists
