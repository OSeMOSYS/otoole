.. include:: ../README.rst

Getting Started
===============

Install ``otoole`` using pip::

    pip install otoole

Check the version installed::

    otoole -V

Download an OSeMOSYS datapackage and convert it to a modelfile::

    otoole convert datapackage datafile https://zenodo.org/record/3479823/files/KTH-dESA/simplicity-v0.1a0.zip simplicity.txt

Visualise the Reference Energy System::

    otoole viz res https://zenodo.org/record/3479823/files/KTH-dESA/simplicity-v0.1a0.zip res.png && open res.png

Alternatively, convert an OSeMOSYS datafile to a datapackage::

    otoole convert datafile datapackage simplicity.txt simplicity

Validate the names of technologies and fuels against the standard
naming convention and identify isolated fuels, emissions and
technologies::

    otoole validate datapackage https://zenodo.org/record/3479823/files/KTH-dESA/simplicity-v0.1a0.zip


Contents
========

.. toctree::
   :maxdepth: 2

   Core Functionality <functionality>
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
