===========
whey-conda
===========

.. start short_desc

**Whey extension for creating Conda packages for Python projects.**

.. end short_desc


.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |actions_linux| |actions_windows| |actions_macos| |coveralls|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Anaconda
	  - |conda-version| |conda-platform|
	* - Activity
	  - |commits-latest| |commits-since| |maintained| |pypi-downloads|
	* - QA
	  - |codefactor| |actions_flake8| |actions_mypy|
	* - Other
	  - |license| |language| |requires|

.. |docs| image:: https://img.shields.io/readthedocs/whey-conda/latest?logo=read-the-docs
	:target: https://whey-conda.readthedocs.io/en/latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/repo-helper/whey-conda/workflows/Docs%20Check/badge.svg
	:target: https://github.com/repo-helper/whey-conda/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |actions_linux| image:: https://github.com/repo-helper/whey-conda/workflows/Linux/badge.svg
	:target: https://github.com/repo-helper/whey-conda/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/repo-helper/whey-conda/workflows/Windows/badge.svg
	:target: https://github.com/repo-helper/whey-conda/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/repo-helper/whey-conda/workflows/macOS/badge.svg
	:target: https://github.com/repo-helper/whey-conda/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status

.. |actions_flake8| image:: https://github.com/repo-helper/whey-conda/workflows/Flake8/badge.svg
	:target: https://github.com/repo-helper/whey-conda/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/repo-helper/whey-conda/workflows/mypy/badge.svg
	:target: https://github.com/repo-helper/whey-conda/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://requires.io/github/repo-helper/whey-conda/requirements.svg?branch=master
	:target: https://requires.io/github/repo-helper/whey-conda/requirements/?branch=master
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/repo-helper/whey-conda/master?logo=coveralls
	:target: https://coveralls.io/github/repo-helper/whey-conda?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/repo-helper/whey-conda?logo=codefactor
	:target: https://www.codefactor.io/repository/github/repo-helper/whey-conda
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/whey-conda
	:target: https://pypi.org/project/whey-conda/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/whey-conda?logo=python&logoColor=white
	:target: https://pypi.org/project/whey-conda/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/whey-conda
	:target: https://pypi.org/project/whey-conda/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/whey-conda
	:target: https://pypi.org/project/whey-conda/
	:alt: PyPI - Wheel

.. |conda-version| image:: https://img.shields.io/conda/v/domdfcoding/whey-conda?logo=anaconda
	:target: https://anaconda.org/domdfcoding/whey-conda
	:alt: Conda - Package Version

.. |conda-platform| image:: https://img.shields.io/conda/pn/domdfcoding/whey-conda?label=conda%7Cplatform
	:target: https://anaconda.org/domdfcoding/whey-conda
	:alt: Conda - Platform

.. |license| image:: https://img.shields.io/github/license/repo-helper/whey-conda
	:target: https://github.com/repo-helper/whey-conda/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/repo-helper/whey-conda
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/repo-helper/whey-conda/v0.1.1
	:target: https://github.com/repo-helper/whey-conda/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/repo-helper/whey-conda
	:target: https://github.com/repo-helper/whey-conda/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2021
	:alt: Maintenance

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/whey-conda
	:target: https://pypi.org/project/whey-conda/
	:alt: PyPI - Downloads

.. end shields

Installation
--------------

.. start installation

``whey-conda`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install whey-conda

To install with ``conda``:

	* First add the required channels

	.. code-block:: bash

		$ conda config --add channels https://conda.anaconda.org/conda-forge
		$ conda config --add channels https://conda.anaconda.org/domdfcoding

	* Then install

	.. code-block:: bash

		$ conda install whey-conda

.. end installation

-----

To enable ``whey-conda``, add the following lines to your ``pyproject.toml`` file:

.. code-block:: TOML

	[tool.whey.builders]
	binary = "whey_conda"

The ``whey-conda``-specific configuration is defined in the ``tool.whey-conda`` table.
See `the documentation`_ for more details.

.. _the documentation: https://whey-conda.readthedocs.io/en/latest/
