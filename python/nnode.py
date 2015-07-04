from utils import matching_import
from debug import dprint
import debug
matching_import("DEBUG_.*", debug, globals())
import neat

class NNode:
    """
    // ----------------------------------------------------------------------- 
    // A NODE is either a NEURON or a SENSOR.  
    //   - If it's a sensor, it can be loaded with a value for output
    //   - If it's a neuron, it has a list of its incoming input signals (List<Link> is used) 
    // Use an activation count to avoid flushing
    """

    # NNode types
    NEURON = 0
    SENSOR = 1

    # Node place types
    HIDDEN = 0
    INPUT = 1
    OUTPUT = 2
    BIAS = 3

    # Function types
    SIGMOID = 0

    def deep_string(self):
        return str(self) + "\n"
    
    def __str__(self):
        typ = "TYPE?"
        if self.type == NNode.NEURON:
            typ = "NEURON"
        elif self.type == NNode.SENSOR:
            typ = "SENSOR"

        label = "LABEL?"
        if self.gen_node_label == NNode.HIDDEN:
            label = "HIDDEN"
        elif self.gen_node_label == NNode.INPUT:
            label = "INPUT"
        elif self.gen_node_label == NNode.OUTPUT:
            label = "OUTPUT"
        elif self.gen_node_label == NNode.BIAS:
            label = "BIAS"
        
        s = "NNode[%d] %s %s ac:%d af:%s inc:%d outg:%d" \
            % (self.node_id, label, typ, int(self.activation_count),
               str(self.active_flag), len(self.incoming), len(self.outgoing))
        return s
        
    def __init__(self):
	self.activation_count = 0 # int activation_count;  // keeps track of which activation the node is currently in
	self.last_activation = 0.0 # double last_activation; // Holds the previous step's activation for recurrency
	self.last_activation2 = 0.0 # double last_activation2; // Holds the activation BEFORE the prevous step's
        # // This is necessary for a special recurrent case when the innode
        # // of a recurrent link is one time step ahead of the outnode.
        # // The innode then needs to send from TWO time steps ago

	self.nodetrait = None # Trait *nodetrait; // Points to a trait of parameters
	self.trait_id = 1 # int trait_id;  // identify the trait derived by this node

	self.dup = None      # NNode *dup;       // Used for Genome duplication
	self.analogue = None # NNode *analogue;  // Used for Gene decoding
	self.override = False # bool override; // The NNode cannot compute its own output- something is overriding it
        self.override_value = 0.0 # double override_value; // Contains the activation value that will override this node's activation
        
	self.frozen = False  # bool frozen; // When frozen, cannot be mutated (meaning its trait pointer is fixed)
	self.ftype = NNode.SIGMOID # functype ftype; // type is either SIGMOID ..or others that can be added
	self.type = None # nodetype type; // type is either NEURON or SENSOR 
	self.activesum = 0.0 # double activesum;  // The incoming activity before being processed 
	self.activation = 0.0 # double activation; // The total activation entering the NNode 
	self.active_flag = False # bool active_flag;  // To make sure outputs are active
	self.output = 0.0

        self.params = [ 0.0 for x in range(neat.num_trait_params) ]
        self.incoming = [] # std::vector<Link*> incoming; // A list of pointers to incoming weighted signals from other nodes
        self.outgoing = [] # std::vector<Link*> outgoing;  // A list of pointers to links carrying this node's signal
        #self.rowlevels = ?
        #self.row = ?
        #self.ypos = ?
        #self.xpos = ?

        self.node_id = 0
        self.gen_node_label = None  # HIDDEN, INPUT, OUTPUT, BIAS

        self.depth_visited = False
        self.depth_max = 0
        return

    def SetFromNodeTypeAndId(self, ntype, nodeid):
	self.type = ntype; # NEURON or SENSOR type
	self.node_id = nodeid
	self.gen_node_label = NNode.HIDDEN
        return

    def SetFromNodeTypeIdAndPlacement(self, ntype, nodeid, placement):
	self.type = ntype; # NEURON or SENSOR type
	self.node_id = nodeid
	self.gen_node_label = placement
        return
        

    def SetFromNNodeAndTrait(self, n, t):
        self.type = n.type
	self.node_id = n.node_id
	self.gen_node_label = n.gen_node_label
	self.nodetrait = t
        if t is not None:
            self.trait_id = t.trait_id
        return

    def SetFromStringAndTraits(self, argline, traits):
        parts = argline.split()
        self.node_id = int(parts[0])
        traitnum = int(parts[1])
        self.type = int(parts[2])
        self.gen_node_label = int(parts[3])
        if traitnum != 0:
            for i in range(len(traits)):
                if traits[i].trait_id == traitnum:
                    break
            self.nodetrait = traits[i]
            self.trait_id = self.nodetrait.trait_id
        return
        

    def SetFromNNode(self, nnode):
	self.active_flag = nnode.active_flag
	self.activesum = nnode.activesum
	self.activation = nnode.activation
	self.output = nnode.output
	self.last_activation = nnode.last_activation
	self.last_activation2 = nnode.last_activation2
	self.type = nnode.type # NEURON or SENSOR type
	self.activation_count = nnode.activation_count # Inactive upon creation
	self.node_id = nnode.node_id
	self.ftype = nnode.ftype
	self.nodetrait = nnode.nodetrait
	self.gen_node_label = nnode.gen_node_label
	self.dup = nnode.dup
	self.analogue = nnode.dup
	self.frozen = nnode.frozen
	self.trait_id = nnode.trait_id
	self.override = nnode.override
        return
        

    def get_type(self):
        return self.type

    def set_type(self, newtype):
        self.type = newtype
        return self.type

    def sensor_load(self, value):
        if self.type == NNode.SENSOR:
            self.last_activation2 = self.last_activation
            self.last_activation = self.activation
            self.activation_count += 1
            self.activation = value
            return True
        return False

    def add_incoming(self, feednode, weight, recur=False):
        newlink = Link(weight, feednode, self, recur)
        self.incoming.append(newlink)
        feednode.outgoing.append(newlink)
        return

    def get_active_out(self):
        if self.activation_count > 0:
            return self.activation
        return 0.0

    def get_active_out_td(self):
        if self.activation_count > 1:
            return self.last_activation
        return 0.0

    def flushback(self):
        if self.type != NNode.SENSOR:
            if self.activation_count > 0:
                self.activation_count = 0
                self.activation = 0.0
                self.last_activation = 0.0
                self.last_activation2 = 0.0
            for i in range(len(self.incoming)):
                self.incoming[i].added_weight = 0.0
                if self.incoming[i].in_node.activation_count > 0:
                    self.incoming[i].in_node.flushback()
        else:
            self.activation_count = 0
            self.activation = 0.0
            self.last_activation = 0.0
            self.last_activation2 = 0.0
        return

    def flushback_check(self, seenlist):
        if self.type != NNode.SENSOR:
            if self.activation_count > 0:
                print "ALERT:",self,"has activation count",self.activation_count
            if self.activation > 0:
                print "ALERT:",self,"has activation",self.activation
            if self.last_activation > 0:
                print "ALERT:",self,"has last_activation",self.last_activation
            if self.last_activation2 > 0:
                print "ALERT:",self,"has last_activation2",self.last_activation2
            for i in range(len(self.incoming)):
                try:
                    location = seenlist.index(self.incoming[i].in_node)
                except:
                    seenlist.append(self.incoming[i].in_node)
                    self.incoming[i].in_node.flushback_check(seenlist)
        else:
            print "sALERT:",self,"has activation count",self.activation_count
            print "sALERT:",self,"has activation",self.activation
            print "sALERT:",self,"has last_activation",self.last_activation
            print "sALERT:",self,"has last_activation2",self.last_activation2

            if self.activation_count > 0:
                print "ALERT:",self,"has activation count",self.activation_count
            if self.activation > 0:
                print "ALERT:",self,"has activation",self.activation
            if self.last_activation > 0:
                print "ALERT:",self,"has last_activation",self.last_activation
            if self.last_activation2 > 0:
                print "ALERT:",self,"has last_activation2",self.last_activation2
            
        return

    def derive_trait(self, curtrait):
        if curtrait != None:
            for count in range(neat.num_trait_params):
                self.params[count] = curtrait.params[count]
            self.trait_id = curtrait.trait_id
        else:
            for count in range(neat.num_trait_params):
                self.params[count] = 0
            self.trait_id = 1
        return

    def get_analogue(self):
        return self.analogue

    def override_output(self, new_output):
        self.override_value = new_output
        self.override = True
        return

    def overridden(self):
        return self.override

    def activate_override(self):
        self.activation = self.override_value
        self.override = False
        return

    def print_to_file(self, fout):
        fout.write("node " + str(self.node_id) + " ")
        if self.nodetrait is not None:
            fout.write(str(self.nodetrait.trait_id) + " ")
        else:
            fout.write("0 ")
        fout.write(str(self.type) + " ")
        fout.write(str(self.gen_node_label) + "\n")
        return

    def depth(self, mynet):
        if self.depth_visited:
            # stop loops
            for curlink in self.incoming:
                if curlink.in_node.depth_max + 1 > self.depth_max:
                    self.depth_max = curlink.in_node.depth_max + 1
            dprint(DEBUG_INTEGRITY, "Network loop detected.  node:", self, "depth:", self.depth_max)
            return self.depth_max

        # first visit
        self.depth_visited = True
        self.depth_max = 0

        if self.type == NNode.SENSOR:
            return self.depth_max
        else:
            for curlink in self.incoming:
                cur_depth = curlink.in_node.depth(mynet)
                if cur_depth + 1 > self.depth_max:
                    self.depth_max = cur_depth + 1
            return self.depth_max


def main():
    print "Need NNode exercise code here."
    return
    
if __name__ == "__main__":
    main()
    
