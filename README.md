# Rubik3Matrix
This project tries to find solutions of a given cube
with a given number of moves using matrices for moves

## Execution instructions
First clone the git repository to your machine and then execute this command in terminal: 

Go to project root

_pip install -r requirements.txt_

To execute the cube solver run this command:

_python rubik3_matrix_main.py_

To try the performed tests, run this command:

_python -m pytest_

## run the single modules

_python -m src.Moves.Moves_
_python -m src.Matrix.Matrix_

### Linux
_python tests/test_moves.py_
_python tests/test_matrix.py_

### Windows
_python tests\test_moves.py_
_python tests\test_matrix.py_

## test coverage

_coverage erase_
_coverage run -m pytest_

### Linux
_coverage html --omit */tests/* && open ./htmlcov/index.html_
or
_coverage html --omit */tests/* && firefox ./htmlcov/index.html_

### Windows
'/' and '\' allowed
_coverage html --omit */tests/* && start firefox .\htmlcov\index.html_

## Local testing any python module

add local project main directory to PYTHONPATH eg.

_export PYTHONPATH=~/python_projects/Rubik3Matrix_

now you can start any module with python <module>.py
