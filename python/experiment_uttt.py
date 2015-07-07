import sys, os
sys.path.append(".")
from neat.utils import matching_import
from neat.debug import dprint
from neat import debug as debug
matching_import("DEBUG_.*", debug, globals())
import neat
#neat.debug.debug_level = neat.debug.debug_level | neat.debug.DEBUG_FILEINPUT
from neat import Genome, print_Genome_tofile, Population
import neat.neat as neatconfig

g_found_optimal = False

#//Perform evolution on UTTT, for gens generations
def uttt_test(gens):
    gene_filename = neatconfig.genedir + "/utttstartgenes"
    
    pop = None
    start_genome = None
    
    #//Hold records for each run
    evals = [ 0 for i in range(neatconfig.num_runs) ]
    genes = [ 0 for i in range(neatconfig.num_runs) ]
    nodes = [ 0 for i in range(neatconfig.num_runs) ]

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
        dprint(DEBUG_ERROR, "Unable to open starting genome file %s." % (gene_filename, ))
        return pop
    
    dprint(DEBUG_INFO, "START UTTT TEST")

    #//Read in the start Genome
    dprint(DEBUG_INFO, "Reading in the start genome")
    line = iFile.readline()
    words = line.strip().split()
    curword = words[0]
    gid = int(words[1])
    if curword != "genomestart":
        dprint(DEBUG_ERROR, "Bad starting genome file %s." % (gene_filename, ))
        return pop
        
    dprint(DEBUG_INFO, "Reading in Genome id %d." % (gid,))
    start_genome = Genome()
    start_genome.SetFromFile(gid, iFile)
    iFile.close()
    
    dprint(DEBUG_INFO, "Verifying start_genome")
    if not start_genome.verify():
        dprint(DEBUG_ERROR, "genome.verify() failed:", start_genome.deep_string())

    #Complete a number of runs
    for expcount in range(neatconfig.num_runs):
        #//Spawn the Population
        dprint(DEBUG_INFO, "Spawning Population off Genome")
        pop = Population()
        pop.SetFromGenome(start_genome, neatconfig.pop_size)
      
        dprint(DEBUG_INFO, "Verifying Spawned Population[%d]" % (expcount, ))
        if not pop.verify():
            dprint(DEBUG_ERROR, "Population[%d] verification failed" % (expcount, ))

        #// evolve up to gens generations
        for gen in range(1, gens+1):
            dprint(DEBUG_INFO, "Verifying Spawned Population[%d] Epoch[%d]" % (expcount, gen))
            if not pop.verify():
                dprint(DEBUG_ERROR, "Population[%d] Epoch[%d] verification failed" % (expcount, gen))

            #print "Epoch", gen
            generation_filename = neatconfig.generationdir + "/utttgen_%d" % (gen,)

            # Evaluate one generation, checking for a successful end
            #//Check for success
            if uttt_epoch(pop, gen, generation_filename, winnernum, winnergenes, winnernodes):
                evals[expcount] = neatconfig.pop_size * (gen-1) + winnernum[0]
                genes[expcount] = winnergenes[0]
                nodes[expcount] = winnernodes[0]
                break

        # end of generation loop
        if g_found_optimal:
            break
    # end of num_runs loop

    #//Average and print stats
    dprint(DEBUG_INFO, "Nodes: ")
    for expcount in range(neatconfig.num_runs):
        dprint(DEBUG_INFO, nodes[expcount])
        totalnodes += nodes[expcount]
    
    dprint(DEBUG_INFO, "Genes: ")
    for expcount in range(neatconfig.num_runs):
        dprint(DEBUG_INFO, genes[expcount])
        totalgenes += genes[expcount]
    
    dprint(DEBUG_INFO, "Evals ")
    samples = 0
    for expcount in range(neatconfig.num_runs):
        dprint(DEBUG_INFO, evals[expcount])
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
        
    dprint(DEBUG_INFO, "Failures:", (neatconfig.num_runs - samples), "out of", neatconfig.num_runs, "runs")
    dprint(DEBUG_INFO, "Average Nodes:", avgnodes)
    dprint(DEBUG_INFO, "Average Genes:", avggenes)
    dprint(DEBUG_INFO, "Average Evals:", avgevals)

    return pop

