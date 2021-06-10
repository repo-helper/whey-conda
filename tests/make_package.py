# stdlib
import sys

# 3rd party
from whey.foreman import Foreman

# this package
from whey_conda import CondaBuilder

foreman = Foreman(sys.argv[1])
foreman.config["builders"]["binary"] = CondaBuilder
print(foreman.build_binary(verbose=True, out_dir=f"{sys.argv[1]}/conda-bld/noarch"))
