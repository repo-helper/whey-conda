# stdlib
import tarfile
import tempfile

# 3rd party
import pytest
from coincidence import min_version
from coincidence.regressions import AdvancedDataRegressionFixture, check_file_regression
from domdf_python_tools.paths import PathPlus
from pyproject_examples.example_configs import (
		AUTHORS,
		CLASSIFIERS,
		DEPENDENCIES,
		DYNAMIC_REQUIREMENTS,
		ENTRY_POINTS,
		KEYWORDS,
		LONG_REQUIREMENTS,
		MAINTAINERS,
		MINIMAL_CONFIG,
		OPTIONAL_DEPENDENCIES,
		UNICODE,
		URLS
		)
from pytest_regressions.file_regression import FileRegressionFixture
from whey import SDistBuilder
from whey.config import load_toml

# this package
from tests.example_configs import (
		COMPLETE_A,
		COMPLETE_B,
		CONDA_CHANNELS,
		CONDA_DESCRIPTION,
		CONDA_EXTRAS,
		CONDA_EXTRAS_ALL,
		CONDA_EXTRAS_EXPLICIT_NONE,
		DESCRIPTION,
		MKRECIPE_CHANNELS,
		MKRECIPE_EXTRAS,
		MKRECIPE_EXTRAS_ALL
		)
from whey_conda import CondaBuilder


@pytest.mark.parametrize(
		"config",
		[
				pytest.param(MINIMAL_CONFIG, id="minimal"),
				pytest.param(DESCRIPTION, id="description"),
				pytest.param(
						f'{MINIMAL_CONFIG}\nrequires-python = ">=3.8"',
						id="requires-python",
						marks=min_version(3.8),
						),
				pytest.param(
						f'{MINIMAL_CONFIG}\nrequires-python = ">=2.7,!=3.0.*,!=3.2.*"',
						id="requires-python_complex"
						),
				pytest.param(KEYWORDS, id="keywords"),
				pytest.param(AUTHORS, id="authors"),
				pytest.param(MAINTAINERS, id="maintainers"),
				pytest.param(CLASSIFIERS, id="classifiers"),
				pytest.
				param(f"{DEPENDENCIES}\n[tool.whey-conda]\nconda-channels = ['conda-forge']\n", id="dependencies"),
				pytest.param(OPTIONAL_DEPENDENCIES, id="optional-dependencies"),
				pytest.param(CONDA_DESCRIPTION, id="conda-description"),
				pytest.param(CONDA_EXTRAS, id="conda-extras"),
				pytest.param(CONDA_EXTRAS_ALL, id="conda-extras-all"),
				pytest.param(CONDA_EXTRAS_EXPLICIT_NONE, id="conda-extras-explicit-none"),
				pytest.param(MKRECIPE_EXTRAS, id="mkrecipe-extras"),
				pytest.param(MKRECIPE_EXTRAS_ALL, id="mkrecipe-extras-all"),
				pytest.param(CONDA_CHANNELS, id="conda-channels"),
				pytest.param(MKRECIPE_CHANNELS, id="mkrecipe-channels"),
				pytest.param(URLS, id="urls"),
				pytest.param(ENTRY_POINTS, id="entry_points"),
				pytest.param(UNICODE, id="unicode"),
				]
		)
def test_build_success(
		config: str,
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		file_regression: FileRegressionFixture,
		capsys,
		fixed_datetime,
		):
	(tmp_pathplus / "pyproject.toml").write_clean(config)
	(tmp_pathplus / "spam").mkdir()
	(tmp_pathplus / "spam" / "__init__.py").write_clean("print('hello world)")

	data = {}

	with tempfile.TemporaryDirectory() as tmpdir:
		conda_builder = CondaBuilder(
				project_dir=tmp_pathplus,
				config=load_toml(tmp_pathplus / "pyproject.toml"),
				build_dir=tmpdir,
				out_dir=tmp_pathplus,
				verbose=True,
				colour=False,
				)

		wheel = conda_builder.build_conda()
		assert (tmp_pathplus / wheel).is_file()

		with tarfile.open(tmp_pathplus / wheel) as zip_file:
			data["wheel_content"] = sorted(zip_file.getnames())

			with zip_file.extractfile("site-packages/spam/__init__.py") as fp:
				assert fp.read().decode("UTF-8") == "print('hello world)\n"

			with zip_file.extractfile("site-packages/spam-2020.0.0.dist-info/METADATA") as fp:
				check_file_regression(fp.read().decode("UTF-8"), file_regression)

			with zip_file.extractfile("info/about.json") as fp:
				check_file_regression(fp.read().decode("UTF-8"), file_regression, extension="_about.json")

			with zip_file.extractfile("info/index.json") as fp:
				check_file_regression(fp.read().decode("UTF-8"), file_regression, extension="_index.json")

			# assert "info/license.txt" in zip_file.getnames()
			assert "info/files" in zip_file.getnames()

	outerr = capsys.readouterr()
	data["stdout"] = outerr.out.replace(tmp_pathplus.as_posix(), "...")
	data["stderr"] = outerr.err

	advanced_data_regression.check(data)


