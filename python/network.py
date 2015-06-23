class Network:

    def __init__(self):
        self.numnodes = 0 # int number of nodes in the net (-1 not counted yet)
        self.numlinks = 0 # int number of links in the net (-1 not counted yet)
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

    def SetFromLists(self, ins, outs, alls, netid, adaptval=False):
        ???
        return

    def SetFromId(self, netid, adaptval=False):
        ???
        return

    def SetFromOther(self, other):
        ???
        return

    def flush(self):
        ???
        return

    def flush_check(self):
        ???
        return

    def activate(self):
        ???
        return

    def show_activation(self):
        ???
        return

    def show_input(self):
        ???
        return

    def add_input(self, in_node):
        ???
        return

    def add_output(self, out_node):
        ???
        return

    def load_sensors(self, sensvals):
        ???
        return

    def override_outputs(self, outputs):
        ???
        return

    def give_name(self, new_name):
        ???
        return

    def nodecount(self):
        ???
        return

    def linkcount(self):
        ???
        return

    def is_recur(self, potin_node, potout_node, count??ref, thresh):
        ???
        return

    def input_start(self):
        ???
        return

    def load_in(self, d):
        ???
        return

    def outputsoff(self):
        ???
        return

    def print_links_tofile(self, filename):
        ???
        return

    def max_depth(self):
        ???
        return
    
    
