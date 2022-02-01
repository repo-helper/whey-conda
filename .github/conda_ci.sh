set -ex

eval "$($CONDA/bin/conda shell.bash hook)"
$CONDA/bin/conda activate env

echo "Build and index channel"
$CONDA/bin/conda config --add channels conda-forge
$CONDA/bin/conda config --add channels domdfcoding

python -m whey --builder whey_conda --out-dir conda-bld/noarch
$CONDA/bin/conda index ./conda-bld

echo "Search for package"
$CONDA/bin/conda search -c file://$(pwd)/conda-bld whey-conda
$CONDA/bin/conda search -c file://$(pwd)/conda-bld --override-channels whey-conda

echo "Install package"
$CONDA/bin/conda install -c file://$(pwd)/conda-bld whey-conda=0.1.2=py_1 -y || exit 1

echo "Run Tests"
rm -rf whey_conda
$CONDA/bin/pip install -r tests/requirements.txt
$CONDA/bin/pytest tests/
