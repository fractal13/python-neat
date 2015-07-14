import sys, os, re
sys.path.append(".")
from neat.utils import matching_import
from neat.debug import dprint
from neat import debug as debug
matching_import("DEBUG_.*", debug, globals())
import neat
#neat.debug.debug_level = neat.debug.debug_level | neat.debug.DEBUG_FILEINPUT
from neat import Genome, print_Genome_tofile, Population
from neat.species import order_species_key
import neat.neat as neatconfig
from multiprocessing import Process, Queue

g_found_optimal = False

#//Perform evolution on UTTT, for gens generations
def uttt_test(config):
    gens = config['max_generations']
    
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
    
    dprint(DEBUG_INFO, "START UTTT TEST")

    if config['seed_with_start_genome']:
        gene_filename = neatconfig.genedir + "/utttstartgenes"
        iFile = open(gene_filename, "r")
        if not iFile:
            dprint(DEBUG_ERROR, "Unable to open starting genome file %s." % (gene_filename, ))
            return pop
    

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
        
        if config['seed_with_start_genome']:
        
            #//Spawn the Population
            dprint(DEBUG_INFO, "Spawning Population off Genome")
            pop = Population()
            pop.SetFromGenome(start_genome, neatconfig.pop_size)
            
            dprint(DEBUG_INFO, "Verifying Spawned Population[%d]" % (expcount, ))
            if not pop.verify():
                dprint(DEBUG_ERROR, "Population[%d] verification failed" % (expcount, ))
                
        elif config['seed_with_previous_population']:
            population_filename = neatconfig.genedir + "/" + config['previous_population_file']
            dprint(DEBUG_INFO, "Reading Population from %s" % (population_filename, ))
            pop = Population()
            pop.SetFromFilename(population_filename)
            
            dprint(DEBUG_INFO, "Verifying Start Population[%d]" % (expcount, ))
            if not pop.verify():
                dprint(DEBUG_ERROR, "Population[%d] verification failed" % (expcount, ))


        #// evolve up to gens generations
        gen = 1
        while gen <= gens:
            dprint(DEBUG_INFO, "Evaluating Spawned Population[%d] Epoch[%d]" % (expcount, gen))
            # if not pop.verify():
            #     dprint(DEBUG_ERROR, "Population[%d] Epoch[%d] verification failed" % (expcount, gen))

            #print "Epoch", gen
            generation_filename = neatconfig.generationdir + "/utttgen_%d" % (gen,)

            # Evaluate one generation, checking for a successful end
            #//Check for success
            if uttt_epoch(pop, gen, generation_filename, winnernum, winnergenes, winnernodes):
                evals[expcount] = neatconfig.pop_size * (gen-1) + winnernum[0]
                genes[expcount] = winnergenes[0]
                nodes[expcount] = winnernodes[0]
                break

            # in case we want to change after run has started
            config = uttt_read_config(neatconfig.configdir + '/uttt.config')
            gens = config['max_generations']
            gen += 1

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
def uttt_evaluate(org, generation, config):
    
    #
    # Run this network, and get its fitness value
    #
    prog_dir = config['program_directory']
    pwd = os.getcwd()
    os.chdir(prog_dir)
    import uttt_main

    # repeat until a successful run is made
    do_evaluate = True
    while do_evaluate:
        results_file = config['results_file']
        genome_file = config['genome_file']
        if os.path.exists(results_file):
            os.remove(results_file)
        if os.path.exists(genome_file):
            os.remove(genome_file)

        org.gnome.print_to_filename(genome_file)

        cmd1_argv = [ config['program'],
                      '--user', config['user1'],
                      '--password', config['password1'],
                      '--ai', 'full',
                      '--no-gui',
                      '--results-file', config['results_file'],
                      '--genome-file', config['genome_file'],
                      '--ai-type', 'genomelearn' ]

        cmd2_argv = [ config['program'],
                      '--user', config['user2'],
                      '--password', config['password2'],
                      '--ai', 'full',
                      '--ai-level', config['minimax_level'],
                      '--no-gui',
                      '--ai-type', 'minimax' ]
        # run two child processes, and wait for result

        ### Spawn children to play the game
        processes = []
        t = Process(target=uttt_main.main, args=(cmd1_argv,))
        t.start()

        if config['spawn_opponent']:
            u = Process(target=uttt_main.main, args=(cmd2_argv,))
            u.start()

        # wait for end of processes
        t.join()
        if config['spawn_opponent']:
            u.join()
        ### Done with spawn children

        #
        fin = open(results_file, "r")
        if fin:
            board_utility = float(fin.readline().strip())
            fin.close()
            do_evaluate = False
        else:
            board_utility = 0.0
            do_evaluate = True
        #
        if os.path.exists(results_file):
            os.remove(results_file)
        if os.path.exists(genome_file):
            os.remove(genome_file)
        # end of while do_evaluate
    os.chdir(pwd)

    #
    # rank the organism
    # -1.0 <= board_utility <= 1.0
    # 0.0 <= errorsum <= 2.0
    errorsum = abs(1.0 - board_utility)
    org.fitness = (2.0 - errorsum) ** 2
    org.error = errorsum

    dprint(DEBUG_INFO, "Org[%03d]Epoch[%04d]" % (int(org.gnome.genome_id), int(generation)),
           " error: %7.5f  fitness: %7.5f  utility: %7.5f" % (errorsum, org.fitness, board_utility))

    if org.fitness >= float(config['win_fitness']):
        org.winner = True
        return True
    else:
        org.winner = False
        return False
    # end of uttt_evaluate

