import random, math

datadir = "data"
configdir = datadir + "/config"
genedir = datadir + "/genes"
generationdir = datadir + "/gen"
testdir = datadir + "/testout"

num_trait_params = 8

trait_param_mut_prob = 0.0 # double; 
trait_mutation_power = 0.0 # double;  // Power of mutation on a signle trait param 
linktrait_mut_sig = 0.0 # double;  // Amount that mutation_num changes for a trait change inside a link
nodetrait_mut_sig = 0.0 # double;  // Amount a mutation_num changes on a link connecting a node that changed its trait 
weight_mut_power = 0.0 # double;  // The power of a linkweight mutation 
recur_prob = 0.0 # double;  // Prob. that a link mutation which doesn't have to be recurrent will be made recurrent 

# // These 3 global coefficients are used to determine the formula for
# // computating the compatibility between 2 genomes.  The formula is:
# // disjoint_coeff*pdg+excess_coeff*peg+mutdiff_coeff*mdmg.
# // See the compatibility method in the Genome class for more info
# // They can be thought of as the importance of disjoint Genes,
# // excess Genes, and parametric difference between Genes of the
# // same function, respectively. 
disjoint_coeff = 0.0 # double; 
excess_coeff = 0.0 # double; 
mutdiff_coeff = 0.0 # double;

#// This global tells compatibility threshold under which two Genomes are considered the same species 
compat_threshold = 0.0 # double;

age_significance = 0.0 # double;  // How much does age matter? 
survival_thresh = 0.0 # double;  // Percent of ave fitness for survival 
mutate_only_prob = 0.0 # double;  // Prob. of a non-mating reproduction 
mutate_random_trait_prob = 0.0 # double; 
mutate_link_trait_prob = 0.0 # double; 
mutate_node_trait_prob = 0.0 # double; 
mutate_link_weights_prob = 0.0 # double; 
mutate_toggle_enable_prob = 0.0 # double; 
mutate_gene_reenable_prob = 0.0 # double; 
mutate_add_node_prob = 0.0 # double; 
mutate_add_link_prob = 0.0 # double; 
interspecies_mate_rate = 0.0 # double;  // Prob. of a mate being outside species 
mate_multipoint_prob = 0.0 # double;      
mate_multipoint_avg_prob = 0.0 # double; 
mate_singlepoint_prob = 0.0 # double; 
mate_only_prob = 0.0 # double;  // Prob. of mating without mutation 
recur_only_prob = 0.0 # double;   // Probability of forcing selection of ONLY links that are naturally recurrent 

pop_size = 0 # int ;  // Size of population 
dropoff_age = 0 # int ;  // Age where Species starts to be penalized 
newlink_tries = 0 # int ;  // Number of tries mutate_add_link will attempt to find an open link 
print_every = 0 # int ; // Tells to print population to file every n generations 
babies_stolen = 0 # int ; // The number of babies to siphen off to the champions 
num_runs = 0 # int ; //number of times to run experiment


#// Inline Random Functions 
def randposneg():
    return random.choice( [ 1, -1 ] )

def randint(x, y):
    return random.randrange(x, y+1)

def randfloat():
    return random.random()

#// Returns a normally distributed deviate with 0 mean and unit variance
#// Algorithm is from Numerical Recipes in C, Second Edition
_gaussrand_iset = 0
_gaussrand_gset = 0.0
def gaussrand():
    """Should probably use random.gauss() need to figure out mu and sigma"""
    global _gaussrand_iset, _gaussrand_gset
    if _gaussrand_iset == 0:
        rsq = 2.0
        while rsq >= 1.0 or rsq == 0.0:
            v1 = 2.0 * (randfloat())-1.0
            v2 = 2.0 * (randfloat())-1.0
            rsq = v1*v1 + v2*v2
            
        fac = math.sqrt(-2.0*math.log(rsq)/rsq)
        _gaussrand_gset = v1 * fac
        _gaussrand_iset = 1
        return v2 * fac
    else:
        _gaussrand_iset = 0
        return _gaussrand_gset


# // SIGMOID FUNCTION ********************************
# // This is a signmoidal activation function, which is an S-shaped squashing function
# // It smoothly limits the amplitude of the output of a neuron to between 0 and 1
# // It is a helper to the neural-activation function get_active_out
# // It is made inline so it can execute quickly since it is at every non-sensor 
# // node in a network.
# // NOTE:  In order to make node insertion in the middle of a link possible,
# // the signmoid can be shifted to the right and more steeply sloped:
# // slope=4.924273
# // constant= 2.4621365
# // These parameters optimize mean squared error between the old output,
# // and an output of a node inserted in the middle of a link between
# // the old output and some other node. 
# // When not right-shifted, the steepened slope is closest to a linear
# // ascent as possible between -0.5 and 0.5
def fsigmoid(activesum, slope, constant):
    return (1/(1+(math.exp(-(slope*activesum))))); #Compressed
    
