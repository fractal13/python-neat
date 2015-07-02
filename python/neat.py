import random, math

num_trait_params = 8

trait_param_mut_prob = 0.0 # double; 
trait_mutation_power = 0.0 # double;  // Power of mutation on a signle trait param 
linktrait_mut_sig = 0.0 # double;  // Amount that mutation_num changes for a trait change inside a link
nodetrait_mut_sig = 0.0 # double;  // Amount a mutation_num changes on a link connecting a node that changed its trait 
weight_mut_power = 0.0 # double;  // The power of a linkweight mutation 
recur_prob = 0.0 # double;  // Prob. that a link mutation which doesn't have to be recurrent will be made recurrent 
disjoint_coeff = 0.0 # double; 
excess_coeff = 0.0 # double; 
mutdiff_coeff = 0.0 # double; 
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
num_runs = 0 # int ;


def randposneg():
    return random.choice( [ 1, -1 ] )

def randint(x, y):
    return random.randrange(x, y+1)

def randfloat():
    return random.random()

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

def fsigmod(activesum, slope, constant):
    return (1/(1+(math.exp(-(slope*activesum))))); #Compressed
    
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
