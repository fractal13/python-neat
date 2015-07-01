class Organism:

    def __init__(self):
        self.fitness = 0. # float;  //A measure of fitness for the Organism
        self.orig_fitness = 0. # float;  //A fitness measure that won't change during adjustments
        self.error = 0. # float;  //Used just for reporting purposes
        self.winner = False # bool;  //Win marker (if needed for a particular task)
        self.net = None # Network;  //The Organism's phenotype
        self.gnome = None # Genome; //The Organism's genotype 
        self.species = None # Species;  //The Organism's Species 
        self.expected_offspring = 0. # float; //Number of children this Organism may have
        self.generation = 0 # int;  //Tells which generation this Organism is from
        self.eliminate = False # bool;  //Marker for destruction of inferior Organisms
        self.champion = False # bool; //Marks the species champ
        self.super_champ_offspring = 0 #int;  //Number of reserved offspring for a population leader
        self.pop_champ = False # bool;  //Marks the best in population
        self.pop_champ_child = False # bool; //Marks the duplicate child of a champion (for tracking purposes)
        self.high_fit = 0. # double; //DEBUG variable- high fitness of champ
        self.time_alive = 0 # int; //When playing in real-time allows knowing the maturity of an individual
        
        #// Track its origin- for debugging or analysis- we can tell how the organism was born
        self.mut_struct_baby = False # bool;
        self.mate_baby = False # bool;
        
        #// MetaData for the object
        self.metadata = "" # string;
        self.modified = False # bool;

        return

    def SetFromGenome(self, fit, g, gen, md = ""):
        self.fitness = fit
        self.orig_fitness = self.fitness
        self.gnome = g
        self.net = self.gnome.genesis(self.gnome.genome_id)
        self.species = None
        self.expected_offspring = 0
        self.generation = gen
        self.eliminate = False
        self.error = 0.
        self.winner = False
        self.champion = False
        self.super_champ_offspring = 0
        self.metadata = md
        self.time_alive = 0
        
        self.pop_champ = False
        self.pop_champ_child = False
        self.high_fit = 0.
        self.mut_struct_baby = False
        self.mate_baby = False
        self.modified = True
        return

    def SetFromOther(self, other):
        self.fitness = other.fitness
        self.orig_fitness = other.orig_fitness
        self.gnome = Genome()
        self.gnome.SetFromOther(other.genome)
        self.net = Network()
        self.net.SetFromOther(other.net)
        self.species = other.species
        self.expected_offspring = other.expected_offspring
        self.generation = other.generation
        self.eliminate = other.eliminate
        self.error = other.error
        self.winner = other.winner
        self.champion = other.champion
        self.super_champ_offspring = other.super_champ_offspring
        self.metadata = other.metadata
        self.time_alive = other.time_alive
        
        self.pop_champ = other.pop_champ
        self.pop_champ_child = other.pop_champ_child
        self.high_fit = other.high_fit
        self.mut_struct_baby = other.mut_struct_baby
        self.mate_baby = other.mate_baby
        self.modified = False

        return

    #// Regenerate the network based on a change in the genotype 
    def update_phenotype(self):
        self.net = self.gnome.genesis(self.gnome.genome_id)
        self.modified = True
        return

    #// Print the Organism's genome to a file preceded by a comment detailing the organism's species, number, and fitness 
    def print_to_file(self, filename):
        ofile = open(filename, "w")
        retval = self.write_to_file(ofile)
        ofile.close()
        return retval

    def write_to_file(self, ofile):
        if self.modified:
            tempbuf2 = "/* Organism #%d Fitness: %f Time: %d */\n" % (self.gnome.genome_id, self.fitness, self.time_alive)
        else:
            tempbuf2 =  "/* %s */\n" % (self.metadata, )
        ofile.write(tempbuf2)
        self.gnome.print_to_file(ofile)
        return True

        

#// This is used for list sorting of Organisms by fitness..highest fitness first
def order_orgs(x, y):
    return x.fitness > y.fitness

def order_orgs_by_adjusted_fit(x, y):
    return x.fitness / len(x.species.organisms)  > y.fitness / len(y.species.organisms)

def main():
    print "Need Organism exercise code here."
    return
    
if __name__ == "__main__":
    main()

