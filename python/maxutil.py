#!/usr/bin/env python
import sys, re


#INF uttt_evaluate:experiment_uttt.py:186: Org[135]Epoch[0046]  error: 0.96500  fitness: 1.07123  utility: 0.03500
def main(fin):
    max_utility = {}
    max_fitness = {}
    for line in fin:
        words = line.strip().split()
        if len(words) >= 9:
            match = re.search('Org\[([0-9])+\]Epoch\[([0-9]+)\]', words[2])
            if match:
                org = match.group(1)
                epoch = match.group(2)
                if epoch not in max_utility:
                    max_utility[epoch] = 0.0
                    max_fitness[epoch] = 0.0
                max_utility[epoch] = max(max_utility[epoch], float(words[8]))
                max_fitness[epoch] = max(max_fitness[epoch], float(words[6]))
    #
    keys = max_utility.keys()
    keys.sort()
    for key in keys:
        print "%s fitness: %7.5f  utility: %7.5f" % (key, max_fitness[key], max_utility[key])

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

                
                
                
