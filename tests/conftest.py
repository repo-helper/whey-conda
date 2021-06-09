# 3rd party
import pytest
from coincidence import AdvancedFileRegressionFixture

# this package
from tests.utils import TarFileRegressionFixture

pytest_plugins = ("coincidence", )


@pytest.fixture()
def tar_regression(datadir, original_datadir, request) -> AdvancedFileRegressionFixture:
	return TarFileRegressionFixture(datadir, original_datadir, request)