# // Hebbian Adaptation Function
# // Based on equations in Floreano & Urzelai 2000
# // Takes the current weight, the maximum weight in the containing network,
# // the activation coming in and out of the synapse,
# // and three learning rates for hebbian, presynaptic, and postsynaptic
# // modification
# // Returns the new modified weight
# // NOTE: For an inhibatory connection, it makes sense to
# //      emphasize decorrelation on hebbian learning!	
def hebbian(weight, maxweight, active_in, active_out, hebb_rate, pre_rate, post_rate):
    neg = False
    if maxweight < 5.0:
        maxweight = 5.0
    if weight > maxweight:
        weight = maxweight
    if weight < -maxweight:
        weight = -maxweight
    if weight < 0:
        neg = True
        weight = -weight
    
    topweight = weight + 2.0
    if topweight > maxweight:
        topweight = maxweight

    if not neg:
        delta = (hebb_rate * (maxweight-weight) * active_in * active_out +
                 pre_rate * (topweight) * active_in * (active_out-1.0))
        return weight + delta
        
    else:
        # In the inhibatory case, we strengthen the synapse when output is low and
        # input is high
        delta = (pre_rate * (maxweight-weight) * active_in * (1.0-active_out) + # "unhebb"
                 -hebb_rate * (topweight+2.0) * active_in * active_out + # anti-hebbian
                 0)
        return -(weight + delta)


# bool load_neat_params(const char *filename, bool output = false);
def load_neat_params(filename, output):
    g = globals()

    float_params = [ "trait_param_mut_prob",
                     "trait_mutation_power",
                     "linktrait_mut_sig",
                     "nodetrait_mut_sig",
                     "weight_mut_power",
                     "recur_prob",
                     "disjoint_coeff",
                     "excess_coeff",
                     "mutdiff_coeff",
                     "compat_threshold",
                     "age_significance",
                     "survival_thresh",
                     "mutate_only_prob",
                     "mutate_random_trait_prob",
                     "mutate_link_trait_prob",
                     "mutate_node_trait_prob",
                     "mutate_link_weights_prob",
                     "mutate_toggle_enable_prob",
                     "mutate_gene_reenable_prob",
                     "mutate_add_node_prob",
                     "mutate_add_link_prob",
                     "interspecies_mate_rate",
                     "mate_multipoint_prob",
                     "mate_multipoint_avg_prob",
                     "mate_singlepoint_prob",
                     "mate_only_prob",
                     "recur_only_prob",
                     ]
    int_params = [ "pop_size",
                   "dropoff_age",
                   "newlink_tries",
                   "print_every",
                   "babies_stolen",
                   "num_runs",
                   ]
    
    paramFile = open(filename, "r")
    if not paramFile:
        dprint(DEBUG_ERROR, "Unable to open file %s." % (filename, ))
        return False

        
    #// **********LOAD IN PARAMETERS*************** //
    if output:
        print "NEAT READING IN %s" % (filename,)
    
    for line in paramFile:
        line = line.strip()
        if line == "":
            continue
        if line[0] == "#":
            continue
        words = line.split()
        if len(words) < 2:
            print "Unknown parameter line: %" % (line)
            continue
        param_name = words[0]
        if param_name in float_params:
            value = float(words[1])
        elif param_name in int_params:
            value = int(words[1])
        else:
            value = words[1]
            print "Warning: unclassified parameter: %s = %s" % (param_name, value)

        if param_name not in g:
            print "ERROR: Configuration file parameter %s is not known." % (param_name,)
        else:
            g[param_name] = value

    if output:
        for p in float_params:
            print "%s=%f" % (p, g[p])
        for p in int_params:
            print "%s=%d" % (p, g[p])

    paramFile.close()
    return True


def str_to_bool(string):
    if string.lower() == "true":
        return True
    if string.lower() == "false":
        return False
    if string == "0":
        return False
    if string == "1":
        return True
    try:
        if int(string) == 0:
            return False
        else:
            return True
    except:
        return False
    
def main():
    filenames = [ "p2mpar3bare.ne", "p2nv.ne", "p2test.ne", "params256.ne", "pole2_markov.ne", "test.ne" ]
    for filename in filenames:
        if not load_neat_params(configdir + "/" + filename, True):
            print "LOAD FAILED:"

    print "Still need tests for random functions, fsigmod, and hebbian"
    return
    
if __name__ == "__main__":
    main()

    
