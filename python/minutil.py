#!/usr/bin/env python
import sys, re


#INF uttt_evaluate:experiment_uttt.py:186: Org[135]Epoch[0046]  error: 0.96500  fitness: 1.07123  utility: 0.03500
def main(fin):
    min_utility = {}
    min_fitness = {}
    for line in fin:
        words = line.strip().split()
        if len(words) >= 9:
            match = re.search('Org\[([0-9])+\]Epoch\[([0-9]+)\]', words[2])
            if match:
                org = match.group(1)
                epoch = match.group(2)
                if epoch not in min_utility:
                    min_utility[epoch] = 99999999.0
                    min_fitness[epoch] = 99999999.0
                min_utility[epoch] = min(min_utility[epoch], float(words[8]))
                min_fitness[epoch] = min(min_fitness[epoch], float(words[6]))
    #
    keys = min_utility.keys()
    keys.sort()
    for key in keys:
        print "%s fitness: %7.5f  utility: %7.5f" % (key, min_fitness[key], min_utility[key])

if __name__ == "__main__":
    if len(sys.argv) == 1:
        fin = sys.stdin
    else:
        fin = open(sys.argv[1], "r")
        if not fin:
            print "Unable to open:", sys.argv[1]
            sys.exit(1)
    main(fin)
    fin.close()

                
                
                
