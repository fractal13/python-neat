from utils import matching_import
from debug import dprint, dcallstack
import debug
matching_import("DEBUG_.*", debug, globals())
from genome import Genome
from organism import Organism, order_orgs_key
import neat
import math

# // ---------------------------------------------  
# // SPECIES CLASS:
# //   A Species is a group of similar Organisms      
# //   Reproduction takes place mostly within a
# //   single species, so that compatible organisms
# //   can mate.                                      
# // ---------------------------------------------  

class Species:

    def __init__(self):
        self.id = 0 # int ;
        self.age = 0 # int ; //The age of the Species 
        self.ave_fitness = 0. # double; //The average fitness of the Species
        self.max_fitness = 0. # double ; //Max fitness of the Species
        self.max_fitness_ever = 0. # double ; //The max it ever had
        self.expected_offspring = 0 # int ;
        self.novel = False # bool ;
        self.checked = False # bool ;
        self.obliterate = False # bool ;  //Allows killing off in competitive coevolution stagnation
        self.organisms = [] # std::vector<Organism*> ; //The organisms in the Species
        self.age_of_last_improvement = 0 # int ;  //If this is too long ago, the Species will goes extinct
        self.average_est = 0. # double ; //When playing real-time allows estimating average fitness
        return

    def SetFromId(self, i):
        self.id = i
        self.age = 1
        self.ave_fitness = 0.0
        self.expected_offspring = 0
        self.novel = False
        self.age_of_last_improvement = 0
        self.max_fitness = 0.
        self.max_fitness_ever = 0.
        self.obliterate = False
        self.average_est = 0.
        return

    #//Allows the creation of a Species that won't age (a novel one)
    #//This protects new Species from aging inside their first generation
    def SetFromIdAndNovel(self, i, n):
        self.id = i
        self.age = 1
        self.ave_fitness = 0.0
        self.expected_offspring = 0
        self.novel = n
        self.age_of_last_improvement = 0
        self.max_fitness = 0.
        self.max_fitness_ever = 0.
        self.obliterate = False
        self.average_est = 0.
        return

    def add_Organism(self, o):
        self.organisms.append(o)
        return True

    def first(self):
        return self.organisms[0]

    def print_to_file(self, ofile):
	tempbuf = "/* Species #%d : (Size %d) (AF %f) (Age %d)  */\n\n" % (self.id, len(self.organisms), self.average_est, self.age)
        ofile.write(tempbuf)
        for curorg in self.organisms:
            tempbuf2 = "/* Organism #%d Fitness: %f Time: %d */\n" % ( curorg.gnome.genome_id, curorg.fitness,
                                                                       curorg.time_alive )
            ofile.write(tempbuf2)
            if curorg.winner:
                tempbuf3 = "/* ##------$ WINNER %d SPECIES #%d $------## */\n" % ( curorg.gnome.genome_id, self.id )
                ofile.write(tempbuf3)
            curorg.gnome.print_to_file(ofile)
        ofile.write("\n\n")
        return True
        
    #//Change the fitness of all the organisms in the species to possibly depend slightly on the age of the species
    #//and then divide it by the size of the species so that the organisms in the species "share" the fitness
    def adjust_fitness(self):
        age_debt = (self.age - self.age_of_last_improvement + 1) - neat.dropoff_age
        if age_debt == 0:
            age_debt = 1
        
        for curorg in self.organisms:
            curorg.orig_fitness = curorg.fitness
            if age_debt >= 1 or self.obliterate:
                curorg.fitness = curorg.fitness * 0.01
            if self.age <= 10:
                curorg.fitness = curorg.fitness * neat.age_significance
            if curorg.fitness < 0.0:
                curorg.fitness = 0.0001
            curorg.fitness = curorg.fitness / len(self.organisms)

        self.organisms.sort(key=order_orgs_key)
        if debug.is_set(DEBUG_CHECK):
            for i in range(1, len(self.organisms)):
                if self.organisms[i-1].fitness < self.organisms[i].fitness:
                    dprint(DEBUG_ERROR, "sorted organisms out of order %7.5f < %7.5f." % (self.organisms[i-1].fitness,
                                                                                          self.organisms[i].fitness))

        if self.organisms[0].orig_fitness > self.max_fitness_ever:
            self.max_fitness_ever = self.organisms[0].orig_fitness
            self.age_of_last_improvement = self.age

        num_parents = int(math.floor(neat.survival_thresh * float(len(self.organisms))+1.0))
        self.organisms[0].champion = True
        if len(self.organisms) > num_parents:
            for i in range(num_parents, len(self.organisms)):
                self.organisms[i].eliminate = True
        return

    def compute_average_fitness(self):
        total = 0.0

        for curorg in self.organisms:
            total += curorg.fitness

        self.ave_fitness = total / len(self.organisms)
        return self.ave_fitness

    def compute_max_fitness(self):
        mx = 0.0
        for curorg in self.organisms:
            if curorg.fitness > mx:
                mx = curorg.fitness
        self.max_fitness = mx
        return self.max_fitness

    #//Counts the number of offspring expected from all its members skim is for keeping track of remaining 
    #// fractional parts of offspring and distributing them among species
    def count_offspring(self, skim):
        self.expected_offspring = 0
        for curorg in self.organisms:
            e_o_intpart = int(math.floor( curorg.expected_offspring ))
            e_o_fracpart = curorg.expected_offspring - e_o_intpart
            self.expected_offspring += e_o_intpart
            skim += e_o_fracpart
            if skim > 1.0:
                skim_intpart = int(math.floor(skim))
                self.expected_offspring += int( skim_intpart )
                skim -= skim_intpart
        return skim

    #//Compute generations since last improvement
    def last_improved(self):
        return self.age-self.age_of_last_improvement

    #//Remove an organism from Species
    def remove_org(self, org):
        found = False
        for org_i in range(len(self.organisms)):
            if self.organisms[org_i] == org:
                found = True
                break
        if found:
            self.organisms.pop(org_i)
            return True
        else:
            print "ERROR in remove_org, no match"
            return False

    def size(self):
        return len(self.organisms)

    def get_champ(self):
        champ_fitness = -1.0
        for curorg in self.organisms:
            if curorg.fitness > champ_fitness:
                thechamp = curog
                champ_fitness = curorg.fitness
        return thechamp

    def verify_baby(self, baby, mom, dad):
        if debug.is_set(DEBUG_INTEGRITY):
            if not baby.verify():
                dcallstack(DEBUG_INTEGRITY)
                dprint(DEBUG_INTEGRITY, "baby.verify() failed.")
                dprint(DEBUG_INTEGRITY, "baby:\n", baby.deep_string())
                if mom:
                    dprint(DEBUG_INTEGRITY, "mom:\n", mom.deep_string())
                if dad:
                    dprint(DEBUG_INTEGRITY, "dad:\n", dad.deep_string())
        return

    def verify_genome(self, g):
        if debug.is_set(DEBUG_INTEGRITY):
            if not g.verify():
                dcallstack(DEBUG_INTEGRITY)
                dprint(DEBUG_INTEGRITY, "g.verify() failed.")
                dprint(DEBUG_INTEGRITY, "g:\n", g.deep_string())
        return

    #//Perform mating and mutation to form next generation
    def reproduce(self, generation, pop, sorted_species):
        champ_done = False
        mut_power = neat.weight_mut_power
        total_fitness = 0.0
        
        if self.expected_offspring > 0 and len(self.organisms) == 0:
            return False

        poolsize = len(self.organisms) - 1
        thechamp_i = 0
        for count in range(0, self.expected_offspring):
            mut_struct_baby = False
            mate_baby = False
            outside = False
            mom = dad = None

            if self.organisms[thechamp_i].super_champ_offspring > 0:
                dprint(DEBUG_CHECK, "super_champ_offspring()")
                mom_i = thechamp_i
                mom = self.organisms[mom_i]
                new_genome = mom.gnome.duplicate(count)
                if self.organisms[thechamp_i].super_champ_offspring == 1:
                    pass
                if self.organisms[thechamp_i].super_champ_offspring > 1:
                    if neat.randfloat() < 0.8 or neat.mutate_add_link_prob == 0.0:
                        new_genome.mutate_link_weights(mut_power, 1.0, Genome.GAUSSIAN)
                    else:
                        net_analogue = new_genome.genesis(generation)
                        ok, pop.cur_innov_num = \
                            new_genome.mutate_add_link(pop.innovations, pop.cur_innov_num, neat.newlink_tries)
                        net_analogue = None
                        mut_struct_baby = True
                #
                baby = Organism()
                baby.SetFromGenome(0.0, new_genome, generation)
                if self.organisms[thechamp_i].super_champ_offspring == 1:
                    if self.organisms[thechamp_i].pop_champ:
                        baby.pop_champ_child = True
                        baby.high_fit = mom.orig_fitness
                #
                self.organisms[thechamp_i].super_champ_offspring -= 1
                self.verify_baby(baby, mom, dad)

                # super_champ_offspring > 0
            elif (not champ_done) and (self.expected_offspring > 5):
                dprint(DEBUG_CHECK, "champ()")
                mom_i = thechamp_i
                mom = self.organisms[mom_i]
                new_genome = mom.gnome.duplicate(count)
                baby = Organism()
                baby.SetFromGenome(0.0, new_genome, generation)
                champ_done = True
                self.verify_baby(baby, mom, dad)

                # (not champ_done) and (self.expected_offspring > 5)
            elif (neat.randfloat() < neat.mutate_only_prob) or (poolsize == 0):
                dprint(DEBUG_CHECK, "mutate_only()")
                mom_i = neat.randint(0, poolsize)
                mom = self.organisms[mom_i]
                new_genome = mom.gnome.duplicate(count)
                self.verify_genome(new_genome)

                if neat.randfloat() < neat.mutate_add_node_prob:
                    dprint(DEBUG_INTEGRITY, "a: pop.cur_node_id:", pop.cur_node_id)
                    ok, pop.cur_node_id, pop.cur_innov_num = \
                        new_genome.mutate_add_node(pop.innovations, pop.cur_node_id, pop.cur_innov_num)
                    dprint(DEBUG_INTEGRITY, "b: pop.cur_node_id:", pop.cur_node_id)
                    mut_struct_baby = True
                    self.verify_genome(new_genome)

                elif neat.randfloat() < neat.mutate_add_link_prob:
                    net_analogue = new_genome.genesis(generation)
                    ok, pop.cur_innov_num = \
                        new_genome.mutate_add_link(pop.innovations, pop.cur_innov_num, neat.newlink_tries)
                    net_analogue = None
                    mut_struct_baby = True
                    self.verify_genome(new_genome)

                else:
                    if neat.randfloat() < neat.mutate_random_trait_prob:
                        new_genome.mutate_random_trait()
                        self.verify_genome(new_genome)
                    if neat.randfloat() < neat.mutate_link_trait_prob:
                        new_genome.mutate_link_trait(1)
                        self.verify_genome(new_genome)
                    if neat.randfloat() < neat.mutate_node_trait_prob:
                        new_genome.mutate_node_trait(1)
                        self.verify_genome(new_genome)
                    if neat.randfloat() < neat.mutate_link_weights_prob:
                        new_genome.mutate_link_weights(mut_power, 1.0, Genome.GAUSSIAN)
                        self.verify_genome(new_genome)
                    if neat.randfloat() < neat.mutate_toggle_enable_prob:
                        new_genome.mutate_toggle_enable(1)
                        self.verify_genome(new_genome)
                    if neat.randfloat() < neat.mutate_gene_reenable_prob:
                        new_genome.mutate_gene_reenable()
                        self.verify_genome(new_genome)

                baby = Organism()
                baby.SetFromGenome(0.0, new_genome, generation)
                self.verify_baby(baby, mom, dad)

                # (neat.randfloat() < neat.mutate_only_prob) or (poolsize == 0)
            else:
                mom_i = neat.randint(0, poolsize)
                mom = self.organisms[mom_i]

                if neat.randfloat() > neat.interspecies_mate_rate:
                    # within species
                    dad_i = neat.randint(0, poolsize)
                    dad = self.organisms[dad_i]

                else:
                    # outside species
                    randspecies = self

                    giveup = 0
                    while (randspecies == self) and (giveup < 5):
                        randmult = neat.gaussrand() / 4.
                        if randmult > 1.0:
                            randmult = 1.0
                        randspeciesnum = int(math.floor( (randmult * (len(sorted_species) - 1.0)) + 0.5 ))
                        randspecies = sorted_species[randspeciesnum]
                        giveup += 1

                    dad = randspecies.organisms[0]
                    outside = True

                if neat.randfloat() < neat.mate_multipoint_prob:
                    dprint(DEBUG_CHECK, "mate_multipoint()")
                    new_genome = mom.gnome.mate_multipoint(dad.gnome, count, mom.orig_fitness, dad.orig_fitness, outside)
                elif neat.randfloat() < neat.mate_multipoint_avg_prob / (neat.mate_multipoint_avg_prob+neat.mate_singlepoint_prob):
                    dprint(DEBUG_CHECK, "mate_multipoint_avg()")
                    new_genome = mom.gnome.mate_multipoint_avg(dad.gnome, count, mom.orig_fitness, dad.orig_fitness, outside)
                else:
                    dprint(DEBUG_CHECK, "mate_singlepoint()")
                    new_genome = mom.gnome.mate_singlepoint(dad.gnome, count)

                mate_baby = True

                if ((neat.randfloat() > neat.mate_only_prob) or
                    (dad.gnome.genome_id == mom.gnome.genome_id) or
                    (dad.gnome.compatibility(mom.gnome) == 0.0)):
                    dprint(DEBUG_CHECK, "mate_and_mutate()")
                    if neat.randfloat() < neat.mutate_add_node_prob:
                        dprint(DEBUG_INTEGRITY, "a: pop.cur_node_id:", pop.cur_node_id)
                        ok, pop.cur_node_id, pop.cur_innov_num = \
                            new_genome.mutate_add_node(pop.innovations, pop.cur_node_id, pop.cur_innov_num)
                        dprint(DEBUG_INTEGRITY, "b: pop.cur_node_id:", pop.cur_node_id)
                        mut_struct_baby = True
                    elif neat.randfloat() < neat.mutate_add_link_prob:
                        net_analogue = new_genome.genesis(generation)
                        ok, pop.cur_innov_num = \
                            new_genome.mutate_add_link(pop.innovations, pop.cur_innov_num, neat.newlink_tries)
                        net_analogue = None
                        mut_struct_baby = True
                    else:
                        if neat.randfloat() < neat.mutate_random_trait_prob:
                            new_genome.mutate_random_trait()
                        if neat.randfloat() < neat.mutate_link_trait_prob:
                            new_genome.mutate_link_trait(1)
                        if neat.randfloat() < neat.mutate_node_trait_prob:
                            new_genome.mutate_node_trait(1)
                        if neat.randfloat() < neat.mutate_link_weights_prob:
                            new_genome.mutate_link_weights(mut_power, 1.0, Genome.GAUSSIAN)
                        if neat.randfloat() < neat.mutate_toggle_enable_prob:
                            new_genome.mutate_toggle_enable(1)
                        if neat.randfloat() < neat.mutate_gene_reenable_prob:
                            new_genome.mutate_gene_reenable()

                    baby = Organism()
                    baby.SetFromGenome(0.0, new_genome, generation)
                    self.verify_baby(baby, mom, dad)

                else:
                    dprint(DEBUG_CHECK, "mate_only()")
                    baby = Organism()
                    baby.SetFromGenome(0.0, new_genome, generation)
                    self.verify_baby(baby, mom, dad)

                # else

            baby.mut_struct_baby = mut_struct_baby
            baby.mate_baby = mate_baby
            
            curspecies_i = 0
            found = False
            while (curspecies_i < len(pop.species)) and (not found):
                comporg = pop.species[curspecies_i].first()
                if comporg == None:
                    curspecies_i += 1
                elif baby.gnome.compatibility(comporg.gnome) < neat.compat_threshold:
                    pop.species[curspecies_i].add_Organism(baby)
                    baby.species = pop.species[curspecies_i]
                    found = True
                else:
                    curspecies_i += 1
            #
            if not found:
                pop.last_species += 1
                newspecies = Species()
                newspecies.SetFromIdAndNovel(pop.last_species, True)
                pop.species.append(newspecies)
                newspecies.add_Organism(baby)
                baby.species = newspecies
                    

            # for count in self.expected_offspring

        return True

    #// *** Real-time methods *** 

    #//Place organisms in this species in order by their fitness
    def rank(self):
        self.organisms.sort(key=order_org_key)
        return True


#// This is used for list sorting of Species by fitness of best organism highest fitness first 
def order_species(x, y):
    return x.organisms[0].orig_fitness > y.organisms[0].orig_fitness
def order_species_key(x):
    # change sign to get highest first
    return -x.organisms[0].orig_fitness

def order_new_species(x, y):
    return x.compute_max_fitness() > y.compute_max_fitness()

    
def main():
    print "Need Species exercise code here."
    return
    
if __name__ == "__main__":
    main()

        