def check_built_wheel(filename: PathPlus, file_regression: FileRegressionFixture):
	assert filename.is_file()

	with tarfile.open(filename) as zip_file:

		with zip_file.extractfile("site-packages/whey/__init__.py") as fp:
			assert fp.read().decode("UTF-8") == "print('hello world)\n"
		with zip_file.extractfile("site-packages/whey-2021.0.0.dist-info/METADATA") as fp:
			check_file_regression(fp.read().decode("UTF-8"), file_regression)

		contents = sorted(zip_file.getnames())

		with zip_file.extractfile("site-packages/whey-2021.0.0.dist-info/RECORD") as fp:
			for line in fp.readlines():
				entry_filename, digest, size, *_ = line.decode("UTF-8").strip().split(',')
				entry_filename = f"site-packages/{entry_filename}"
				assert entry_filename in contents, entry_filename
				contents.remove(entry_filename)

				if "RECORD" not in entry_filename:
					assert zip_file.getmember(entry_filename).size == int(size), entry_filename
					# TODO: check digest

		return sorted(zip_file.getnames())


@pytest.mark.parametrize(
		"config",
		[
				# pytest.param(COMPLETE_PROJECT_A, id="COMPLETE_PROJECT_A"),
				pytest.param(
						f"{COMPLETE_A}\n[tool.whey-conda]\nconda-channels = ['conda-forge']\n",
						id="COMPLETE_A",
						),
				pytest.param(
						f"{COMPLETE_B}\n[tool.whey-conda]\nconda-channels = ['conda-forge']\n",
						id="COMPLETE_B",
						),
				pytest.param(
						f"{LONG_REQUIREMENTS}\n[tool.whey-conda]\nconda-channels = ['conda-forge']\n",
						id="LONG_REQUIREMENTS",
						),
				]
		)
def test_build_complete(
		config: str,
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		file_regression: FileRegressionFixture,
		capsys,
		):
	(tmp_pathplus / "pyproject.toml").write_clean(config)
	(tmp_pathplus / "whey").mkdir()
	(tmp_pathplus / "whey" / "__init__.py").write_clean("print('hello world)")
	(tmp_pathplus / "README.rst").write_clean("Spam Spam Spam Spam")
	(tmp_pathplus / "LICENSE").write_clean("This is the license")
	(tmp_pathplus / "requirements.txt").write_clean("domdf_python_tools")

	data = {}

	with tempfile.TemporaryDirectory() as tmpdir:
		conda_builder = CondaBuilder(
				project_dir=tmp_pathplus,
				config=load_toml(tmp_pathplus / "pyproject.toml"),
				build_dir=tmpdir,
				out_dir=tmp_pathplus,
				verbose=True,
				colour=False,
				)

		wheel = conda_builder.build_conda()
		data["wheel_content"] = check_built_wheel(tmp_pathplus / wheel, file_regression)

	outerr = capsys.readouterr()
	data["stdout"] = outerr.out.replace(tmp_pathplus.as_posix(), "...")
	data["stderr"] = outerr.err

	advanced_data_regression.check(data)


