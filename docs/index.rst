.. include:: ../README.rst

Getting Started
===============

Install ``otoole`` using pip::

    pip install otoole

Check the version installed::

    otoole -V

Read an online OSeMOSYS datapackage and convert it to a modelfile::

    wget https://zenodo.org/record/3707794/files/OSeMOSYS/simplicity-v0.2.1.zip
    unzip simplicity-v0.2.1.zip -d simplicity
    otoole convert datapackage datafile simplicity/OSeMOSYS-simplicity-11a3a26/datapackage.json ./simplicity.txt

Visualise the Reference Energy System::

    otoole viz res https://zenodo.org/record/3707794/files/OSeMOSYS/simplicity-v0.2.1.zip res.png && open res.png

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
