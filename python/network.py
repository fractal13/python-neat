from utils import matching_import
from debug import dprint, dcallstack
import debug
matching_import("DEBUG_.*", debug, globals())
from nnode import NNode
import neat

class Network:

    def __init__(self):
        self.numnodes = -1 # int number of nodes in the net (-1 not counted yet)
        self.numlinks = -1 # int number of links in the net (-1 not counted yet)
        self.all_nodes = [] # list of NNode
        self.input_iter = 0 # index into current input NNode
        self.genotype = None # Genome allows network to be matched with its genome
        self.name = "" # every network can be named
        self.inputs = [] # list of NNode that are inputs into the network
        self.outputs = [] # list of NNode that are outputs from the network
        self.net_id = 0 # int, id of network
        self.maxweight = 0.0 # float, maximum weight in the network for adaptation purposes
        self.adaptable = False # bool, can the network adapt?
        return

    def __str__(self):
        gid = 0
        if self.genotype:
            gid = self.genotype.genome_id
            
        s = "Network[%d] numnodes:%d ffnumlinks:%d all_nodes:%d input_iter:%d genotype:%d name:%s inputs:%d outputs:%d maxweight:%f adaptable:%s" \
            % (self.net_id, self.numnodes, self.numlinks, len(self.all_nodes), self.input_iter,
               int(gid), self.name, len(self.inputs), len(self.outputs),
               self.maxweight, str(self.adaptable))
        return s
    def deep_string(self):
        s = str(self) + " start\n"
        for curnode in self.all_nodes:
            s += "  " + str(curnode) + " start\n"
            for ilink in curnode.incoming:
                s += "  " + "  " + "ilink: " + str(ilink) + "\n"
            for olink in curnode.outgoing:
                s += "  " + "  " + "olink: " + str(olink) + "\n"
            s += "  " + str(curnode) + " end\n"
        s += "Network[%d] end\n" % (self.net_id) 
        return s

    def verify(self):
        # check the genome
        if self.genotype:
            if not self.genotype.verify():
                dprint(DEBUG_ERROR, "Genome not verified.")
                return False
                
        # make sure we have outputs and inputs
        if len(self.outputs) == 0:
            dcallstack(DEBUG_ERROR)
            dprint(DEBUG_INTEGRITY, "NO_OUTPUTS", str(self))
            return False
        if len(self.inputs) == 0:
            dcallstack(DEBUG_ERROR)
            dprint(DEBUG_INTEGRITY, "NO_INPUTS", str(self))
            return False

        # Note: connectivity is not strictly required.
        # It's possible for nodes to be disconnected during evolution.
        if debug.is_set(DEBUG_INTEGRITY):
            
            # check connectivity
            for curnode in self.all_nodes:

                if curnode.type != NNode.SENSOR:
                    # should have inputs
                    if len(curnode.incoming) == 0:
                        dcallstack(DEBUG_ERROR)
                        dprint(DEBUG_ERROR, "Node without incoming:", str(curnode))
                        return False
                    # each incoming link should have curnode as out_node
                    for ilink in curnode.incoming:
                        onode = ilink.out_node
                        if onode != curnode:
                            dcallstack(DEBUG_ERROR)
                            dprint(DEBUG_ERROR, "curnode.incoming[?].out_node isn't curnode.",
                                   "curnode:", str(curnode), "ilink:", str(ilink),
                                   "out_node:", str(ilink.out_node))
                            return False

                if curnode.gen_node_label != NNode.OUTPUT:
                    # should have outputs
                    if len(curnode.outgoing) == 0:
                        dcallstack(DEBUG_ERROR)
                        dprint(DEBUG_ERROR, "Node without outgoing:", str(curnode))
                        return False
                    # each outgoing link should have curnode as in_node
                    for olink in curnode.outgoing:
                        if olink.in_node != curnode:
                            dcallstack(DEBUG_ERROR)
                            dprint(DEBUG_ERROR, "curnode.outgoing[?].in_node isn't curnode.",
                                   "curnode:", str(curnode), "olink:", str(olink),
                                   "in_node:", (olink.in_node))
                            return False
        return True
        
    def SetFromLists(self, ins, outs, alls, netid, adaptval=False):
        self.inputs = ins
        self.outputs = outs
        self.all_nodes = alls
        self.net_id = netid
        self.adaptable = adaptval
        return

    def SetFromId(self, netid, adaptval=False):
        self.net_id = netid
        return

    def SetFromOther(self, other):
        for curnode in other.inputs:
            n = NNode()
            n.SetFromNNode(curnode)
            self.inputs.append(n)
            self.all_nodes.append(n)
            
        for curnode in other.outputs:
            n = NNode()
            n.SetFromNNode(curnode)
            self.outputs.append(n)
            self.all_nodes.append(n)

        self.name = other.name
        self.numnodes = other.numnodes
        self.numlinks = other.numlinks
        self.net_id = other.net_id
        self.adaptable = other.adaptable
        return

    # Return network to initial state
    def flush(self):
        for curnode in self.outputs:
            curnode.flushback()
        return

    # Check network state
    def flush_check(self):
        seenlist = []
        for curnode in self.outputs:
            try:
                location = seenlist.index(curnode)
            except:
                seenlist.append(curnode)
                curnode.flushback_check(seenlist)
        return

    def activate(self):
        abortcount = 0
        onetime = False
        while self.outputsoff() or (not onetime):
            abortcount += 1
            if abortcount >= 20:
                return False

            # for each (non-sensor) node, compute the sum of its incoming activation
            for curnode in self.all_nodes:
                if curnode.type != NNode.SENSOR:
                    curnode.activesum = 0.0
                    curnode.active_flag = False

                    for curlink in curnode.incoming:
                        if not curlink.time_delay:
                            add_amount = curlink.weight * curlink.in_node.get_active_out()
                            if curlink.in_node.active_flag or curlink.in_node.type == NNode.SENSOR:
                                curnode.active_flag = True
                            curnode.activesum += add_amount
                        else:
                            add_amount = curlink.weight * curlink.in_node.get_active_out_td()
                            curnode.activesum += add_amount

            # now, activate all non-sensor nodes off their incoming activation
            for curnode in self.all_nodes:
                if curnode.type != NNode.SENSOR:
                    
                    # only activated nodes
                    if curnode.active_flag:
                        # keep memory of past activations, for time delayed connections
                        curnode.last_activation2 = curnode.last_activation
                        curnode.last_activation = curnode.activation

                        if curnode.overridden():
                            curnode.activate_override()
                        else:
                            if curnode.ftype == NNode.SIGMOID:
                                curnode.activation = neat.fsigmoid(curnode.activesum, 4.924273, 2.4621365)
                        curnode.activation_count += 1

            onetime = True

        if self.adaptable:
            # ADAPTATION:  Adapt weights based on activations, for non-sensors
            for curnode in self.all_nodes:
                if curnode.type != NNode.SENSOR:
                    # For each incoming connection, perform adaptation based on the trait of the connection 
                    for curlink in curnode.incoming:
                        if (curlink.trait_id == 2 or
                            curlink.trait_id == 3 or
                            curlink.trait_id == 4):
                            # In the recurrent case we must take the last activation of the
                            # input for calculating hebbian changes
                            if curlink.is_recurrent:
                                curlink.weight = neat.hebbian(curlink.weight, self.maxweight,
                                                              curlink.in_node.last_activation,
                                                              curlink.out_node.get_active_out(),
                                                              curlink.params[0], curlink.params[1],
                                                              curlink.params[2])
                            else:
                                curlink.weight = neat.hebbian(curlink.weight, self.maxweight,
                                                              curlink.in_node.get_active_out(),
                                                              curlink.out_node.get_active_out(),
                                                              curlink.params[0], curlink.params[1],
                                                              curlink.params[2])
        
        return True

    def show_activation(self):
        count = 1
        for outp in self.outputs:
            count += 1
        return

    def show_input(self):
        count = 1
        for inp in self.inputs:
            count += 1
        return

    def add_input(self, in_node):
        self.inputs.append(in_node)
        return

    def add_output(self, out_node):
        self.outputs.append(out_node)
        return

    # Set activation values for inputs
    def load_sensors(self, sensvals):
        for i in range(min(len(sensvals), len(self.inputs))):
            if self.inputs[i].type == NNode.SENSOR:
                self.inputs[i].sensor_load(sensvals[i])
        return

    # Overrides the outputs' activations with these values (used for adaptation)
    def override_outputs(self, outvals):
        i = 0
        for out in self.outputs:
            out.override_output(outvalus[i])
            i += 1
        return

    def give_name(self, new_name):
        self.name = new_name
        return

    # Check a potential link between an in_node and an out_node to see if the link must be recurrent
    def is_recur(self, potin_node, potout_node, count, thresh):
        count += 1
        if count > thresh:
            # too many visits, stop looking
            return False, count

        if potin_node == potout_node:
            # found a loop
            return True, count

        # check incoming links on the in_node
        for curlink in potin_node.incoming:
            # skip known recurrent links
            if not curlink.is_recurrent:
                ok, count = self.is_recur(curlink.in_node, potout_node, count, thresh)
                if ok:
                    return True, count

        # No loops found here
        return False, count

    # Initialize the loop counter
    def input_start(self):
        self.input_iter = 0
        return 1

    # Load the next input, incrementing the loop counter
    def load_in(self, d):
        self.inputs[self.input_iter].sensor_load(d)
        self.input_iter += 1
        if self.input_iter >= len(self.inputs):
            return 0
        return 1

    # Return True if any output is not active
    def outputsoff(self):
        for curnode in self.outputs:
            if curnode.activation_count == 0:
                return True
        return False

    def print_links_tofile(self, filename):
        fout = open(filename, "w")

        for curnode in self.all_nodes:
            if curnode.type != NNode.SENSOR:
                for curlink in curnode.incoming:
                    s = str(curlink.in_node.node_id) + " -> " + str(curlink.out_node.node_id) + " : " + curlink.weight + "\n"
                    fout.write(s)
        
        fout.close()
        return

    # Find the maximum number of neurons between an output and an input
    def max_depth(self):
        mx = 0
        for o in self.outputs:
            for curnode in self.all_nodes:
                curnode.depth_max = 0
                curnode.depth_visited = False
            cur_depth = o.depth(self)
            dprint(DEBUG_INTEGRITY, "Output Node:", o, "depth:", cur_depth)
            if cur_depth > mx:
                mx = cur_depth
        return mx

def main():
    print "Need Network tests"
    return
    
if __name__ == "__main__":
    main()
    
