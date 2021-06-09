# stdlib
import sys

# 3rd party
import dom_toml
import pytest
import southwark
from apeye import URL
from domdf_python_tools.paths import PathPlus, in_directory
from dulwich.config import StackedConfig
from dulwich.porcelain import clone
from whey import Foreman

# this package
from tests.example_configs import DESCRIPTION
from whey_conda import CondaBuilder


def test_info_dir(tmp_pathplus):

	(tmp_pathplus / "pyproject.toml").write_text(DESCRIPTION)

	with in_directory(tmp_pathplus):
		builder = CondaBuilder(tmp_pathplus, config=dom_toml.loads(DESCRIPTION)["project"])
		info_dir = builder.info_dir
		assert isinstance(info_dir, PathPlus)
		assert info_dir.exists()
		assert info_dir.is_dir()
		assert info_dir.relative_to(builder.build_dir)
		assert info_dir.name == "info"


GITHUB_COM = URL("https://github.com")


# @pypy_windows_dulwich
@pytest.mark.parametrize(
		"username, repository",
		[
				("sphinx-toolbox", "sphinx-toolbox"),
				("sphinx-toolbox", "default_values"),
				("repo-helper", "whey"),
				("domdfcoding", "consolekit"),
				("domdfcoding", "mathematical"),
				]
		)
def test_build(username, repository, tmp_pathplus, monkeypatch):
	# Monkeypatch dulwich so it doesn't try to use the global config.
	monkeypatch.setattr(StackedConfig, "default_backends", lambda *args: [])
	email = b"repo-helper[bot] <74742576+repo-helper[bot]@users.noreply.github.com>"
	monkeypatch.setattr(southwark.repo, "get_user_identity", lambda *args: email)

	target_dir = tmp_pathplus / f"{username}_{repository}"

	ret = 0
	target_dir = PathPlus(target_dir)

	url = GITHUB_COM / username / repository

	print("==============================================")
	print(f"Cloning {url!s} -> {target_dir!s}")

	clone(str(url), str(target_dir), depth=1)

	with in_directory(target_dir):
		foreman = Foreman(target_dir)
		foreman.config["builders"]["binary"] = CondaBuilder
		foreman.build_binary(verbose=True)

		sys.stdout.flush()

	# TODO: Install package
	# Run their tests
	# make_pyproject(target_dir, templates)
	# print((target_dir / "pyproject.toml").read_text())
	# test_process = Popen(["python3", "-m", "tox", "-n", "test"])
	# (output, err) = test_process.communicate()
	# exit_code = test_process.wait()
	# ret |= exit_code

	assert not ret
