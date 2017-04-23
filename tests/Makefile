PYTHON3_IS_36=`python3 -c 'import sys;print("Y" if sys.version_info >= (3,6)) else "F")`
ifeq ($(PYTHON3_IS_36),Y)
PYTHON=python3
else
PYTHON=python3.6
endif

test:
	$(PYTHON) -m nose2 -c 'nose2.discover()' --verbose --log-level ERROR

coverage:
	lcov -c -i -d ../src -o coverage-base
	lcov -c -d ../src -o coverage-run
	lcov -d ../src -a coverage-base -a coverage-run -o coverage-total
	genhtml --no-branch-coverage -o coverage-report coverage-total

.PHONY: test coverage
