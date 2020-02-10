.. include:: ../README.rst

Getting Started
===============

Install ``otoole`` using pip::

    pip install otoole

Check the version installed::

    otoole -V

Read an online OSeMOSYS datapackage and convert it to a modelfile::

    otoole convert datapackage datafile https://zenodo.org/record/3479823/files/KTH-dESA/simplicity-v0.1a0.zip simplicity.txt

Visualise the Reference Energy System::

    otoole viz res https://zenodo.org/record/3479823/files/KTH-dESA/simplicity-v0.1a0.zip res.png && open res.png

Convert an OSeMOSYS datafile to a datapackage::

    otoole convert datafile datapackage simplicity.txt simplicity

Validate the names of technologies and fuels against the standard
naming convention and identify isolated fuels, emissions and
technologies::

    otoole validate datapackage simplicity/datapackage.json


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
