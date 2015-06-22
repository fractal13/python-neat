import neat

class Trait:

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
        values = argline.split()
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

    
def main():
    t = Trait()
    u = Trait()
    v = Trait()
    w = Trait()
    t.SetFromNine( 1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9 )
    u.SetFromString("2 0.9 0.8 0.7 0.6 0.5 0.4 0.3 0.2 0.1")
    v.SetFromOther(t)
    w.SetFromAverage(t, u)
    fout = open("trait.txt", "wb")
    t.print_to_file(fout)
    u.print_to_file(fout)
    v.print_to_file(fout)
    w.print_to_file(fout)
    w.mutate()
    w.print_to_file(fout)
    fout.close()
    
if __name__ == "__main__":
    main()

    