# evaluates the Organism's performance on sample problems
# bool uttt_evaluate(Organism *org) {
def uttt_evaluate(org):
    #
    # Run this network, and get its fitness value
    #
    prog_dir = "uttt"
    pwd = os.getcwd()
    os.chdir(prog_dir)
    org.gnome.print_to_filename("genome.txt")

    from multiprocessing import Process, Queue
    import uttt_main
    
    #cmd1 = "python ./uttt_main.py --user lisa --password foobar --ai --no-gui --results-file 'results.txt' --genome-file 'genome.txt' --ai-type 'genomelearn'"
    cmd1_argv = [ './uttt_main.py', '--user', 'lisa', '--password', 'foobar', '--ai', 'full',
                  '--no-gui',
                  '--results-file', 'results.txt',
                  '--genome-file', 'genome.txt', '--ai-type', 'genomelearn' ]
    #cmd2 = "python ./uttt_main.py --user fred --password dino123 --ai --ai-level 5 --no-gui --ai-type 'minimax'"
    cmd2_argv = [ './uttt_main.py', '--user', 'fred', '--password', 'dino123', '--ai', 'full',
                  '--ai-level', '5', '--no-gui', '--ai-type', 'minimax' ]
    # run two child processes, and wait for result

    ### Spawn children to play the game
    processes = []
    t = Process(target=uttt_main.main, args=(cmd1_argv,))
    t.start()

    u = Process(target=uttt_main.main, args=(cmd2_argv,))
    u.start()
    
    # wait for end of processes
    t.join()
    u.join()
    ### Done with spawn children
    

    #
    fin = open("results.txt", "r")
    board_utility = float(fin.readline().strip())
    fin.close()
    os.chdir(pwd)

    #
    # rank the organism
    # -1.0 <= board_utility <= 1.0
    # 0.0 <= errorsum <= 2.0
    errorsum = abs(1.0 - board_utility)
    org.fitness = (2.0 - errorsum) ** 2
    org.error = errorsum

    dprint(DEBUG_INFO, "Org", org.gnome.genome_id,
           " error: %7.5f  fitness: %7.5f  utility: %7.5f" % (errorsum, org.fitness, board_utility))

    if org.fitness >= 3.9:
        org.winner = True
        return True
    else:
        org.winner = False
        return False
    # end of uttt_evaluate

# int uttt_epoch(Population *pop,int generation,char *filename,int &winnernum,int &winnergenes,int &winnernodes) {
def uttt_epoch(pop, generation, filename, winnernum, winnergenes, winnernodes):
    win = False

    #//Evaluate each organism on a test
    for curorg in pop.organisms:
        if uttt_evaluate(curorg):
            win = True
            winnernum[0] = curorg.gnome.genome_id
            winnergenes[0] = curorg.gnome.extrons()
            winnernodes[0] = len(curorg.gnome.nodes)
            if winnernodes[0] == 163:
                #//You could dump out optimal genomes here if desired
                curorg.gnome.print_to_filename(neatconfig.genedir + "/uttt_optimal");
                global g_found_optimal
                g_found_optimal = True
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
    if win or ((generation % neatconfig.print_every) == 0):
        pop.print_to_filename_by_species(filename)

    if win:
        for curorg in pop.organisms:
            if curorg.winner:
                dprint(DEBUG_INFO, "WINNER IS #", curorg.gnome.genome_id)
                #//Prints the winner to file
                #//IMPORTANT: This causes generational file output!
                print_Genome_tofile(curorg.gnome, neatconfig.genedir + "/uttt_winner")

    if win:
        return True
    else:
        # only evolve if not done
        dprint(DEBUG_INFO, "Creating next generation.")
        pop.epoch(generation)
        dprint(DEBUG_INFO, "Creating next generation - done.")
        return False

    # utt_epoch done

def main():
    neat.load_neat_params(neatconfig.configdir + "/uttt.ne", True)
    p = uttt_test(100)
    p = None
    return
    
if __name__ == "__main__":
    main()

