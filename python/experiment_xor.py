from utils import matching_import
from debug import dprint
import debug
matching_import("DEBUG_.*", debug, globals())

import neat
from genome import Genome, print_Genome_tofile
from population import Population

#//Perform evolution on XOR, for gens generations
#Population *xor_test(int gens) {
def xor_test(gens):
    gene_filename = "xorstartgenes"
    
    pop = None
    start_genome = None
    
    #//Hold records for each run
    evals = [ 0 for i in range(neat.num_runs) ]
    genes = [ 0 for i in range(neat.num_runs) ]
    nodes = [ 0 for i in range(neat.num_runs) ]

    # Made as lists for pass-by-reference
    winnernum = [ 0 ]
    winnergenes = [ 0 ]
    winnernodes = [ 0 ]
    
    #//For averaging
    totalevals = 0
    totalgenes = 0
    totalnodes = 0

    iFile = open(gene_filename, "r")
    if not iFile:
        print "Unable to open starting genome file %s." % (gene_filename)
        return pop
    
    print "START XOR TEST"

    #//Read in the start Genome
    print "Reading in the start genome"
    line = iFile.readline()
    words = line.strip().split()
    curword = words[0]
    gid = int(words[1])
    if curword != "genomestart":
        print "Bad starting genome file %s." % (gene_filename, )
        return pop
        
    print "Reading in Genome id %d." % (gid,)
    start_genome = Genome()
    start_genome.SetFromFile(gid, iFile)
    iFile.close()
    
    print "Verifying start_genome"
    start_genome.verify()

    #Complete a number of runs
    for expcount in range(neat.num_runs):
        #//Spawn the Population
        print "Spawning Population off Genome2"
        pop = Population()
        pop.SetFromGenome(start_genome, neat.pop_size)
      
        print "Verifying Spawned Pop"
        if not pop.verify():
            dprint(DEBUG_ERROR, "Population verification failed")

        #// evolve up to gens generations
        for gen in range(1, gens+1):
            print "Epoch", gen
            generation_filename = "gen_%d" % (gen,)

            # Evaluate one generation, checking for a successful end
            #//Check for success
            if xor_epoch(pop, gen, generation_filename, winnernum, winnergenes, winnernodes):
                evals[expcount] = neat.pop_size * (gen-1) + winnernum[0]
                genes[expcount] = winnergenes[0]
                nodes[expcount] = winnernodes[0]
                break

        # end of generation loop
    # end of num_runs loop

    #//Average and print stats
    print "Nodes: "
    for expcount in range(neat.num_runs):
        print nodes[expcount]
        totalnodes += nodes[expcount]
    
    print "Genes: "
    for expcount in range(neat.num_runs):
        print genes[expcount]
        totalgenes += genes[expcount]
    
    print "Evals "
    samples = 0
    for expcount in range(neat.num_runs):
        print evals[expcount]
        if evals[expcount] > 0:
            totalevals += evals[expcount]
            samples += 1

    if samples > 0:
        avgnodes = float(totalnodes)/samples
        avggenes = float(totalgenes)/samples
        avgevals = float(totalevals)/samples
    else:
        avgnodes = 0
        avggenes = 0
        avgevals = 0
        
    print "Failures:", (neat.num_runs - samples), "out of", neat.num_runs, "runs"
    print "Average Nodes:", avgnodes
    print "Average Genes:", avggenes
    print "Average Evals:", avgevals

    return pop

# evaluates the Organism's performance on sample problems
# bool xor_evaluate(Organism *org) {
def xor_evaluate(org):
    outv = [ 0. for i in range(4) ]
    
    #//The four possible input combinations to xor
    #//The first number is for biasing
    inv = [ [ 1.0,0.0,0.0 ],
            [ 1.0,0.0,1.0 ],
            [ 1.0,1.0,0.0 ],
            [ 1.0,1.0,1.0 ] ]

    net = org.net
    dprint(DEBUG_INTEGRITY, "Network:", str(net))
    numnodes = len(org.gnome.nodes)
    net_depth = net.max_depth()

    #//Load and activate the network on each input
    for count in range(4):
        net.load_sensors(inv[count])

        #//Relax net and get output
        success = net.activate()

        #//use depth to ensure relaxation
        for relax in range(0, net_depth+1):
            success = net.activate()
            this_out = net.outputs[0].activation
            
        # record the output value
        outv[count] = net.outputs[0].activation
        
        # clear the network
        net.flush()

    # finished with input samples
    if success:
        errorsum = abs(float(outv[0])) + abs(1.0-outv[1]) + abs(1.0 - outv[2]) + abs(float(outv[3]))
        org.fitness = (4.0-errorsum) ** 2
        org.error = errorsum
    else:
        #//The network is flawed (shouldnt happen)
        errorsum = 999.0
        org.fitness = 0.001

    print "Org", org.gnome.genome_id, "                                    error:", errorsum, " [", outv[0], outv[1], outv[2], outv[3], "]"
    print "Org", org.gnome.genome_id, "                                    fitness:", org.fitness

    if outv[0] < 0.5 and outv[1] >= 0.5 and outv[2] >= 0.5 and outv[3] < 0.5:
        org.winner = True
        return True
    else:
        org.winner = False
        return False
    # end of xor_evaluate

# int xor_epoch(Population *pop,int generation,char *filename,int &winnernum,int &winnergenes,int &winnernodes) {
def xor_epoch(pop, generation, filename, winnernum, winnergenes, winnernodes):
    win = False

    #//Evaluate each organism on a test
    for curorg in pop.organisms:
        if xor_evaluate(curorg):
            win = True
            winnernum[0] = curorg.gnome.genome_id
            winnergenes[0] = curorg.gnome.extrons()
            winnernodes[0] = len(curorg.gnome.nodes)
            if winnernodes[0] == 5:
                #//You could dump out optimal genomes here if desired
                #//(*curorg)->gnome->print_to_filename("xor_optimal");
                pass
  
    #//Average and max their fitnesses for dumping to file and snapshot
    for curspecies in pop.species:
        #//This experiment control routine issues commands to collect ave
        #//and max fitness, as opposed to having the snapshot do it, 
        #//because this allows flexibility in terms of what time
        #//to observe fitnesses at
        curspecies.compute_average_fitness()
        curspecies.compute_max_fitness()


    #//Only print to file every print_every generations
    if win or ((generation % neat.print_every) == 0):
        pop.print_to_filename_by_species(filename)

    if win:
        for curorg in pop.organisms:
            if curorg.winner:
                print "WINNER IS #", curorg.gnome.genome_id
                #//Prints the winner to file
                #//IMPORTANT: This causes generational file output!
                print_Genome_tofile(curorg.gnome, "xor_winner")

    pop.epoch(generation)
    if win:
        return True
    else:
        return False

    # xor_epoch done
