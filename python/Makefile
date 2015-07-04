PYTHON_MODULES := \
	debug.py \
	experiments.py \
	experiment_xor.py \
	gene.py \
	genome.py \
	innovation.py \
	link.py \
	neat.py \
	network.py \
	nnode.py \
	organism.py \
	population.py \
	species.py \
	trait.py \
	utils.py

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



