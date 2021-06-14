#!/usr/bin/env python3
#
#  __init__.py
"""
Whey extension for creating Conda packages for Python projects.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import datetime
import os
import pathlib
import posixpath
import tarfile
import tempfile
from itertools import chain
from subprocess import PIPE, Popen
from textwrap import dedent, indent
from typing import Any, List, Mapping, Optional, Union

# 3rd party
import click
import dom_toml
from consolekit.terminal_colours import Fore
from consolekit.utils import abort
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from domdf_python_tools.words import word_join
from mkrecipe.config import MkrecipeParser
from pyproject_parser.classes import _NormalisedName
from shippinglabel.checksum import get_record_entry
from shippinglabel.conda import make_conda_description, prepare_requirements, validate_requirements
from shippinglabel.requirements import ComparableRequirement
from whey.builder import WheelBuilder

# this package
from whey_conda.config import WheyCondaParser

__all__ = ["CondaBuilder"]

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020-2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.1.0"
__email__: str = "dominic@davis-foster.co.uk"


class CondaBuilder(WheelBuilder):
	"""
	Builds Conda packages using metadata read from ``pyproject.toml``.

	:param project_dir: The project to build the distribution for.
	:param build_dir: The (temporary) build directory.
	:default build_dir: :file:`{<project_dir>}/build/wheel`
	:param out_dir: The output directory.
	:default out_dir: :file:`{<project_dir>}/dist`
	:param verbose: Enable verbose output.

	.. autosummary-widths:: 1/2
		:html: 45/100
	"""

	def __init__(
			self,
			project_dir: PathPlus,
			config: Mapping[str, Any],
			build_dir: Optional[PathLike] = None,
			out_dir: Optional[PathLike] = None,
			*,
			verbose: bool = False,
			colour: bool = None,
			):
		super().__init__(
				project_dir,
				config=config,
				build_dir=build_dir,
				out_dir=out_dir,
				verbose=verbose,
				colour=colour,
				)

		our_config = dom_toml.load(self.project_dir / "pyproject.toml")

		mkrecipe_table = our_config.get("tool", {}).get("mkrecipe", {})
		mkrecipe_config = MkrecipeParser().parse(mkrecipe_table, set_defaults=False)

		if "extras" in mkrecipe_config:
			mkrecipe_config["conda-extras"] = mkrecipe_config["extras"]

		self.config.update(mkrecipe_config)

		whey_deb_table = our_config.get("tool", {}).get("whey-conda", {})
		parsed_config = WheyCondaParser().parse(whey_deb_table, set_defaults=False)
		self.config.update(parsed_config)

		for key, default in WheyCondaParser.defaults.items():
			self.config.setdefault(key, default)
		# for key, factory in WheyCondaParser.factories.items():
		# 	self.config.setdefault(key, factory())

		if "%s" in self.config["conda-description"]:
			if self.config["description"]:
				self.config["conda-description"] = self.config["conda-description"] % self.config["description"]
			else:
				self.config["conda-description"] = self.config["conda-description"] % ''

	@property
	def default_build_dir(self) -> PathPlus:  # pragma: no cover
		"""
		Provides a default for the ``build_dir`` argument.
		"""

		return self.project_dir / "build" / "conda"

	@property
	def info_dir(self) -> PathPlus:
		"""
		The ``info`` directory in the build directory for Conda builds.
		"""

		info_dir = self.build_dir / "info"
		info_dir.maybe_make()
		return info_dir

	def _echo_if_v(self, *args, **kwargs):
		if self.verbose:
			self._echo(*args, **kwargs)

	def write_conda_index(self, build_number: int = 1):
		"""
		Write the conda ``index.json`` file.

		.. seealso:: https://docs.conda.io/projects/conda-build/en/latest/resources/package-spec.html#info-index-json

		:param build_number:
		"""  # noqa: D400

		build_string = f"py_{build_number}"
		# https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html#build-number-and-string

		package_name = self.config["name"]
		if isinstance(package_name, _NormalisedName):
			package_name = package_name.unnormalized

		index = {
				"name": package_name.lower(),
				"version": str(self.config["version"]),
				"build": build_string,
				"build_number": build_number,
				"depends": list(map(str, self.get_runtime_requirements())),
				"arch": None,
				"noarch": "python",
				"platform": None,
				"subdir": "noarch",
				"timestamp": int(datetime.datetime.now().timestamp() * 1000)
				}

		index_json_file = self.info_dir / "index.json"
		index_json_file.dump_json(index, indent=2)
		self.report_written(index_json_file)

	def write_conda_about(self):
		"""
		Write the conda ``about.json`` file.

		.. seealso:: https://docs.conda.io/projects/conda-build/en/latest/resources/package-spec.html#info-about-json
		"""

		about = {}

		for category, url in self.config["urls"].items():
			if category.lower() in {"homepage", "home page"}:
				about["home"] = url
				about["dev_url"] = url
			elif category.lower().startswith("source"):
				about["dev_url"] = url
			elif category.lower() in {"docs", "documentation"}:
				about["doc_url"] = url

		# TODO: "license_family"
		# TODO: "license_url"

		about["license"] = self.config["license-key"]

		if self.config["description"]:
			about["summary"] = self.config["description"]

		about["description"] = make_conda_description(
				self.config["conda-description"],
				self.config["conda-channels"],
				)

		author = []
		maintainer = []

		for entry in self.config["authors"]:
			if entry["name"]:
				author.append(entry["name"])

		for entry in self.config["maintainers"]:
			if entry["name"]:
				maintainer.append(entry["name"])

		if maintainer:
			about["extra"] = {"maintainers": maintainer}
		elif author:
			about["extra"] = {"maintainers": author}

		about_json_file = self.info_dir / "about.json"
		about_json_file.dump_json(about, indent=2)
		self.report_written(about_json_file)

	def create_conda_archive(self, wheel_contents_dir: PathLike, build_number: int = 1) -> str:
		"""
		Create the conda archive.

		:param wheel_contents_dir: The directory containing the installed contents of the wheel.
		:param build_number:

		:return: The filename of the created archive.
		"""

		build_string = f"py_{build_number}"
		site_packages = pathlib.PurePosixPath("site-packages")

		package_name = self.config["name"]
		if isinstance(package_name, _NormalisedName):
			package_name = package_name.unnormalized

		conda_filename = self.out_dir / f"{package_name.lower()}-{self.config['version']}-{build_string}.tar.bz2"
		wheel_contents_dir = PathPlus(wheel_contents_dir)

		self.out_dir.maybe_make(parents=True)

		files_entries = []

		with tarfile.open(conda_filename, mode="w:bz2") as conda_archive:

			pkg_dir = posixpath.join(self.config["source-dir"], self.config["package"].split('.')[0])
			for file in (wheel_contents_dir / pkg_dir).rglob('*'):
				if file.is_file():
					filename = (site_packages / file.relative_to(wheel_contents_dir)).as_posix()
					files_entries.append(str(filename))
					conda_archive.add(str(file), arcname=filename)

			dist_info_dir = wheel_contents_dir / f"{self.archive_name}.dist-info"

			if (dist_info_dir / "INSTALLER").is_file():
				# Otherwise it says pip
				(dist_info_dir / "INSTALLER").write_clean("conda")

			for file in dist_info_dir.rglob('*'):
				if file.name == "RECORD":
					record_lines = file.read_lines()
					for idx, line in enumerate(record_lines):
						# Ensure the digest and size are updated for "conda" rather than "pip"
						if ".dist-info/INSTALLER,sha256=" in line:
							record_lines[idx] = get_record_entry(
									dist_info_dir / "INSTALLER",
									relative_to=wheel_contents_dir,
									)
						elif ".dist-info/direct_url.json,sha256=" in line:
							record_lines[idx] = ''
						elif ".dist-info/REQUESTED,sha256=" in line:
							record_lines[idx] = ''

					# Remove double blank line caused by removal of entries
					file.write_clean('\n'.join(record_lines).replace("\n\n", '\n'))

				elif file.name in {"REQUESTED", "direct_url.json"}:
					continue

				if file.is_file():
					filename = (site_packages / file.relative_to(wheel_contents_dir)).as_posix()
					files_entries.append(str(filename))
					conda_archive.add(str(file), arcname=filename)

			(self.info_dir / "files").write_lines(files_entries)

			for file in self.info_dir.rglob('*'):
				if not file.is_file():
					continue

				conda_archive.add(str(file), arcname=file.relative_to(self.build_dir).as_posix())

		return os.path.basename(conda_filename)

	def write_license(self, dest_dir: PathPlus, dest_filename: str = "LICENSE"):
		"""
		Write the ``LICENSE`` file.

		:param dest_dir: The directory to write the file into.
		:param dest_filename: The name of the file to write in ``dest_dir``.
		"""

		if self.config.get("license", None) is not None:
			target = dest_dir / dest_filename
			target.parent.maybe_make(parents=True)
			target.write_clean(self.config["license"].text)
			self.report_written(target)

	def get_runtime_requirements(self) -> List[ComparableRequirement]:
		"""
		Returns a list of the project's runtime requirements.
		"""

		extras: List[Union[ComparableRequirement, str]] = []

		if self.config["conda-extras"] == "all":
			extras.extend(chain.from_iterable(self.config["optional-dependencies"].values()))
		elif self.config["conda-extras"] == "none":
			pass
		else:
			for extra in self.config["conda-extras"]:
				extras.extend(list(self.config["optional-dependencies"].get(extra, ())))

		extra_requirements = [ComparableRequirement(str(r)) for r in extras]

		# TODO: handle extras from the dependencies. Lookup the requirements in the wheel metadata.
		#  Perhaps wait until exposed in PyPI API
		all_requirements = prepare_requirements(chain(self.config["dependencies"], extra_requirements))

		self._echo_if_v(
				f"Checking dependencies against the following channels: "
				f"{word_join(self.config['conda-channels'], use_repr=True)}"
				)

		all_requirements = validate_requirements(all_requirements, self.config["conda-channels"])

		requirements_entries = [req for req in all_requirements if req and req != "numpy"]

		if [v.specifier for v in all_requirements if v == "numpy"]:
			requirements_entries.append(ComparableRequirement("numpy>=1.19.0"))

		return requirements_entries

	def build_conda(self) -> str:
		"""
		Build the Conda distribution.

		:return: The filename of the created archive.
		"""

		build_number = 1

		# Build the wheel first and clear the build directory
		wheel_file = self.build_wheel()

		self.clear_build_dir()

		self.write_license(self.info_dir, "license.txt")

		self.write_conda_about()
		self.write_conda_index(build_number=build_number)

		with tempfile.TemporaryDirectory() as tmpdir:
			self._echo_if_v("Installing wheel into temporary directory")

			pip_install_wheel(self.out_dir / wheel_file, tmpdir, self.verbose)
			conda_filename = self.create_conda_archive(str(tmpdir), build_number=build_number)

		self._echo(Fore.GREEN(f"Conda package created at {(self.out_dir / conda_filename).resolve().as_posix()}"))
		return conda_filename

	build = build_conda


def pip_install_wheel(wheel_file: PathLike, target_dir: PathLike, verbose: bool = False):
	command = [
			"pip",
			"install",
			os.fspath(wheel_file),
			"--target",
			os.fspath(target_dir),
			"--no-deps",
			"--no-compile",
			"--no-warn-script-location",
			"--no-warn-conflicts",
			"--disable-pip-version-check",
			]

	process = Popen(command, stdout=PIPE)
	(output, err) = process.communicate()
	exit_code = process.wait()

	if verbose:
		click.echo((output or b'').decode("UTF-8"))
		click.echo((err or b'').decode("UTF-8"), err=True)

	if exit_code != 0:
		err = err or b''

		message = dedent(
				f"""\
					Command '{' '.join(command)}' returned non-zero exit code {exit_code}:

					{indent(err.decode("UTF-8"), '    ')}
					"""
				)

		raise abort(message.rstrip() + '\n')