def test_build_additional_files(
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		file_regression: FileRegressionFixture,
		capsys,
		):

	(tmp_pathplus / "pyproject.toml").write_lines([
			COMPLETE_B,
			'',
			"additional-files = [",
			'  "include whey/style.css",',
			'  "exclude whey/style.css",',
			'  "include whey/style.css",',
			'  "recursive-include whey/static *",',
			'  "recursive-exclude whey/static *.txt",',
			']',
			"[tool.whey-conda]",
			"conda-channels = ['conda-forge']",
			'',
			])
	(tmp_pathplus / "whey").mkdir()
	(tmp_pathplus / "whey" / "__init__.py").write_clean("print('hello world)")
	(tmp_pathplus / "whey" / "style.css").write_clean("This is the style.css file")
	(tmp_pathplus / "whey" / "static").mkdir()
	(tmp_pathplus / "whey" / "static" / "foo.py").touch()
	(tmp_pathplus / "whey" / "static" / "foo.c").touch()
	(tmp_pathplus / "whey" / "static" / "foo.txt").touch()
	(tmp_pathplus / "README.rst").write_clean("Spam Spam Spam Spam")
	(tmp_pathplus / "LICENSE").write_clean("This is the license")
	(tmp_pathplus / "requirements.txt").write_clean("domdf_python_tools")

	data = {}

	with tempfile.TemporaryDirectory() as tmpdir:
		conda_builder = CondaBuilder(
				project_dir=tmp_pathplus,
				config=load_toml(tmp_pathplus / "pyproject.toml"),
				build_dir=tmpdir,
				out_dir=tmp_pathplus,
				verbose=True,
				colour=False,
				)

		wheel = conda_builder.build_conda()
		assert (tmp_pathplus / wheel).is_file()
		zip_file = tarfile.open(tmp_pathplus / wheel)
		data["wheel_content"] = sorted(zip_file.getnames())

		with zip_file.extractfile("site-packages/whey/__init__.py") as fp:
			assert fp.read().decode("UTF-8") == "print('hello world)\n"

		with zip_file.extractfile("site-packages/whey-2021.0.0.dist-info/METADATA") as fp:
			check_file_regression(fp.read().decode("UTF-8"), file_regression)

	outerr = capsys.readouterr()
	data["stdout"] = outerr.out.replace(tmp_pathplus.as_posix(), "...")
	data["stderr"] = outerr.err

	advanced_data_regression.check(data)


def test_build_markdown_readme(
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		file_regression: FileRegressionFixture,
		capsys,
		):

	(tmp_pathplus / "pyproject.toml").write_clean(
			f"{COMPLETE_B.replace('.rst', '.md')}\n[tool.whey-conda]\nconda-channels = ['conda-forge']\n",
			)
	(tmp_pathplus / "whey").mkdir()
	(tmp_pathplus / "whey" / "__init__.py").write_clean("print('hello world)")
	(tmp_pathplus / "README.md").write_clean("Spam Spam Spam Spam")
	(tmp_pathplus / "LICENSE").write_clean("This is the license")
	(tmp_pathplus / "requirements.txt").write_clean("domdf_python_tools")

	data = {}

	with tempfile.TemporaryDirectory() as tmpdir:
		conda_builder = CondaBuilder(
				project_dir=tmp_pathplus,
				config=load_toml(tmp_pathplus / "pyproject.toml"),
				build_dir=tmpdir,
				out_dir=tmp_pathplus,
				verbose=True,
				colour=False,
				)

		wheel = conda_builder.build_conda()
		data["wheel_content"] = check_built_wheel(tmp_pathplus / wheel, file_regression)

	outerr = capsys.readouterr()
	data["stdout"] = outerr.out.replace(tmp_pathplus.as_posix(), "...")
	data["stderr"] = outerr.err

	advanced_data_regression.check(data)


def test_build_missing_dir(tmp_pathplus: PathPlus):
	(tmp_pathplus / "pyproject.toml").write_clean(MINIMAL_CONFIG)

	with tempfile.TemporaryDirectory() as tmpdir:
		conda_builder = CondaBuilder(
				project_dir=tmp_pathplus,
				config=load_toml(tmp_pathplus / "pyproject.toml"),
				build_dir=tmpdir,
				out_dir=tmp_pathplus,
				verbose=True,
				colour=False,
				)

		with pytest.raises(FileNotFoundError, match="Package directory 'spam' not found."):
			conda_builder.build_conda()


def test_build_empty_dir(tmp_pathplus: PathPlus):
	(tmp_pathplus / "pyproject.toml").write_clean(MINIMAL_CONFIG)
	(tmp_pathplus / "spam").mkdir()

	with tempfile.TemporaryDirectory() as tmpdir:
		conda_builder = CondaBuilder(
				project_dir=tmp_pathplus,
				config=load_toml(tmp_pathplus / "pyproject.toml"),
				build_dir=tmpdir,
				out_dir=tmp_pathplus,
				verbose=True,
				colour=False,
				)

		with pytest.raises(FileNotFoundError, match="No Python source files found in"):
			conda_builder.build_conda()


@pytest.mark.parametrize(
		"config",
		[
				pytest.param(
						f"{COMPLETE_A}\n[tool.whey-conda]\nconda-channels = ['conda-forge']\n",
						id="COMPLETE_A",
						),
				pytest.param(
						f"{COMPLETE_B}\n[tool.whey-conda]\nconda-channels = ['conda-forge']\n",
						id="COMPLETE_B",
						),
				pytest.param(
						f"{DYNAMIC_REQUIREMENTS}\n[tool.whey-conda]\nconda-channels = ['conda-forge']\n",
						id="DYNAMIC_REQUIREMENTS",
						),
				pytest.param(
						f"{LONG_REQUIREMENTS}\n[tool.whey-conda]\nconda-channels = ['conda-forge']\n",
						id="LONG_REQUIREMENTS",
						),
				]
		)
