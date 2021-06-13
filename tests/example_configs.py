# 3rd party
from pyproject_examples import MINIMAL_CONFIG, OPTIONAL_DEPENDENCIES

COMPLETE_A = """\
[build-system]
requires = [ "whey",]
build-backend = "whey"

[project]
name = "whey"
version = "2021.0.0"
description = "A simple Python wheel builder for simple projects."
keywords = [ "pep517", "pep621", "build", "sdist", "wheel", "packaging", "distribution",]
dynamic = [ "classifiers", "requires-python",]
readme = "README.rst"
dependencies = [
  "httpx",
  "gidgethub[httpx]>4.0.0",
  "django>2.1; os_name != 'nt'",
  "django>2.0; os_name == 'nt'"
]

[project.license]
file = "LICENSE"

[[project.authors]]
email = "dominic@davis-foster.co.uk"
name = "Dominic Davis-Foster"

[project.urls]
Homepage = "https://whey.readthedocs.io/en/latest"
Documentation = "https://whey.readthedocs.io/en/latest"
"Issue Tracker" = "https://github.com/repo-helper/whey/issues"
"Source Code" = "https://github.com/repo-helper/whey"

[tool.whey]
base-classifiers = [ "Development Status :: 4 - Beta",]
python-versions = [ "3.6", "3.7", "3.8", "3.9", "3.10",]
python-implementations = [ "CPython", "PyPy",]
platforms = [ "Windows", "macOS", "Linux",]
license-key = "MIT"
"""

COMPLETE_B = """\
[build-system]
requires = [ "whey",]
build-backend = "whey"

[project]
name = "Whey"
version = "2021.0.0"
description = "A simple Python wheel builder for simple projects."
readme = "README.rst"
keywords = [ "pep517", "pep621", "build", "sdist", "wheel", "packaging", "distribution",]
dynamic = [ "classifiers", "requires-python",]
dependencies = [
  "httpx",
  "gidgethub[httpx]>4.0.0",
  "django>2.1; os_name != 'nt'",
  "django>2.0; os_name == 'nt'"
]

[project.license]
file = "LICENSE"

[[project.authors]]
email = "dominic@davis-foster.co.uk"
name = "Dominic Davis-Foster"

[project.urls]
Homepage = "https://whey.readthedocs.io/en/latest"
"Home Page" = "https://whey.readthedocs.io/en/latest"
Documentation = "https://whey.readthedocs.io/en/latest"
"Issue Tracker" = "https://github.com/repo-helper/whey/issues"
"Source Code" = "https://github.com/repo-helper/whey"

[tool.whey]
base-classifiers = [ "Development Status :: 4 - Beta",]
python-versions = [ "3.6", "3.7", "3.8", "3.9", "3.10",]
python-implementations = [ "CPython", "PyPy",]
platforms = [ "Windows", "macOS", "Linux",]
license-key = "MIT"
package = "whey"
"""

CONDA_DESCRIPTION = f"""
{MINIMAL_CONFIG}
description = "Lovely Spam! Wonderful Spam!"

[tool.whey-conda]
conda-description = "Fantastic Spam!"
"""

CONDA_EXTRAS = f"""
{OPTIONAL_DEPENDENCIES}

[tool.whey-conda]
conda-extras = ["test"]
"""

CONDA_EXTRAS_ALL = f"""
{OPTIONAL_DEPENDENCIES}

[tool.whey-conda]
conda-extras = "all"
"""

CONDA_EXTRAS_EXPLICIT_NONE = f"""
{OPTIONAL_DEPENDENCIES}

[tool.whey-conda]
conda-extras = "None"
"""

MKRECIPE_EXTRAS = f"""
{OPTIONAL_DEPENDENCIES}

[tool.mkrecipe]
extras = ["test"]
"""

MKRECIPE_EXTRAS_ALL = f"""
{OPTIONAL_DEPENDENCIES}

[tool.mkrecipe]
extras = "all"
"""

CONDA_CHANNELS = f"""
{MINIMAL_CONFIG}
dependencies = [
  "domdf_python_tools",
  "typing-extensions>=3.10.0.0",
]

[tool.whey-conda]
conda-channels = ["conda-forge", "domdfcoding"]
"""

MKRECIPE_CHANNELS = f"""
{MINIMAL_CONFIG}
dependencies = [
  "domdf_python_tools",
  "typing-extensions>=3.10.0.0",
]

[tool.mkrecipe]
conda-channels = ["conda-forge", "domdfcoding"]
"""

BOTH_CHANNELS = f"""
{MINIMAL_CONFIG}
dependencies = [
  "domdf_python_tools",
  "typing-extensions>=3.10.0.0",
]

[tool.mkrecipe]
conda-channels = ["domdfcoding"]

[tool.whey-conda]
conda-channels = ["conda-forge", "domdfcoding"]
"""

BOTH_CHANNELS2 = f"""
{MINIMAL_CONFIG}
dependencies = [
  "domdf_python_tools",
  "typing-extensions>=3.10.0.0",
]

[tool.mkrecipe]
conda-channels = ["conda-forge", "domdfcoding"]

[tool.whey-conda]
"""

DESCRIPTION = f"""
{MINIMAL_CONFIG}
description = "Lovely Spam! Wonderful Spam!"
"""
