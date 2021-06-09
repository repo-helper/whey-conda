# 3rd party
import dom_toml
import pytest
from coincidence import AdvancedDataRegressionFixture
from dom_toml.parser import BadConfigError
from domdf_python_tools.paths import PathPlus

# this package
from whey_conda import WheyCondaParser


@pytest.mark.parametrize(
		"toml_config",
		[
				pytest.param('[tool.whey-conda]\nconda-description = "Fantastic Spam!"', id="description"),
				pytest.param('[tool.whey-conda]\nconda-extras = ["cli", "testing"]', id="extras"),
				pytest.param('[tool.whey-conda]\nconda-extras = "all"', id="extras_all"),
				pytest.param('[tool.whey-conda]\nconda-extras = "none"', id="extras_none"),
				pytest.param(
						'[tool.whey-conda]\nconda-channels = ["domdfcoding", "conda-forge"]', id="conda_channels"
						),
				]
		)
def test_whey_conda_parser_valid_config(
		toml_config: str,
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):
	(tmp_pathplus / "pyproject.toml").write_clean(toml_config)
	config = WheyCondaParser().parse(dom_toml.load(tmp_pathplus / "pyproject.toml")["tool"]["whey-conda"])
	advanced_data_regression.check(config)


@pytest.mark.parametrize(
		"toml_config", [
				pytest.param('[tool.whey-conda]\nconda-extras = "cli"', id="extras_cli"),
				]
		)
def test_whey_conda_parser_invalid_extras(
		toml_config: str,
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):

	with pytest.raises(BadConfigError, match=r"Invalid value for \[tool.whey-conda.conda-extras\]: "):
		WheyCondaParser().parse(dom_toml.loads(toml_config)["tool"]["whey-conda"])
