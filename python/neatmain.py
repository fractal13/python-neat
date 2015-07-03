import sys
import neat, experiments

def main():
    if len(sys.argv) != 2:
        print "A NEAT parameters file (.ne file) is required to run the experiments!"
        sys.exit(1)
        
    p = None # Population
    
    #//Load in the params
    neat.load_neat_params(sys.argv[1], True)

    print "Please choose an experiment: "
    print "1 - 1-pole balancing"
    print "2 - 2-pole balancing, velocity info provided"
    print "3 - 2-pole balancing, no velocity info provided (non-markov)"
    print "4 - XOR"
    choice = input("Number: ")

    if choice == 1:
        p = experiments.pole1_test(100)
    elif choice == 2:
        p = experiments.pole2_test(100, 1)
    elif choice == 3:
        p = experiments.pole2_test(100, 0)
    elif choice == 4:
        p = experiments.xor_test(100)
    else:
        print "Not an option."
        sys.exit(1)

    p = None
    return

if __name__ == "__main__":
    main()
