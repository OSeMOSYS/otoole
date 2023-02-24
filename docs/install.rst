.. _install:

===============
Getting Started
===============

Installation
------------
Install ``otoole`` using pip::

    pip install otoole

Check the version installed::

    ~ otoole -V
    1.0.0

To upgrade ``otoole`` using pip::

    pip install otoole --upgrade

.. TIP::
   We recommend installing ``otoole`` in an isolated virtual environment, either through
   the use of venv_ or conda_

Dependencies
------------

``otoole`` relies on a number of dependencies. If the user wants to download the
individual dependencies, the easiest way to do this is through miniconda_.

1. Obtain the miniconda_ package
2. Add the ``conda-forge`` channel ``conda config --add channels conda-forge``
3. Create a new Python environment
   ``conda create -n otoole python>3.7 networkx pandas graphviz=2.46.1 xlrd pydantic``
4. Activate the new environment ``conda activate otoole``
5. Use pip to install otoole ``pip install otoole``

.. _venv: https://docs.python.org/3/library/venv.html#module-venv
.. _conda: https://docs.conda.io/en/latest/miniconda.html
.. _miniconda: https://docs.conda.io/en/latest/miniconda.html
