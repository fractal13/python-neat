import random, math

num_trait_params = 8
trait_param_mut_prob = 0.01
trait_mutation_power = 0.01
recur_only_prob = 0.0
disjoint_coeff = 0.0
excess_coeff = 0.0
mutdiff_coeff = 0.0

def randposneg():
    return random.choice( [ 1, -1 ] )

def randint(x, y):
    return random.randrange(x, y+1)

def randfloat():
    return random.random()

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
