from utils import matching_import
from debug import dprint
import debug
matching_import("DEBUG_.*", debug, globals())
import neat
from genome import Genome
from organism import Organism
from species import Species, order_species_key
import re

class Population:


    def __init__(self):
        # 	// ******* Organisms and Species of the Population *******
        self.organisms = [] # std::vector<Organism*> organisms; //The organisms in the Population
        self.species = [] # std::vector<Species*> species;  // Species in the Population. Note that the species should comprise all the genomes 

	# 	// ******* Member variables used during reproduction *******
        self.innovations = [] # std::vector<Innovation*> innovations;  // For holding the genetic innovations of the newest generation
        self.cur_node_id = 0 # 	int cur_node_id;  //Current label number available
	self.cur_innov_num = 0.0 # 	double cur_innov_num;
	self.last_species = 0 # 	int last_species;  //The highest species number

	# 	// ******* Fitness Statistics *******
	self.mean_fitness = 0.0 # 	double mean_fitness;
	self.variance = 0.0 # 	double variance;
	self.standard_deviation = 0.0 # 	double standard_deviation;
	self.winnergen = 0 # 	int winnergen; //An integer that when above zero tells when the first winner appeared

	# 	// ******* When do we need to delta code? *******
	self.highest_fitness = 0.0 # 	double highest_fitness;  //Stagnation detector
	self.highest_last_changed = 0 # 	int highest_last_changed; //If too high, leads to delta coding

        return


    #// Construct off of a single spawning Genome 
    # Population(Genome *g,int size);
    def SetFromGenome(self, g, size):
        self.winnergen = 0
        self.highest_fitness = 0.0
        self.highest_last_changed = 0
        self.spawn(g, size)
        return

    #// Construct off of a single spawning Genome without mutation
    # Population(Genome *g,int size, float power);
    def SetFromGenomeAndPower(self, g, size, power):
 	self.winnergen = 0
        self.highest_fitness = 0.0
        self.highest_last_changed = 0
        self.clone(g, size, power)
        return


    #//MSC Addition
    #// Construct off of a vector of genomes with a mutation rate of "power"
    # //Added the ability for a population to be spawned
    # //off of a vector of Genomes.  Useful when converging.
    # Population(std::vector<Genome*> genomeList, float power);
    def SetFromGenomes(self, genomeList, power):
        self.winnergen = 0
        self.highest_fitness = 0.0
        self.highest_last_changed = 0
		
        #//Create size copies of the Genome
        #//Start with perturbed linkweights
        for new_genome in genomeList:
            if power > 0:
                new_genome.mutate_link_weights(power, 1.0, Genome.GAUSSIAN)
            new_genome.randomize_traits()
            new_organism = Organism()
            new_organism.SetFromGenome(0.0, new_genome, 1)
            self.organisms.append(new_organism)
        #

        #//Keep a record of the innovation and node number we are on
        self.cur_node_id = new_genome.get_last_node_id()
        self.cur_innov_num = new_genome.get_last_gene_innovnum()

        #//Separate the new Population into species
        self.speciate()
        return

    #// Construct off of a file of Genomes 
    # Population(const char *filename);
    def SetFromFilename(self, filename):
        self.winnergen = 0
        self.highest_fitness = 0.0
        self.highest_last_changed = 0
        self.cur_node_id = 0
        self.cur_innov_num = 0.0
        curwordnum = 0

        dprint(DEBUG_FILEINPUT, "Opening population file %s." % (filename, ))
        iFile = open(filename, "r")
        if not iFile:
            dprint(DEBUG_ERROR, "Can't open genomes file for input %s." % (filename, ))
            return

        md = False
        metadata = ""
        #//Loop until file is finished, parsing each line
        while True:
            curline = iFile.readline()
            if not curline:
                break
            dprint(DEBUG_FILEINPUT, "line: %s." % (curline.strip(), ))
            words = curline.strip().split()
            dprint(DEBUG_FILEINPUT, "words: %s." % (":".join(words), ))
            if len(words) == 0:
                continue
            if re.search('^\s*#', words[0]):
                continue
            if words[0] == "genomestart":
                dprint(DEBUG_FILEINPUT, "genomestart")
                idcheck = int(words[1])
                if not md:
                    metadata = ""
                md = False
                new_genome = Genome()
                new_genome.SetFromFile(idcheck, iFile)
                new_organism = Organism()
                new_organism.SetFromGenome(0., new_genome, 1, metadata)
                self.organisms.append(new_organism)
                if self.cur_node_id < new_genome.get_last_node_id():
                    self.cur_node_id = new_genome.get_last_node_id()
                if self.cur_innov_num < new_genome.get_last_gene_innovnum():
                    self.cur_innov_num = new_genome.get_last_gene_innovnum()
            elif words[0] == "/*":
                #// New metadata possibly, so clear out the metadata
                metadata = ""
                word_i = 1
                while words[word_i] != "*/":
                    #// If we've started to form the metadata, put a space in the front
                    if md:
                        metadata += " "
                    metadata += words[word_i]
                    md = True
                    word_i += 1
            # end of conditional processing
        # end of while True
        dprint(DEBUG_FILEINPUT, "End of file.")
        iFile.close()
        self.speciate()
        dprint(DEBUG_FILEINPUT, "Done.")
        return

    #// Run verify on all Organisms in this Population (Debugging)
    # bool verify();
    def verify(self):
        verification = True
        for curorg in self.organisms:
            if not curorg.verify():
                dprint(DEBUG_ERROR, "Organism verification failed.")
                verification = False
        return verification

    # bool clone(Genome *g,int size, float power);
    def clone(self, g, size, power):
        new_genome = g.duplicate(1)
        new_organism = Organism()
        new_organism.SetFromGenome(0.0, new_genome, 1)
        self.organisms.append(new_organism)
        
        #//Create size copies of the Genome
        #//Start with perturbed linkweights
        for count in range(2, size+1):
            new_genome = g.duplicate(count)
            if power > 0:
                new_genome.mutate_link_weights(power, 1.0, Genome.GAUSSIAN)
            new_genome.randomize_traits()
            new_organism = Organism()
            new_organism.SetFromGenome(0.0, new_genome, 1)
            self.organisms.append(new_organism)
        #
	
        #//Keep a record of the innovation and node number we are on
        self.cur_node_id = new_genome.get_last_node_id()
        self.cur_innov_num = new_genome.get_last_gene_innovnum()

        #//Separate the new Population into species
        self.speciate()

        return True

    #// A Population can be spawned off of a single Genome 
    #// There will be size Genomes added to the Population 
    #// The Population does not have to be empty to add Genomes 
    # bool spawn(Genome *g,int size);
    def spawn(self, g, size):
        
        #//Create size copies of the Genome
        #//Start with perturbed linkweights
        for count in range(1, size+1):
            dprint(DEBUG_INFO, "Creating organism %d" % (count, ))
            new_genome = g.duplicate(count)
            new_genome.mutate_link_weights(1.0, 1.0, Genome.COLDGAUSSIAN)
            new_genome.randomize_traits()
            new_organism = Organism()
            new_organism.SetFromGenome(0.0, new_genome, 1)
            self.organisms.append(new_organism)
        #
        
        #//Keep a record of the innovation and node number we are on
        self.cur_node_id = new_genome.get_last_node_id()
        self.cur_innov_num = new_genome.get_last_gene_innovnum()

        #//Separate the new Population into species
        self.speciate()

        return True


    #// Separate the Organisms into species
    # bool speciate();
    def speciate(self):
        comporg = None
        counter = 0

        #//Step through all existing organisms
        for curorg in self.organisms:
            #//For each organism, search for a species it is compatible to
            cur_species_i = 0
            if cur_species_i >= len(self.species):
                newspecies = Species()
                counter += 1
                newspecies.SetFromId(counter)
                self.species.append(newspecies)
                newspecies.add_Organism(curorg)
                curorg.species = newspecies
            else:
                curspecies = self.species[cur_species_i]
                comporg = curspecies.first()
                while (comporg is not None) and (cur_species_i < len(self.species)):
                    if curorg.gnome.compatibility(comporg.gnome) < neat.compat_threshold:
                        #//Found compatible species, so add this organism to it
                        curspecies.add_Organism(curorg)
                        curorg.species = curspecies
                        comporg = None  #//Note the search is over
                    else:
                        #//Keep searching for a matching species
                        cur_species_i += 1
                        if cur_species_i < len(self.species):
                            curspecies = self.species[cur_species_i]
                            comporg = curspecies.first()
                # end while looking for species
                #//If we didn't find a match, create a new species
                if comporg is not None:
                    newspecies = Species()
                    counter += 1
                    newspecies.SetFromId(counter)
                    self.species.append(newspecies)
                    newspecies.add_Organism(curorg)
                    curorg.species = newspecies
            # end species search conditions
        # end organism loop
        self.last_species = counter
        return True

    #// Print Population to a file in speciated order with comments separating each species
    #bool print_to_filename_by_species(char *filename);
    def print_to_filename_by_species(self, filename):
        outFile = open(filename, "w")
        if not outFile:
            dprint(DEBUG_ERROR, "Can't open %s for output." % (filename,))
            return False
        self.print_to_file_by_species(outFile)
        outFile.close()
        return True

    #// Print Population to a file in speciated order with comments separating each species
    # bool print_to_file_by_species(std::ostream& outFile);
    def print_to_file_by_species(self, outFile):
        for curspecies in self.species:
            curspecies.print_to_file(outFile)
        return True

    #// Turnover the population to a new generation using fitness 
    #// The generation argument is the next generation
    #bool epoch(int generation);
    def epoch(self, generation):
        total = 0.0 #//Used to compute average fitness over all Organisms
        
        #//The fractional parts of expected offspring that can be 
        #//Used only when they accumulate above 1 for the purposes of counting
        #//Offspring
        skim = 0.
        total_organisms = len(self.organisms)
        
        #//Rights to make babies can be stolen from inferior species
        #//and given to their superiors, in order to concentrate exploration on
        #//the best species
        NUM_STOLEN = neat.babies_stolen # //Number of babies to steal
        sorted_species = [] #//Species sorted by max fit org in Species

        #//We can try to keep the number of species constant at this number
        num_species_target = 4
        num_species = len(self.species)
        self.compat_mod = 0.3 #//Modify compat thresh to control speciation

        #//Stick the Species pointers into a new Species list for sorting
        sorted_species = [ curspecies for curspecies in self.species ]

        #//Sort the Species by max fitness (Use an extra list to do this)
        #//These need to use ORIGINAL fitness
        sorted_species.sort(key=order_species_key)
        if debug.is_set(DEBUG_CHECK):
            for i in range(1, len(sorted_species)):
                if sorted_species[i-1].organisms[0].orig_fitness < sorted_species[i].organisms[0].orig_fitness:
                    dprint(DEBUG_CHECK, "sorted_species out of order %7.5f < %7.5f." % (sorted_species[i-1].organisms[0].orig_fitness,
                                                                                        sorted_species[i].organisms[0].orig_fitness))
            dprint(DEBUG_CHECK, "Epoch starts with %d species." % (len(self.species), ))
                    
                                                                                        

        #//Flag the lowest performing species over age 20 every 30 generations 
        #//NOTE: THIS IS FOR COMPETITIVE COEVOLUTION STAGNATION DETECTION
        curspecies_i = len(sorted_species)-1
        while curspecies_i > 0 and sorted_species[curspecies_i].age < 20:
            curspecies_i -= 1
        if generation % 30 == 0 and sorted_species[curspecies_i].age >= 20:
            sorted_species[curspecies_i].obliterate = True
            dprint(DEBUG_INFO, "Obliterating species raned %d." % (curspecies_i, ))

        #//Use Species' ages to modify the objective fitness of organisms
        #// in other words, make it more fair for younger species
        #// so they have a chance to take hold
        #//Also penalize stagnant species
        #//Then adjust the fitness using the species size to "share" fitness
        #//within a species.
        #//Then, within each Species, mark for death 
        #//those below survival_thresh*average
        for curspecies in self.species:
            curspecies.adjust_fitness()

        #//Go through the organisms and add up their fitnesses to compute the
        #//overall average
        for curorg in self.organisms:
            total += curorg.fitness
        overall_average = total/total_organisms;

        #//Now compute expected number of offspring for each individual organism
        for curorg in self.organisms:
            curorg.expected_offspring = curorg.fitness / overall_average

        #//Now add those offspring up within each Species to get the number of
        #//offspring per Species
        skim = 0.0
        total_expected = 0
        for curspecies in self.species:
            skim = curspecies.count_offspring(skim)
            total_expected += curspecies.expected_offspring
            dprint(DEBUG_CHECK, "Species id[%d].expected_offspring = %d" % (curspecies.id, int(curspecies.expected_offspring)))

        dprint(DEBUG_CHECK, "Total Expected = %7.5f  Total Organisms = %d" % (float(total_expected), total_organisms))
        #//Need to make up for lost foating point precision in offspring assignment
        #//If we lost precision, give an extra baby to the best Species
        if total_expected < total_organisms:
            #//Find the Species expecting the most
            max_expected = 0
            final_expected = 0
            for curspecies in self.species:
                if curspecies.expected_offspring > max_expected:
                    max_expected = curspecies.expected_offspring
                    best_species = curspecies
                final_expected += curspecies.expected_offspring
            #
            #//Give the extra offspring to the best species
            best_species.expected_offspring += 1
            final_expected += 1

            #//If we still arent at total, there is a problem
            #//Note that this can happen if a stagnant Species
            #//dominates the population and then gets killed off by its age
            #//Then the whole population plummets in fitness
            #//If the average fitness is allowed to hit 0, then we no longer have 
            #//an average we can use to assign offspring.
            if final_expected < total_organisms:
                dprint(DEBUG_INFO, "Problem with final_expected = %d, keeping only the best_species" % (final_expected, ))
                for curspecies in self.species:
                    curspecies.expected_offspring = 0
                best_species.expected_offspring = total_organisms
            #
        #

        #//Sort the Species by max fitness (Use an extra list to do this)
        #//These need to use ORIGINAL fitness
        sorted_species.sort(key=order_species_key)
        best_species_num = sorted_species[0].id
        if debug.is_set(DEBUG_CHECK):
            for i in range(1, len(sorted_species)):
                if sorted_species[i-1].organisms[0].orig_fitness < sorted_species[i].organisms[0].orig_fitness:
                    dprint(DEBUG_CHECK, "sorted_species out of order %7.5f < %7.5f." % (sorted_species[i-1].organisms[0].orig_fitness,
                                                                                        sorted_species[i].organisms[0].orig_fitness))

        #//Check for Population-level stagnation
        curspecies = sorted_species[0]
        curspecies.organisms[0].pop_champ = True #//DEBUG marker of the best of pop
        if curspecies.organisms[0].orig_fitness > self.highest_fitness:
            self.highest_fitness = curspecies.organisms[0].orig_fitness
            self.highest_last_changed = 0
        else:
            self.highest_last_changed += 1

        #//Check for stagnation- if there is stagnation, perform delta-coding
        if self.highest_last_changed >= neat.dropoff_age + 5:
            dprint(DEBUG_INFO, "Stagnation in highest fitness.")
            self.highest_last_changed = 0
            half_pop = neat.pop_size/2
            curspecies_i = 0
            curspecies = sorted_species[curspecies_i]
            curspecies.organisms[0].super_champ_offspring = half_pop
            curspecies.expected_offspring = half_pop
            curspecies.age_of_last_improvement = curspecies.age
            curspecies_i += 1
            if curspecies_i < len(sorted_species):
                dprint(DEBUG_INFO, "Stagnation: reducing to top two species.")
                curspecies = sorted_species[curspecies_i]
                curspecies.organisms[0].super_champ_offspring = neat.pop_size - half_pop
                curspecies.expected_offspring = neat.pop_size - half_pop
                curspecies.age_of_last_improvement = curspecies.age
                curspecies_i += 1
                #//Get rid of all species under the first 2
                while curspecies_i < len(sorted_species):
                    curspecies = sorted_species[curspecies_i]
                    curspecies.expected_offspring = 0
                    curspecies_i += 1
                #
            else:
                dprint(DEBUG_INFO, "Stagnation: reducing to top one species.")
                curspecies_i = 0
                curspecies = sorted_species[curspecies_i]
                curspecies.organisms[0].super_champ_offspring += neat.pop_size - half_pop
                curspecies.expected_offspring += neat.pop_size - half_pop
            #
        # end stagnation check
    
        #//STOLEN BABIES:  The system can take expected offspring away from
        #//  worse species and give them to superior species depending on
        #//  the system parameter babies_stolen (when babies_stolen > 0)
        elif neat.babies_stolen > 0:
            #//Take away a constant number of expected offspring from the worst few species
            stolen_babies = 0
            curspecies_i = len(sorted_species) - 1
            
            while stolen_babies < NUM_STOLEN and curspecies_i > 0:
                curspecies = sorted_species[curspecies_i]
                if curspecies.age > 5 and curspecies.expected_offspring > 2:
                    #//This species has enough to finish off the stolen pool
                    if curspecies.expected_offspring - 1 > NUM_STOLEN - stolen_babies:
                        curspecies.expected_offspring -= NUM_STOLEN - stolen_babies
                        stolen_babies = NUM_STOLEN
                    #//Not enough here to complete the pool of stolen
                    else:
                        stolen_babies += curspecies.expected_offspring - 1
                        curspecies.expected_offspring = 1
                #
                curspecies_i -= 1
            #
            
            #//Mark the best champions of the top species to be the super champs
            #//who will take on the extra offspring for cloning or mutant cloning
            curspecies_i = 0
            curspecies = sorted_species[curspecies_i]

            #//Determine the exact number that will be given to the top three
            #//They get , in order, 1/5 1/5 and 1/10 of the stolen babies
            one_fifth_stolen = neat.babies_stolen/5
            one_tenth_stolen = neat.babies_stolen/10

            #//Don't give to dying species even if they are champs
            while curspecies_i < len(sorted_species) and curspecies.last_improved() > neat.dropoff_age:
                curspecies_i += 1
                if curspecies_i < len(sorted_species):
                    curspecies = sorted_species[curspecies_i]

            #//Concentrate A LOT on the number one species
            if (stolen_babies >= one_fifth_stolen) and (curspecies_i < len(sorted_species)):
                curspecies.organisms[0].super_champ_offspring = one_fifth_stolen
                curspecies.expected_offspring += one_fifth_stolen
                stolen_babies -= one_fifth_stolen
                curspecies_i += 1
                if curspecies_i < len(sorted_species):
                    curspecies = sorted_species[curspecies_i]

            #//Don't give to dying species even if they are champs
            while curspecies_i < len(sorted_species) and curspecies.last_improved() > neat.dropoff_age:
                curspecies_i += 1
                if curspecies_i < len(sorted_species):
                    curspecies = sorted_species[curspecies_i]

            if curspecies_i < len(sorted_species):
                if stolen_babies >= one_fifth_stolen:
                    curspecies.organisms[0].super_champ_offspring = one_fifth_stolen
                    curspecies.expected_offspring += one_fifth_stolen
                    stolen_babies -= one_fifth_stolen
                    curspecies_i += 1
                    if curspecies_i < len(sorted_species):
                        curspecies = sorted_species[curspecies_i]

            #//Don't give to dying species even if they are champs
            while curspecies_i < len(sorted_species) and curspecies.last_improved() > neat.dropoff_age:
                curspecies_i += 1
                if curspecies_i < len(sorted_species):
                    curspecies = sorted_species[curspecies_i]

            if curspecies_i < len(sorted_species):
                if stolen_babies >= one_tenth_stolen:
                    curspecies.organisms[0].super_champ_offspring = one_tenth_stolen
                    curspecies.expected_offspring += one_tenth_stolen
                    stolen_babies -= one_tenth_stolen
                    curspecies_i += 1
                    if curspecies_i < len(sorted_species):
                        curspecies = sorted_species[curspecies_i]

            #//Don't give to dying species even if they are champs
            while curspecies_i < len(sorted_species) and curspecies.last_improved() > neat.dropoff_age:
                curspecies_i += 1
                if curspecies_i < len(sorted_species):
                    curspecies = sorted_species[curspecies_i]


            while (stolen_babies > 0) and (curspecies_i < len(sorted_species)):
                #//Randomize a little which species get boosted by a super champ
                if neat.randfloat() > 0.1:
                    if stolen_babies > 3:
                        curspecies.organisms[0].super_champ_offspring = 3
                        curspecies.expected_offspring += 3
                        stolen_babies -= 3
                    else:
                        curspecies.organisms[0].super_champ_offspring = stolen_babies
                        curspecies.expected_offspring += stolen_babies
                        stolen_babies = 0

                curspecies_i += 1
                if curspecies_i < len(sorted_species):
                    curspecies = sorted_species[curspecies_i]

                #//Don't give to dying species even if they are champs
                while curspecies_i < len(sorted_species) and curspecies.last_improved() > neat.dropoff_age:
                    curspecies_i += 1
                    if curspecies_i < len(sorted_species):
                        curspecies = sorted_species[curspecies_i]

            #//If any stolen babies aren't taken, give them to species #1's champ
            if stolen_babies > 0:
                curspecies_i = 0
                curspecies = sorted_species[curspecies_i]
                curspecies.organisms[0].super_champ_offspring += stolen_babies
                curspecies.expected_offspring += stolen_babies
                stolen_babies = 0
            #
        #

        #//Kill off all Organisms marked for death.  The remainder
        #//will be allowed to reproduce.
        keep_organisms = []
        for curorg in self.organisms:
            if curorg.eliminate:
                #//Remove the organism from its Species
                curorg.species.remove_org(curorg)
            else:
                keep_organisms.append(curorg)
        self.organisms = keep_organisms

        #//Perform reproduction.  Reproduction is done on a per-Species
        #//basis.  (So this could be paralellized potentially.)
        curspecies_i = 0
        curspecies = self.species[curspecies_i]
        last_id = curspecies.id
        while curspecies_i < len(self.species):
            curspecies.reproduce(generation, self, sorted_species)
            #//Set the current species to the id of the last species checked
            #//(the iterator must be reset because there were possibly vector insertions during reproduce)
            curspecies2_i = 0
            while curspecies2_i < len(self.species):
                if self.species[curspecies2_i].id == last_id:
                    curspecies_i = curspecies2_i
                    break
                curspecies2_i += 1

            #//Move to the next on the list
            curspecies_i += 1
            if curspecies_i < len(self.species):
                curspecies = self.species[curspecies_i]
                last_id = curspecies.id
        #

        #//Destroy and remove the old generation from the organisms and species
        for curorg in self.organisms:
            #//Remove the organism from its Species
            curorg.species.remove_org(curorg)
        self.organisms = []

        #//Remove all empty Species and age ones that survive
        #//As this happens, create master organism list for the new generation
        orgcount = 0
        keep_species = []
        for curspecies in self.species:
            if len(curspecies.organisms) > 0:
                #//Age surviving Species and 
                #//Rebuild master Organism list: NUMBER THEM as they are added to the list
                if curspecies.novel:
                    curspecies.novel = False
                else:
                    #//Age any Species that is not newly created in this generation
                    curspecies.age += 1
                keep_species.append(curspecies)
                
                #//Go through the organisms of the curspecies and add them to 
                #//the master list
                for curorg in curspecies.organisms:
                    if debug.is_set(DEBUG_CHECK):
                        if curorg.eliminate:
                            dprint(DEBUG_ERROR, "elminated organism still here")
                    curorg.gnome.genome_id = orgcount
                    orgcount += 1
                    self.organisms.append(curorg)
        self.species = keep_species
        dprint(DEBUG_CHECK, "Epoch ends with %d species." % (len(self.species), ))

        #//Remove the innovations of the current generation
        self.innovations = []

        return True

    #// Places the organisms in species in order from best to worst fitness 
    # bool rank_within_species();
    def rank_within_species(self):
        for curspecies in self.species:
            curspecies.rank()
        return True

    
def main():
    print "Need Population exercise code here."
    return
    
if __name__ == "__main__":
    main()

        
