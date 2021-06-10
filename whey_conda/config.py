#!/usr/bin/env python3
#
#  config.py
"""
Configuration for ``whey-conda``.
"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
from typing import Dict, List, Union

# 3rd party
from dom_toml.parser import TOML_TYPES, AbstractConfigParser, BadConfigError, construct_path
from typing_extensions import Literal

__all__ = ["WheyCondaParser"]


class WheyCondaParser(AbstractConfigParser):
	"""
	Parser for the ``[tool.whey-conda]`` table from ``pyproject.toml``.

	.. autosummary-widths:: 7/16
		:html: 4/10
	"""

	defaults = {"conda-description": "%s", "conda-extras": "none", "conda-channels": ("conda-forge", )}

	table_name = ("tool", "whey-conda")

	def parse_conda_description(self, config: Dict[str, TOML_TYPES]) -> str:
		"""
		Parse the ``conda-description`` key, giving the description of the package.

		You can use a single ``%s`` in the description, which will be substituted with
		the value of the :pep621:`description` key from ``pyproject.toml``.

		The default value is ``'%s'``.

		:bold-title:`Example:`

		.. code-block:: TOML

			[tool.whey-conda]
			conda-description = "Fantastic Spam!"

		:param config: The unparsed TOML config for the ``[tool.whey-conda]`` table.
		"""

		description = config["conda-description"]
		self.assert_type(description, str, ["tool", "whey-conda", "conda-description"])
		return description

	def parse_conda_channels(self, config: Dict[str, TOML_TYPES]) -> List[str]:
		"""
		Parse the ``conda-channels`` key, giving a list of required conda channels to build and use the package.

		The default value is ``[]``.

		:bold-title:`Example:`

		.. code-block:: toml

			[tool.whey-conda]
			conda-channels = [
				"domdfcoding",
				"conda-forge",
				"bioconda",
			]

		:param config: The unparsed TOML config for the ``[tool.whey-conda]`` table.
		"""  # noqa: D400

		channels = config["conda-channels"]

		for idx, impl in enumerate(channels):
			self.assert_indexed_type(impl, str, [*self.table_name, "conda-channels"], idx=idx)

		return channels

	def parse_conda_extras(
			self,
			config: Dict[str, TOML_TYPES],
			) -> Union[Literal["all"], Literal["none"], List[str]]:
		"""
		Parse the ``conda-extras`` key, giving a list of extras (see :pep621:`optional-dependencies`)
		to include as requirements in the Conda package.

		* The special keyword ``'all'`` indicates all extras should be included.
		* The special keyword ``'none'`` indicates no extras should be included.

		The default value is ``'none'``.

		:bold-title:`Examples:`

		.. code-block:: toml

			[tool.whey-conda]
			conda-extras = [ "test", "doc",]

			[tool.whey-conda]
			conda-extras = "all"

		"""  # noqa: D400

		extras = config["conda-extras"]

		path_elements = [*self.table_name, "conda-extras"]

		if isinstance(extras, str):
			extras_lower = extras.lower()
			if extras_lower == "all":
				return "all"
			elif extras_lower == "none":
				return "none"
			else:
				raise BadConfigError(
						f"Invalid value for [{construct_path(path_elements)}]: "
						"Expected 'all', 'none' or a list of strings."
						)

		for idx, impl in enumerate(extras):
			self.assert_indexed_type(impl, str, path_elements, idx=idx)

		return extras

	@property
	def keys(self) -> List[str]:
		"""
		The keys to parse from the TOML file.
		"""

		return [
				"conda-description",
				"conda-channels",
				"conda-extras",
				]

	def parse(
			self,
			config: Dict[str, TOML_TYPES],
			set_defaults: bool = False,
			) -> Dict[str, TOML_TYPES]:
		"""
		Parse the TOML configuration.

		:param config: The unparsed TOML config for the ``[tool.whey-conda]`` table.
		:param set_defaults: If :py:obj:`True`, the values in
			:attr:`self.defaults <dom_toml.parser.AbstractConfigParser.defaults>`
			and :attr:`self.factories <dom_toml.parser.AbstractConfigParser.factories>`
			will be set as defaults for the returned mapping.
		"""

		return super().parse(config, set_defaults=set_defaults)