def test_build_conda_from_sdist(
		config: str,
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		file_regression: FileRegressionFixture,
		capsys,
		):
	(tmp_pathplus / "pyproject.toml").write_clean(config)
	(tmp_pathplus / "whey").mkdir()
	(tmp_pathplus / "whey" / "__init__.py").write_clean("print('hello world)")
	(tmp_pathplus / "README.rst").write_clean("Spam Spam Spam Spam")
	(tmp_pathplus / "LICENSE").write_clean("This is the license")
	(tmp_pathplus / "requirements.txt").write_lines([
			"httpx", "gidgethub[httpx]>4.0.0", "django>2.1; os_name != 'nt'", "django>2.0; os_name == 'nt'"
			])

	# Build the sdist

	with tempfile.TemporaryDirectory() as tmpdir:
		sdist_builder = SDistBuilder(
				project_dir=tmp_pathplus,
				config=load_toml(tmp_pathplus / "pyproject.toml"),
				build_dir=tmpdir,
				out_dir=tmp_pathplus,
				verbose=True,
				colour=False,
				)

		sdist = sdist_builder.build_sdist()
		assert (tmp_pathplus / sdist).is_file()

	# unpack sdist into another tmpdir and use that as project_dir

	(tmp_pathplus / "sdist_unpacked").mkdir()

	with tarfile.open(tmp_pathplus / sdist) as sdist_tar:
		sdist_tar.extractall(path=tmp_pathplus / "sdist_unpacked")

	capsys.readouterr()
	data = {}

	with tempfile.TemporaryDirectory() as tmpdir:
		conda_builder = CondaBuilder(
				project_dir=tmp_pathplus / "sdist_unpacked/whey-2021.0.0/",
				config=load_toml(tmp_pathplus / "pyproject.toml"),
				build_dir=tmpdir,
				out_dir=tmp_pathplus,
				verbose=True,
				colour=False,
				)
		wheel = conda_builder.build_conda()
		data["wheel_content"] = check_built_wheel(tmp_pathplus / wheel, file_regression)

	outerr = capsys.readouterr()
	data["stdout"] = outerr.out.replace(tmp_pathplus.as_posix(), "...")
	data["stderr"] = outerr.err

	advanced_data_regression.check(data)


#
# @pytest.mark.parametrize(
# 		"config", [
# 				pytest.param(COMPLETE_A, id="COMPLETE_A"),
# 				pytest.param(COMPLETE_B, id="COMPLETE_B"),
# 				]
# 		)
# def test_build_wheel_reproducible(
# 		config: str,
# 		tmp_pathplus: PathPlus,
# 		):
# 	(tmp_pathplus / "pyproject.toml").write_clean(config)
# 	(tmp_pathplus / "whey").mkdir()
# 	(tmp_pathplus / "whey" / "__init__.py").write_clean("print('hello world)")
# 	(tmp_pathplus / "README.rst").write_clean("Spam Spam Spam Spam")
# 	(tmp_pathplus / "LICENSE").write_clean("This is the license")
# 	(tmp_pathplus / "requirements.txt").write_clean("domdf_python_tools")
#
# 	# Build the wheel twice
#
# 	with tempfile.TemporaryDirectory() as tmpdir:
# 		conda_builder = CondaBuilder(
# 				project_dir=tmp_pathplus,
# 				build_dir=tmpdir,
# 				out_dir=tmp_pathplus / "wheel1",
# 				verbose=True,
# 				colour=False,
# 				config=load_toml(tmp_pathplus / "pyproject.toml"),
# 				)
#
# 		wheel = conda_builder.build_conda()
# 		assert (tmp_pathplus / "wheel1" / wheel).is_file()
#
# 	with tempfile.TemporaryDirectory() as tmpdir:
# 		conda_builder = CondaBuilder(
# 				project_dir=tmp_pathplus,
# 				build_dir=tmpdir,
# 				out_dir=tmp_pathplus / "wheel2",
# 				verbose=True,
# 				colour=False,
# 				config=load_toml(tmp_pathplus / "pyproject.toml"),
# 				)
# 		wheel = conda_builder.build_conda()
# 		assert (tmp_pathplus / "wheel2" / wheel).is_file()
#
# 	# extract both
#
# 	shutil.unpack_archive(
# 			str(tmp_pathplus / "wheel1" / wheel),
# 			extract_dir=tmp_pathplus / "wheel1" / "unpack",
# 			format="zip",
# 			)
# 	shutil.unpack_archive(
# 			str(tmp_pathplus / "wheel1" / wheel),
# 			extract_dir=tmp_pathplus / "wheel2" / "unpack",
# 			format="zip",
# 			)
# 	# (tmp_pathplus / "wheel2" / "unpack" / "foo.txt").touch()
#
# 	assert compare_dirs(
# 			tmp_pathplus / "wheel1" / "unpack",
# 			tmp_pathplus / "wheel2" / "unpack",
# 			)