# int uttt_epoch(Population *pop,int generation,char *filename,int &winnernum,int &winnergenes,int &winnernodes) {
def uttt_epoch(pop, generation, filename, winnernum, winnergenes, winnernodes):
    win = False
    # reread every epoch to all opponent settings to change over time if desired.
    config = uttt_read_config(neatconfig.configdir + '/uttt.config')
    #//Evaluate each organism on a test
    for curorg in pop.organisms:
        if uttt_evaluate(curorg, generation, config):
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

    if debug.is_set(DEBUG_CHECK):
        sorted_species = [ curspecies for curspecies in pop.species ]
        sorted_species.sort(key=order_species_key)
        for curspecies in sorted_species:
            dprint(DEBUG_CHECK, "Species[%d] avefit: %7.5f maxfit: %7.5f age: %4.1f lastimprove: %4.1f numorg: %d" % \
                   (int(curspecies.id), float(curspecies.ave_fitness), float(curspecies.max_fitness),
                    float(curspecies.age), float(curspecies.age_of_last_improvement), len(curspecies.organisms)))

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

def uttt_read_config(config_file):
    float_params = [ 'win_fitness', ]
    int_params = [ 'minimax_level',
                   'max_generations' ]
    bool_params = [ 'spawn_opponent',
                    'seed_with_start_genome',
                    'seed_with_previous_population', ]
    str_params = [ 'program_directory',
                   'results_file',
                   'genome_file',
                   'program',
                   'user1', 'password1',
                   'user2', 'password2',
                   'previous_population_file', ]

    config = { 'program_directory' : 'uttt',
               'results_file': 'results.txt',
               'genome_file': 'genome.txt',
               'program': './uttt_main.py',
               'user1': 'lisa',
               'password1': 'foobar',
               'user2': 'fred',
               'password2': 'dino123',
               'minimax_level': '1',
               'max_generations': '1000',
               'win_fitness': '4.01',
               'spawn_opponent': True,
               'seed_with_start_genome': True,
               'seed_with_previous_population': False,
               'previous_population_file': "",
           }
    fin = open(config_file, "r")
    if fin:
        for line in fin:
            line = line.strip()
            if line == "":
                continue
            if re.search('^\s*#', line):
                continue
            words = line.split()
            if len(words) != 2:
                dprint(DEBUG_ERROR, "Unknown uttt config parameter line: %" % (line, ))
                continue
            param_name = words[0]
            value = words[1]
            if param_name not in config:
                dprint(DEBUG_ERROR, "Unknown uttt config parameter: %" % (param_name, ))
                continue

            if param_name in float_params:
                value = float(value)
            elif param_name in int_params:
                value = int(value)
            elif param_name in bool_params:
                value = neatconfig.str_to_bool(value)
            elif param_name in str_params:
                value = str(value)
            else:
                dprint(DEBUG_ERROR, "Unknown uttt config parameter type %s" % (param_name, ))
            config[param_name] = value
        
        fin.close()
    else:
        dprint(DEBUG_ERROR, "Unable to open uttt config file %s." % (config_file, ))
        
    return config
    
def main():
    config = uttt_read_config(neatconfig.configdir + '/uttt.config')

    # dprint(DEBUG_INFO, "testing population read from file - start")
    # neat.debug.debug_level = neat.debug.debug_level | neat.debug.DEBUG_FILEINPUT
    # population_filename = neatconfig.genedir + "/" + config['previous_population_file']
    # dprint(DEBUG_INFO, "Reading Population from %s" % (population_filename, ))
    # pop = Population()
    # pop.SetFromFilename(population_filename)
    # dprint(DEBUG_INFO, "testing population read from file - end")

    # return
    
    neat.load_neat_params(neatconfig.configdir + "/uttt.ne", True)
    p = uttt_test(config)
    p = None
    return
    
if __name__ == "__main__":
    main()

