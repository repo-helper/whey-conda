=====================
Configuration
=====================

``whey-conda`` is configured in the ``pyproject.toml`` file defined in :pep:`517` and :pep:`518`.

.. seealso::

	The `whey documentation <https://whey.readthedocs.io/en/latest/configuration.html>`_
	contains instructions for configuring ``whey`` itself.

To enable ``whey-conda``, add the following lines to your ``pyproject.toml`` file:

.. code-block:: TOML

	[tool.whey.builders]
	binary = "whey_conda"

The ``whey-conda``-specific configuration is defined in the ``tool.whey-conda`` table.
:conf:`conda-channels` and :conf:`conda-extras` can instead be defined in the `tool.mkrecipe`_
table if you also use ``mkrecipe``.


.. _tool.mkrecipe: https://mkrecipe.readthedocs.io/en/latest/configuration.html#tool-mkrecipe

``[tool.whey-conda]``
----------------------

All keys are optional.


.. conf:: conda-description

	**Type**: :toml:`String`

	The description of the package.

	You can use a single ``%s`` in the description, which will be substituted with
	the value of the :pep621:`description` key from ``pyproject.toml``.

	The default value is ``'%s'``.

	:bold-title:`Example:`

	.. code-block:: TOML

		[tool.whey-conda]
		conda-description = "Fantastic Spam!"


.. conf:: conda-channels

	**Type**: :toml:`Array` of :toml:`strings <String>`

	A list of required conda channels to build and use the package.

	The default value is ``[]``.

	:bold-title:`Example:`

	.. code-block:: toml

		[tool.whey-conda]
		conda-channels = [
			"domdfcoding",
			"conda-forge",
			"bioconda",
		]


.. conf:: conda-extras

	**Type**: :toml:`Array` of :toml:`strings <String>`

	A list of extras (see :pep621:`option-dependencies`) to include as requirements in the Conda package.

	* The special keyword ``'all'`` indicates all extras should be included.
	* The special keyword ``'none'`` indicates no extras should be included.

	The default value is ``'none'``.

	:bold-title:`Examples:`

	.. code-block:: toml

		[tool.whey-conda]
		conda-extras = [ "test", "doc",]

		[tool.whey-conda]
		conda-extras = "all"
