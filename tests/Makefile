PYTHON3_IS_36=`python3 -c 'import sys;print("Y" if sys.version_info >= (3,6)) else "F")`
ifeq ($(PYTHON3_IS_36),Y)
PYTHON=python3
else
PYTHON=python3.6
endif

test:
	$(PYTHON) -m unittest discover -b -v -p '*_test.py'
