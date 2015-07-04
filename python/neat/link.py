from utils import matching_import
from debug import dprint
import debug
matching_import("DEBUG_.*", debug, globals())
import neat

class Link:

    def __str__(self):
        if self.in_node:
            in_id = self.in_node.node_id
        else:
            in_id = 0
        if self.out_node:
            out_id = self.out_node.node_id
        else:
            out_id = 0
        s = "Link[%d:%d] w:%g" % (in_id, out_id, self.weight)
        return s
    
    def __init__(self):
        self.weight = 0.0   # float weight of connection
        self.in_node = None # NNode input into the link
        self.out_node = None # NNode output from the link
        self.is_recurrent = False # bool
        self.time_delay = False # bool
        self.linktrait = None # Trait of parameters for genetic creation
        self.trait_id = 1 # int, trait id used by this link
        self.added_weight = 0.0 # float the amount of weight adjustment
        self.params = [ 0.0 for x in range(neat.num_trait_params) ]
        return

    def SetFromWeight(self, w, inode, onode, recur):
        self.weight = w
        self.in_node = inode
        self.out_node = onode
        self.is_recurrent = recur
        return

    def SetFromTrait(self, lt, w, inode, onode, recur):
        self.linktrait = lt
        self.weight = w
        self.in_node = inode
        self.out_node = onode
        self.is_recurrent = recur
        if lt is not None:
            self.trait_id = lt.trait_id
        return

    def SetFromWeightOnly(self, w):
        self.weight = w
        return

    def SetFromOther(self, other):
        self.weight = other.weight
        self.in_node = other.in_node
        self.out_node = other.out_node
        self.is_recurrent = other.is_recurrent
        self.added_weight = other.added_weight
        self.linktrait = other.linktrait
        self.time_delay = other.time_delay
        self.trait_id = other.trait_id
        return

    def derive_trait(self, curtrait):
        if curtrait is not None:
            self.trait_id = curtrait.trait_id
            for i in range(neat.num_trait_params):
                self.params[i] = curtrait.params[i]
        else:
            self.trait_id = 1
            for i in range(neat.num_trait_params):
                self.params[i] = 0.0

        return


def main():
    print "Need Link exercise code here."
    return
    
if __name__ == "__main__":
    main()
