# stdlib
import datetime
from typing import Iterator

# 3rd party
import pytest
from coincidence import AdvancedFileRegressionFixture, with_fixed_datetime

# this package
from tests.utils import TarFileRegressionFixture

pytest_plugins = ("coincidence", )


@pytest.fixture()
def tar_regression(datadir, original_datadir, request) -> AdvancedFileRegressionFixture:  # noqa: MAN001
	return TarFileRegressionFixture(datadir, original_datadir, request)


@pytest.fixture()
def fixed_datetime() -> Iterator:
	with with_fixed_datetime(datetime.datetime.fromtimestamp(1602552000.0)):
		yield
