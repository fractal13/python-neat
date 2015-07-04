PYTHON_MODULES := \
	experiments.py \
	experiment_xor.py

PYTHON_MAINS := \
	neatmain.py

all:
	@echo "hello"

test:
	-mkdir data/testout
	for f in $(PYTHON_MODULES); do \
		python $$f > data/testout/$$f.testout; \
	done

clean:
	-rm -f *~ *.pyc
	-rm -rf data/testout
	-rm -f data/gen/*



