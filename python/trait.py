from utils import matching_import
from debug import dprint
import debug
matching_import("DEBUG_.*", debug, globals())
import neat

class Trait:
    """
    // ------------------------------------------------------------------ 
    // TRAIT: A Trait is a group of parameters that can be expressed     
    //        as a group more than one time.  Traits save a genetic      
    //        algorithm from having to search vast parameter landscapes  
    //        on every node.  Instead, each node can simply point to a trait 
    //        and those traits can evolve on their own

    
    // ************ LEARNING PARAMETERS *********** 
    // The following parameters are for use in    
    //   neurons that learn through habituation,
    //   sensitization, or Hebbian-type processes
    // self.params[]
    """

    # Constructor
    def __init__(self):
        self.trait_id = 0
        self.params = [ 0.0 for x in range(neat.num_trait_params) ]
        return

    # Set values from distinct function parameters
    def SetFromNine(self, id, p1, p2, p3, p4, p5, p6, p7, p8, p9):
        self.trait_id = id
        self.params[0] = p1
        self.params[1] = p2
        self.params[2] = p3
        self.params[3] = p4
        self.params[4] = p5
        self.params[5] = p6
        self.params[6] = p7
        self.params[7] = 0
        return

    # Set values as explicit copy of another object
    def SetFromOther(self, other):
        self.trait_id = other.trait_id
        for i in range(neat.num_trait_params):
            self.params[i] = other.params[i]
        return

    # Set values by parsing a string
    def SetFromString(self, argline):
        dprint(DEBUG_FILEINPUT, "Trait.SetFromString:argline:", argline)
        values = argline.split()
        if len(values) < neat.num_trait_params+1:
            dprint(DEBUG_ERROR, "Trait.SetFromString:argline:", argline, "too few items:", len(values), "should have", neat.num_trait_params+1)
        self.trait_id = int(values[0])
        for i in range(neat.num_trait_params):
            self.params[i] = float(values[i+1])
        return

    # Set values as an average of two other objects
    def SetFromAverage(self, other1, other2):
        self.trait_id = other1.trait_id
        for i in range(neat.num_trait_params):
            self.params[i] = (other1.params[i] + other2.params[i])/2.0
        return

    # Save to a file
    def print_to_file(self, fout):
        fout.write("trait ")
        fout.write(str(self.trait_id) + " ")
        for i in range(neat.num_trait_params):
            fout.write(str(self.params[i]) + " ")
        fout.write("\n")
        return

    # Perturb the trait parameters slightly
    def mutate(self):
        for i in range(neat.num_trait_params):
            if neat.randfloat() > neat.trait_param_mut_prob:
                self.params[i] += (neat.randposneg()*neat.randfloat()) * neat.trait_mutation_power
                if self.params[i] < 0:
                    self.params[i] = 0.
                if self.params[i] > 1.0:
                    self. params[i] = 1.0
        return

class TraitFromNine(Trait):
    
    def __init__(self, id, p1, p2, p3, p4, p5, p6, p7, p8, p9):
        Trait.__init__(self)
        self.SetFromNine(id, p1, p2, p3, p4, p5, p6, p7, p8, p9)
        return

class TraitFromOther(Trait):

    def __init__(self, other):
        Trait.__init__(self)
        self.SetFromOther(other)
        return

class TraitFromString(Trait):

    def __init__(self, argline):
        Trait.__init__(self)
        self.SetFromString(argline)
        return

class TraitFromAverage(Trait):

    def __init__(self, other1, other2):
        Trait.__init__(self)
        self.SetFromAverage(other1, other2)
        return

    
def main():
    t = TraitFromNine( 1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9 )
    u = TraitFromString("2 0.9 0.8 0.7 0.6 0.5 0.4 0.3 0.2 0.1")
    v = TraitFromOther(t)
    w = TraitFromAverage(t, u)
    fout = open("trait.txt", "wb")
    t.print_to_file(fout)
    u.print_to_file(fout)
    v.print_to_file(fout)
    w.print_to_file(fout)
    w.mutate()
    w.print_to_file(fout)
    fout.close()

    print "Checkout output in trait.txt"
    
    return
    
if __name__ == "__main__":
    main()

    

