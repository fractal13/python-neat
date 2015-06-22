import random

num_trait_params = 8
trait_param_mut_prob = 0.01
trait_mutation_power = 0.01


def randposneg():
    return random.choice( [ 1, -1 ] )

def randint(x, y):
    return random.randrange(x, y+1)

def randfloat():
    return random.random()
