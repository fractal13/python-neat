
class Genome:
    """
    //----------------------------------------------------------------------- 
    //A Genome is the primary source of genotype information used to create   
    //a phenotype.  It contains 3 major constituents:                         
    //  1) A list of Traits                                                 
    //  2) A list of NNodes pointing to a Trait from (1)                      
    //  3) A list of Genes with Links that point to Traits from (1)           
    //(1) Reserved parameter space for future use
    //(2) NNode specifications                                                
    //(3) Is the primary source of innovation in the evolutionary Genome.     
    //    Each Gene in (3) has a marker telling when it arose historically.   
    //    Thus, these Genes can be used to speciate the population, and the   
    //    list of Genes provide an evolutionary history of innovation and     
    //    link-building.
    """

    GAUSSIAN = 0
    COLDGAUSSIAN = 1

    def __init__(self):
        self.genome_id = ? # int,
        self.traits = [] # list of Trait, parameter conglomerations
        self.nodes = [] # list of NNode, NNodes for the network
        self.genes = [] # list of Gene, innovation tracking
        self.phenotype = None # Network, Allows Genome to be matched with its Network
        return

    ##//Constructor which takes full genome specs and puts them into the new one
    def SetFromSpecs(self, gid, traits, nodes, genes):
        ???
        return

    ##//Constructor which takes in links (not genes) and creates a Genome
    def SetFromLinks(self, gid, traits, nodes, links):
        ???
        return

    ##// Copy constructor
    def SetFromOther(self, other):
        ???
        return

    ##//Special constructor which spawns off an input file
    ##//This constructor assumes that some routine has already read in GENOMESTART
    def SetFromFile(self, gid, fin):
        ???
        return

    ##// This special constructor creates a Genome
    ##// with i inputs, o outputs, n out of nmax hidden units, and random
    ##// connectivity.  If r is true then recurrent connections will
    ##// be included. 
    ##// The last input is a bias
    ##// Linkprob is the probability of a link  
    def SetFromCounts(self, gid, i, o, n, nmax, r, linkprob):
        ???
        return

    ##//Special constructor that creates a Genome of 3 possible types:
    ##//0 - Fully linked, no hidden nodes
    ##//1 - Fully linked, one hidden node splitting each link
    ##//2 - Fully connected with a hidden layer, recurrent 
    ##//num_hidden is only used in type 2
    def SetFromCounts2(self, num_in, num_out, num_hidden, typ):
        ???
        return

    ##// Loads a new Genome from a file (doesn't require knowledge of Genome's id)
    @classmethod
    def new_Genome_load(cls, filename):
        ???
        return

    ##//Generate a network phenotype from this Genome with specified id
    def genesis(self, nid):
        ???
        return

    ##// Dump this genome to specified file
    def print_to_file(self, fout):
        ???
        return

    ##// Wrapper for print_to_file above
    def print_to_filename(self, filename):
        ???
        return

    ##// Duplicate this Genome to create a new one with the specified id 
    def duplicate(self, new_id):
        ???
        return

    ##// For debugging: A number of tests can be run on a genome to check its
    ##// integrity
    ##// Note: Some of these tests do not indicate a bug, but rather are meant
    ##// to be used to detect specific system states
    def verify(self):
        ???
        return


    ##// ******* MUTATORS *******

    ##// Perturb params in one trait
    def mutate_random_trait(self):
        ???
        return

    ##// Change random link's trait. Repeat times times
    def mutate_link_trait(self, times):
        ???
        return

    ##// Change random node's trait times times 
    def mutate_node_trait(self, times):
        ???
        return

    ##// Add Gaussian noise to linkweights either GAUSSIAN or COLDGAUSSIAN (from zero)
    def mutate_link_weights(self, power, rate, mut_type):
        ???
        return

    ##// toggle genes on or off 
    def mutate_toggle_enable(self, times):
        ???
        return

    ##// Find first disabled gene and enable it 
    def mutate_gene_reenable(self):
        ???
        return

    ##// These last kinds of mutations return false if they fail
    ##//   They can fail under certain conditions,  being unable
    ##//   to find a suitable place to make the mutation.
    ##//   Generally, if they fail, they can be called again if desired. 

    ##// Mutate genome by adding a node respresentation 
    def mutate_add_node(self, innovs, curnode_id, curinnov):
        ???
        return

    ##// Mutate the genome by adding a new link between 2 random NNodes 
    def mutate_add_link(self, innovs, curinnov, tries):
        ???
        return

    def mutate_add_sensor(self, innovs, curinnov):
        ???
        return
        
    ##// ****** MATING METHODS ***** 

    ##// This method mates this Genome with another Genome g.  
    ##//   For every point in each Genome, where each Genome shares
    ##//   the innovation number, the Gene is chosen randomly from 
    ##//   either parent.  If one parent has an innovation absent in 
    ##//   the other, the baby will inherit the innovation 
    ##//   Interspecies mating leads to all genes being inherited.
    ##//   Otherwise, excess genes come from most fit parent.
    def mate_multipoint(self, g, genomeid, fitness1, fitness2, interspec_flag):
        ???
        return

    ##//This method mates like multipoint but instead of selecting one
    ##//   or the other when the innovation numbers match, it averages their
    ##//   weights 
    def mate_multipoint_avg(self, g, genomeid, fitness1, fitness2, interspec_flag):
        ???
        return

    ##// This method is similar to a standard single point CROSSOVER
    ##//   operator.  Traits are averaged as in the previous 2 mating
    ##//   methods.  A point is chosen in the smaller Genome for crossing
    ##//   with the bigger one.  
    def mate_singlepoint(self, g, genomeid):
        ???
        return

    ##// ******** COMPATIBILITY CHECKING METHODS ********

    ##// This function gives a measure of compatibility between
    ##//   two Genomes by computing a linear combination of 3
    ##//   characterizing variables of their compatibilty.
    ##//   The 3 variables represent PERCENT DISJOINT GENES, 
    ##//   PERCENT EXCESS GENES, MUTATIONAL DIFFERENCE WITHIN
    ##//   MATCHING GENES.  So the formula for compatibility 
    ##//   is:  disjoint_coeff*pdg+excess_coeff*peg+mutdiff_coeff*mdmg.
    ##//   The 3 coefficients are global system parameters 
    def compatibility(self, g):
        ???
        return
    
    def trait_compare(self, t1, t2):
        ???
        return
                
    ##// Return number of non-disabled genes 
    def extrons(self):
        ???
        return
    
    ##// Randomize the trait pointers of all the node and connection genes 
    def randomize_traits(self):
        ???
        return
        
    ##//Inserts a NNode into a given ordered list of NNodes in order
    def node_insert(self, nlist, n):
        ???
        return

    ##//Adds a new gene that has been created through a mutation in the
    ##//*correct order* into the list of genes in the genome
    def add_gene(self, glist, g):
        ???
        return

    def get_last_node_id(self):
        ???
        return

    def get_last_gene_innovnum(self):
        ???
        return

    def print_genome(self):
        ???
        return

    
##//Calls special constructor that creates a Genome of 3 possible types:
##//0 - Fully linked, no hidden nodes
##//1 - Fully linked, one hidden node splitting each link
##//2 - Fully connected with a hidden layer 
##//num_hidden is only used in type 2
##//Saves to file "auto_genome"
def new_Genome_auto(num_in, num_out, num_hidden, typ, filename):
    ???
    return

def print_Genome_tofile(g, filename):
    ???
    return

def main():
    print "Need Genome exercise code here."
    return
    
if __name__ == "__main__":
    main()