def test_build_underscore_name(
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		file_regression: FileRegressionFixture,
		fixed_datetime,
		capsys,
		):
	(tmp_pathplus / "pyproject.toml").write_lines([
			"[project]",
			'name = "spam_spam"',
			'version = "2020.0.0"',
			])
	(tmp_pathplus / "spam_spam").mkdir()
	(tmp_pathplus / "spam_spam" / "__init__.py").write_clean("print('hello world)")

	data = {}

	with tempfile.TemporaryDirectory() as tmpdir:
		conda_builder = CondaBuilder(
				project_dir=tmp_pathplus,
				build_dir=tmpdir,
				out_dir=tmp_pathplus,
				verbose=True,
				colour=False,
				config=load_toml(tmp_pathplus / "pyproject.toml"),
				)

		wheel = conda_builder.build_conda()
		assert (tmp_pathplus / wheel).is_file()

		with tarfile.open(tmp_pathplus / wheel) as zip_file:
			data["wheel_content"] = sorted(zip_file.getnames())

			with zip_file.extractfile("site-packages/spam_spam/__init__.py") as fp:
				assert fp.read().decode("UTF-8") == "print('hello world)\n"

			with zip_file.extractfile("site-packages/spam_spam-2020.0.0.dist-info/METADATA") as fp:
				check_file_regression(fp.read().decode("UTF-8"), file_regression)

			with zip_file.extractfile("info/about.json") as fp:
				check_file_regression(fp.read().decode("UTF-8"), file_regression, extension="_about.json")

			with zip_file.extractfile("info/index.json") as fp:
				check_file_regression(fp.read().decode("UTF-8"), file_regression, extension="_index.json")

			# assert "info/license.txt" in zip_file.getnames()
			assert "info/files" in zip_file.getnames()

	outerr = capsys.readouterr()
	data["stdout"] = outerr.out.replace(tmp_pathplus.as_posix(), "...")
	data["stderr"] = outerr.err

	advanced_data_regression.check(data)


def test_build_stubs_name(
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		file_regression: FileRegressionFixture,
		capsys,
		fixed_datetime,
		):
	(tmp_pathplus / "pyproject.toml").write_lines([
			"[project]",
			'name = "spam_spam-stubs"',
			'version = "2020.0.0"',
			])
	(tmp_pathplus / "spam_spam-stubs").mkdir()
	(tmp_pathplus / "spam_spam-stubs" / "__init__.pyi").write_clean("print('hello world)")

	data = {}

	with tempfile.TemporaryDirectory() as tmpdir:
		conda_builder = CondaBuilder(
				project_dir=tmp_pathplus,
				build_dir=tmpdir,
				out_dir=tmp_pathplus,
				verbose=True,
				colour=False,
				config=load_toml(tmp_pathplus / "pyproject.toml"),
				)

		wheel = conda_builder.build_conda()
		assert (tmp_pathplus / wheel).is_file()

		with tarfile.open(tmp_pathplus / wheel) as zip_file:
			data["wheel_content"] = sorted(zip_file.getnames())

			with zip_file.extractfile("site-packages/spam_spam-stubs/__init__.pyi") as fp:
				assert fp.read().decode("UTF-8") == "print('hello world)\n"

			with zip_file.extractfile("site-packages/spam_spam_stubs-2020.0.0.dist-info/METADATA") as fp:
				check_file_regression(fp.read().decode("UTF-8"), file_regression)

			with zip_file.extractfile("info/about.json") as fp:
				check_file_regression(fp.read().decode("UTF-8"), file_regression, extension="_about.json")

			with zip_file.extractfile("info/index.json") as fp:
				check_file_regression(fp.read().decode("UTF-8"), file_regression, extension="_index.json")

			# assert "info/license.txt" in zip_file.getnames()
			assert "info/files" in zip_file.getnames()

	outerr = capsys.readouterr()
	data["stdout"] = outerr.out.replace(tmp_pathplus.as_posix(), "...")
	data["stderr"] = outerr.err

	advanced_data_regression.check(data)


# TODO: test some bad configurations
