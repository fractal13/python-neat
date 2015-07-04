from utils import matching_import
from debug import dprint, dcallstack
import debug
matching_import("DEBUG_.*", debug, globals())
from trait import Trait
from nnode import NNode
from gene import Gene
from link import Link
from network import Network
from innovation import Innovation
import neat

class Genome:
    """
    //----------------------------------------------------------------------- 
    //A Genome is the primary source of genotype information used to create   
    //a phenotype.  It contains 3 major constituents:                         
    //  1) A list of Traits                                                 
    //  2) A list of NNodes pointing to a Trait from (1)                      
    //  3) A list of Genes with Links that point to Traits from (1)           
    //(1) Reserved parameter space for future use
    //(2) NNode specifications                                                
    //(3) Is the primary source of innovation in the evolutionary Genome.     
    //    Each Gene in (3) has a marker telling when it arose historically.   
    //    Thus, these Genes can be used to speciate the population, and the   
    //    list of Genes provide an evolutionary history of innovation and     
    //    link-building.
    """

    GAUSSIAN = 0
    COLDGAUSSIAN = 1

    def __init__(self):
        self.genome_id = 0 # int,
        self.traits = [] # list of Trait, parameter conglomerations
        self.nodes = [] # list of NNode, NNodes for the network
        self.genes = [] # list of Gene, innovation tracking
        self.phenotype = None # Network, Allows Genome to be matched with its Network
        return

    def deep_string(self):
        s = "Genome[%d]:start\n" % (self.genome_id, )
        for curtrait in self.traits:
            s += "  " + curtrait.deep_string()
        for curnode in self.nodes:
            s += "  " + curnode.deep_string()
        for curgene in self.genes:
            s += "  " + curgene.deep_string()
        if self.phenotype:
            s += "  " + self.phenotype.deep_string()
        s += "Genome[%d]:end\n" % (self.genome_id, )
        return s
        
    ##//Constructor which takes full genome specs and puts them into the new one
    def SetFromSpecs(self, gid, traits, nodes, genes):
        self.genome_id = gid
        self.traits = traits
        self.nodes = nodes
        self.genes = genes
        return

    ##//Constructor which takes in links (not genes) and creates a Genome
    def SetFromLinks(self, gid, traits, nodes, links):
        self.genome_id = gid
        self.traits = traits
        self.nodes = nodes

        for curlink in links:
            tempgene = Gene()
            tempgene.SetFromTraitAndValues(curlink.linktrait, curlink.weight, curlink.in_node, curlink.out_node, curlink.is_recurrent, 1.0, 0.0)
            self.genes.append(tempgene)
        
        return

    ##// Copy constructor
    def SetFromOther(self, other):
        self.genome_id = other.genome_id

        # duplicate Traits
        for curtrait in other.traits:
            t = Trait()
            t.SetFromOther(curtrait)
            self.traits.append(t)

        # duplicate NNodes
        for curnode in other.nodes:
            if curnode.nodetrait is None:
                assoc_trait = None
            else:
                assoc_trait = None
                for curtrait in self.traits:
                    if curtrait.trait_id == curnode.nodetrait.trait_id:
                        assoc_trait = curtrait
                        break
            newnode = NNode()
            newnode.SetFromNNodeAndTrait(curnode, assoc_trait)
            curnode.dup = newnode
            self.nodes.append(newnode)
        
        # duplicate Genes
        for curgene in other.genes:
            inode = curgene.lnk.in_node.dup
            onode = curgene.lnk.out_node.dup

            trait = curgene.lnk.linktrait
            if trait is None:
                assoc_trait = None
            else:
                assoc_trait = None
                for curtrait in self.traits:
                    if curtrait.trait_id == trait.trait_id:
                        assoc_trait = curtrait
                        break
                        
            newgene = Gene()
            newgene.SetFromGeneAndValues(curgene, assoc_trait, inode, onode)
            self.genes.append(newgene)
                
        return

    ##//Special constructor which spawns off an input file
    ##//This constructor assumes that some routine has already read in GENOMESTART
    def SetFromFile(self, gid, fin):
        self.genome_id = gid
        done = 0
        
        words = fin.readline().strip().split()
        dprint(DEBUG_FILEINPUT, "Genome.SetFromFile:words: ", " ".join(words))
        wordcount = len(words)
        curwordnum = 0
        while not done:
            if curwordnum > wordcount or wordcount == 0:
                words = fin.readline().strip().split()
                dprint(DEBUG_FILEINPUT, "Genome.SetFromFile:words: ", " ".join(words))
                wordcount = len(words)
                curwordnum = 0
            curword = words[curwordnum]

            if curword == "genomeend":
                # end of genome
                idcheck = int(words[curwordnum+1])
                if idcheck != self.genome_id:
                    print "ERROR: id mismatch in genome."
                done = 1

            elif curword == "genomestart":
                # start of genome
                curwordnum += 1

            elif curword == "/*":
                # ignore comments
                curwordnum += 1
                curword = words[curwordnum]
                while curword != "*/":
                    curwordnum += 1
                    curword = words[curwordnum]

            elif curword == "trait":
                argline = " ".join(words[curwordnum+1:])
                curwordnum = wordcount + 1
                newtrait = Trait()
                newtrait.SetFromString(argline)
                self.traits.append(newtrait)

            elif curword == "node":
                argline = " ".join(words[curwordnum+1:])
                curwordnum = wordcount + 1
                newnode = NNode()
                newnode.SetFromStringAndTraits(argline, self.traits)
                self.nodes.append(newnode)

            elif curword == "gene":
                argline = " ".join(words[curwordnum+1:])
                curwordnum = wordcount + 1
                newgene = Gene()
                newgene.SetFromString(argline, self.traits, self.nodes)
                self.genes.append(newgene)

            else:
                print "ERROR: Unepected curword = %s" % (curword,)
                
        return

    ##// This special constructor creates a Genome
    ##// with i inputs, o outputs, n out of nmax hidden units, and random
    ##// connectivity.  If r is true then recurrent connections will
    ##// be included. 
    ##// The last input is a bias
    ##// Linkprob is the probability of a link  
    def SetFromCounts(self, gid, i, o, n, nmax, r, linkprob):
        totalnodes = i + o + nmax
        matrixdim = totalnodes * totalnodes
        cm = []
        maxnode = i + n
        first_output = totalnodes - o + 1
        self.genome_id = gid

        # Random connection matrix
        for count in range(matrixdim):
            if neat.randfloat() < linkprob:
                cm.append(True)
            else:
                cm.append(False)

        # Dummy trait
        newtrait = Trait()
        newtrait.SetFromNine(1, 0., 0., 0., 0., 0., 0., 0., 0., 0.)
        self.traits.append(newtrait)

        # Input nodes
        for ncount in range(1, i+1):
            newnode = NNode()
            
            if ncount < i:
                placement = NNode.INPUT
            elif ncount == i:
                placement = NNode.BIAS

            newnode.SetFromNodeTypeIdAndPlacement(NNode.SENSOR, ncount, placement)
            newnode.nodetrait = newtrait
            self.nodes.append(newnode)

        # Hidden nodes
        for ncount in range(i+1, i+n+1):
            newnode = NNode()
            newnode.SetFromNodeTypeIdAndPlacement(NNode.NEURON, ncount, NNode.HIDDEN)
            newnode.nodetrait = newtrait
            self.nodes.append(newnode)

        # Output nodes
        for ncount in range(first_output, totalnodes+1):
            newnode = NNode()
            newnode.SetFromNodeTypeIdAndPlacement(NNode.NEURON, ncount, NNode.OUTPUT)
            newnode.nodetrait = newtrait
            self.nodes.append(newnode)

        # Connect nodes according to connection matrix
        ccount = 1
        count = 0
        for col in range(1, totalnodes+1):
            for row in range(1, totalnodes+1):

                # link is set in matrix, and doesn't lead into a sensor
                if ((cm[col*totalnodes+row]) and (col > i) and
                    ((col <= maxnode) or (col >= first_output)) and
                    ((row <= maxnode) or (row >= first_output))):

                    if col > row or r:
                        # col > row  -->> not recurrent link, create it
                        is_recur = False
                        # col <= row and r -->> recurrent link, create it anyways
                        if col <= row and r:
                            is_recur = True

                        # in_node
                        for node_iter in self.nodes:
                            if node_iter.node_id == row:
                                in_node = node_iter
                                break
                                
                        # out_node
                        for node_iter in self.nodes:
                            if node_iter.node_id == col:
                                out_node = node_iter
                                break

                        # Gene
                        new_weight = neat.randposneg() * neat.randfloat()
                        newgene = Gene()
                        newgene.SetFromTraitAndValues(newtrait, new_weight, in_node, out_node, is_recur, count, new_weight)

                        self.genes.append(newgene)
                        
                count += 1
            
        return

    ##//Special constructor that creates a Genome of 3 possible types:
    ##//0 - Fully linked, no hidden nodes
    ##//1 - Fully linked, one hidden node splitting each link
    ##//2 - Fully connected with a hidden layer, recurrent 
    ##//num_hidden is only used in type 2
    def SetFromCounts2(self, num_in, num_out, num_hidden, typ):
        self.genome_id = 0
        
        # Dummy trait
        newtrait = Trait()
        newtrait.SetFromNine(1, 0., 0., 0., 0., 0., 0., 0., 0., 0.)
        self.traits.append(newtrait)

	# Adjust hidden number
	if typ == 0: 
            num_hidden = 0
	elif typ == 1:
            num_hidden = num_in*num_out

        # Input nodes
        inputs = []
        for ncount in range(1, num_in+1):
            newnode = NNode()
            
            if ncount < num_in:
                placement = NNode.INPUT
            elif ncount == i:
                placement = NNode.BIAS
                bias = newnode

            newnode.SetFromNodeTypeIdAndPlacement(NNode.SENSOR, ncount, placement)
            self.nodes.append(newnode)
            inputs.append(newnode)

        # Hidden nodes
        hidden = []
        for ncount in range(num_in+1, num_in+num_hidden+1):
            newnode = NNode()
            newnode.SetFromNodeTypeIdAndPlacement(NNode.NEURON, ncount, NNode.HIDDEN)
            self.nodes.append(newnode)
            hidden.append(newnode)

        # Output nodes
        outputs = []
        for ncount in range(num_in+num_hidden+1, num_in+num_hidden+num_out+1):
            newnode = NNode()
            newnode.SetFromNodeTypeIdAndPlacement(NNode.NEURON, ncount, NNode.OUTPUT)
            self.nodes.append(newnode)
            outputs.append(newnode)

        # Create links
        if typ == 0:
            # inputs connected directly to outputs
            count = 1
            for curnode1 in outputs:
                for curnode2 in inputs:
                    newgene = Gene()
                    newgene.SetFromTraitAndValues(newtrait, 0., curnode2, curnode1, False, count, 0.)
                    self.genes.append(newgene)
                    count += 1

        elif typ == 1:
            # A split link from each input to each output
            count = 1
            hidden_i = 0

            for curnode1 in outputs:
                for curnode2 in inputs:
                    curnode3 = hidden[hidden_i]
                    
                    newgene = Gene()
                    newgene.SetFromTraitAndValues(newtrait, 0., curnode2, curnode3, False, count, 0.)
                    self.genes.append(newgene)
                    count += 1

                    newgene = Gene()
                    newgene.SetFromTraitAndValues(newtrait, 0., curnode3, curnode1, False, count, 0.)
                    self.genes.append(newgene)
                    count += 1

                    hidden_i += 1

        elif typ == 2:
            # Fully connected
            count = 1

            # All inputs to all hidden
            for curnode1 in hidden:
                for curnode2 in inputs:
                    newgene = Gene()
                    newgene.SetFromTraitAndValues(newtrait, 0., curnode2, curnode1, False, count, 0.)
                    self.genes.append(newgene)
                    count += 1

            # All hidden to all outputs
            for curnode1 in outputs:
                for curnode2 in hidden:
                    newgene = Gene()
                    newgene.SetFromTraitAndValues(newtrait, 0., curnode2, curnode1, False, count, 0.)
                    self.genes.append(newgene)
                    count += 1

            # Bias to all outputs
            for curnode1 in outputs:
                newgene = Gene()
                newgene.SetFromTraitAndValues(newtrait, 0., bias, curnode1, False, count, 0.)
                self.genes.append(newgene)
                count += 1

            # All hidden to all hidden (recurrent)
            for curnode1 in hidden:
                for curnode2 in hidden:
                    newgene = Gene()
                    newgene.SetFromTraitAndValues(newtrait, 0., curnode2, curnode1, True, count, 0.)
                    self.genes.append(newgene)
                    count += 1

        # Done
        return

    ##// Loads a new Genome from a file (doesn't require knowledge of Genome's id)
    @classmethod
    def new_Genome_load(cls, filename):
        newgenome = cls()
        fin = open(filename, "r")
        if not fin:
            dprint(DEBUG_ERROR, "Unable to open file %s." % (filename, ))
            return None
            
        done = False
        while (not done) and fin:
            words = fin.readline().strip().split()
            if words[0] == "/*":
                words = fin.readline().strip().split()
            elif words[0] == "genomestart":
                gid = int(words[1])
                done = True
            else:
                print "ERROR: Bad line at head of genome file:", " ".join(words)
                
        newgenome.SetFromFile(gid, fin)
        fin.close()
        return newgenome

    ##//Generate a network phenotype from this Genome with specified id
    def genesis(self, nid):
        maxweight = 0.0
        inlist = []
        outlist = []
        all_list = []
        
        # create nodes
        for curnode in self.nodes:
            newnode = NNode()
            newnode.SetFromNodeTypeIdAndPlacement(curnode.type, curnode.node_id, curnode.gen_node_label)

            # Trait parameters
            curtrait = curnode.nodetrait
            newnode.derive_trait(curtrait)

            # Placement
            if curnode.gen_node_label == NNode.INPUT:
                inlist.append(newnode)
            elif curnode.gen_node_label == NNode.BIAS:
                inlist.append(newnode)
            elif curnode.gen_node_label == NNode.OUTPUT:
                outlist.append(newnode)
            all_list.append(newnode)

            # track generation for later use
            curnode.analogue = newnode

        # create links
        for curgene in self.genes:
            if curgene.enable:
                curlink = curgene.lnk
                inode = curlink.in_node.analogue
                onode = curlink.out_node.analogue

                newlink = Link()
                newlink.SetFromWeight(curlink.weight, inode, onode, curlink.is_recurrent)
                onode.incoming.append(newlink)
                inode.outgoing.append(newlink)

                curtrait = curlink.linktrait
                newlink.derive_trait(curtrait)

                maxweight = max(maxweight, abs(newlink.weight))

        # create network
        newnet = Network()
        newnet.SetFromLists(inlist, outlist, all_list, nid)

        newnet.maxweight = maxweight
        
        # connect genome and network
        newnet.genotype = self
        self.phenotype = newnet

        return newnet

    ##// Dump this genome to specified file
    def print_to_file(self, fout):
        # header
        s = "genomestart " + str(self.genome_id) + "\n"
        fout.write(s)

        # traits
        trait_id = 1
        for curtrait in self.traits:
            curtrait.trait_id = trait_id
            curtrait.print_to_file(fout)
            trait_id += 1

        # nodes
        for curnode in self.nodes:
            curnode.print_to_file(fout)

        # genes
        for curgene in self.genes:
            curgene.print_to_file(fout)
            
        # footer
        s = "genomeend " + str(self.genome_id) + "\n"
        fout.write(s)
        return

    ##// Wrapper for print_to_file above
    def print_to_filename(self, filename):
        fout = open(filename, "w")
        self.print_to_file(fout)
        fout.close()
        return

    ##// Duplicate this Genome to create a new one with the specified id 
    def duplicate(self, new_id):

        # Traits
        traits_dup = []
        for curtrait in self.traits:
            newtrait = Trait()
            newtrait.SetFromOther(curtrait)
            traits_dup.append(newtrait)
            
        # NNodes
        nodes_dup = []
        for curnode in self.nodes:
            # find Trait
            if curnode.nodetrait is None:
                assoc_trait = None
            else:
                assoc_trait = None
                for curtrait in traits_dup:
                    if curtrait.trait_id == curnode.nodetrait.trait_id:
                        assoc_trait = curtrait
                        break
                        
            newnode = NNode()
            newnode.SetFromNNodeAndTrait(curnode, assoc_trait)
            curnode.dup = newnode
            nodes_dup.append(newnode)
            
        # Genes
        genes_dup = []
        for curgene in self.genes:
            # find nodes
            inode = curgene.lnk.in_node.dup
            onode = curgene.lnk.out_node.dup
            # find trait
            traitptr = curgene.lnk.linktrait
            if traitptr is None:
                assoc_trait = None
            else:
                assoc_trait = None
                for curtrait in traits_dup:
                    if curtrait.trait_id == traitptr.trait_id:
                        assoc_trait = curtrait
                        break

            newgene = Gene()
            newgene.SetFromGeneAndValues(curgene, assoc_trait, inode, onode)
            genes_dup.append(newgene)
            
        # Genome
        newgenome = Genome()
        newgenome.SetFromSpecs(new_id, traits_dup, nodes_dup, genes_dup)

        return newgenome

    # debug integrity of structure
    def check_output_count_aux(self, nodelist):
        count = 0
        for curnode in nodelist:
            if curnode.gen_node_label == NNode.OUTPUT:
                count += 1
        if count == 0:
            raise Exception("output count is 0")
            return False
        return True
        
    def check_output_count(self):
        self.check_output_count_aux(self.nodes)
        
    ##// For debugging: A number of tests can be run on a genome to check its
    ##// integrity
    ##// Note: Some of these tests do not indicate a bug, but rather are meant
    ##// to be used to detect specific system states
    def verify(self):
        
        # Check for duplicate NNode_node_id
        node_ids = set()
        for curnode in self.nodes:
            if curnode.node_id in node_ids:
                dcallstack(DEBUG_ERROR)
                dprint(DEBUG_ERROR, "Duplicate node id:", curnode)
                return False
            node_ids.add(curnode.node_id)
        node_ids = None
            
        
        # Check the genes' nodes
        for curgene in self.genes:
            inode = curgene.lnk.in_node
            onode = curgene.lnk.out_node

            # is inode found?
            found = False
            for curnode in self.nodes:
                if curnode == inode:
                    found = True
                    break
            if not found:
                dcallstack(DEBUG_ERROR)
                dprint(DEBUG_ERROR, "inode not found")
                return False
                
            found = False
            for curnode in self.nodes:
                if curnode == onode:
                    found = True
                    break
            if not found:
                dcallstack(DEBUG_ERROR)
                dprint(DEBUG_ERROR, "onode not found")
                return False

        # Check nodes are in order
        last_id = 0
        for curnode in self.nodes:
            if curnode.node_id < last_id:
                dcallstack(DEBUG_ERROR)
                dprint(DEBUG_ERROR, "node_id out of order")
                return False
            last_id = curnode.node_id

        # Check for duplicate genes
        for curgene in self.genes:
            for curgene2 in self.genes:
                if ((curgene != curgene2) and
                    ((curgene.lnk.is_recurrent == curgene2.lnk.is_recurrent) and
                     (curgene.lnk.in_node.node_id == curgene2.lnk.in_node.node_id) and
                     (curgene.lnk.out_node.node_id == curgene2.lnk.out_node.node_id))):
                    pass
                    #print "ALERT: Duplicate Genes"
                    #return False

        # 2 disables in a row?
        # not necessarily bad
        if len(self.nodes) >= 500:
            disab = False
            for curgene in self.genes:
                if (not curgene.enable) and (disab):
                    # two in a row
                    pass
                disab = not curgene.enable
                    
        #
        return True


    ##// ******* MUTATORS *******

    ##// Perturb params in one trait
    def mutate_random_trait(self):
        traitnum = neat.randint(0, len(self.traits)-1)
        thetrait = self.traits[traitnum]
        thetrait.mutate()
        return

    ##// Change random link's trait. Repeat times times
    def mutate_link_trait(self, times):

        for loop in range(times):
            traitnum = neat.randint(0, len(self.traits)-1)
            thetrait = self.traits[traitnum]
            
            genenum = neat.randint(0, len(self.genes)-1)
            thegene = self.genes[genenum]
            
            if not thegene.frozen:
                thegene.lnk.linktrait = thetrait

        return

    ##// Change random node's trait times times 
    def mutate_node_trait(self, times):
        for loop in range(times):
            traitnum = neat.randint(0, len(self.traits)-1)
            thetrait = self.traits[traitnum]
            
            nodenum = neat.randint(0, len(self.nodes)-1)
            thenode = self.nodes[nodenum]

            if not thenode.frozen:
                thenode.nodetrait = thetrait
        #
        return

    ##// Add Gaussian noise to linkweights either GAUSSIAN or COLDGAUSSIAN (from zero)
    def mutate_link_weights(self, power, rate, mut_type):
        if neat.randfloat() > 0.5:
            severe = True
        else:
            severe = False

        num = 0.0
        gene_total = float(len(self.genes))
        endpart = gene_total * 0.8
        powermod = 1.0
        for curgene in self.genes:
            if not curgene.frozen:
                if severe:
                    gausspoint = 0.3
                    coldgausspoint = 0.1
                elif gene_total >= 10.0 and num > endpart:
                    gausspoint = 0.5
                    coldgausspoint = 0.3
                else:
                    if neat.randfloat() > 0.5:
                        gausspoint = 1.0 - rate
                        coldgausspoint = 1.0 - rate - 0.1
                    else:
                        gausspoint = 1.0 - rate
                        coldgausspoint = 1.0 - rate

                # modify the gene link weight
                randnum = neat.randposneg() * neat.randfloat() * power * powermod
                if mut_type == Genome.GAUSSIAN:
                    randchoice = neat.randfloat()
                    if randchoice > gausspoint:
                        curgene.lnk.weight += randnum
                    elif randchoice > coldgausspoint:
                        curgene.lnk.weight = randnum
                elif mut_type == Genome.COLDGAUSSIAN:
                    curgene.lnk.weight = randnum

                if curgene.lnk.weight > 8.0:
                    curgene.lnk.weight = 8.0
                elif curgene.lnk.weight < -8.0:
                    curgene.lnk.weight = -8.0
                    
                # record it
                curgene.mutation_num = curgene.lnk.weight
                num += 1.0
        return

    ##// toggle genes on or off 
    def mutate_toggle_enable(self, times):
        for count in range(times):
            genenum = neat.randint(0, len(self.genes)-1)
            thegene = self.genes[genenum]

            if thegene.enable:
                # disable if safe
                found = False
                for checkgene in range(len(self.genes)):
                    g = self.genes[checkgene]
                    if ((g.lnk.in_node == thegene.lnk.in_node) and
                        (g.enable) and
                        (g.innovation_num != thegene.innovation_num)):
                        found = True
                        break
                if found:
                    thegene.enable = False
            else:
                # enable
                thegene.enable = True
                
        return

    ##// Find first disabled gene and enable it 
    def mutate_gene_reenable(self):
        for thegene in self.genes:
            if not thegene.enable:
                thegene.enable = True
                break
        return

    ##// These last kinds of mutations return false if they fail
    ##//   They can fail under certain conditions,  being unable
    ##//   to find a suitable place to make the mutation.
    ##//   Generally, if they fail, they can be called again if desired. 

    def have_innovation(self, innov_num):
        min_i = 0
        max_i = len(self.genes)
        mid_i = (max_i + min_i) / 2
        while (max_i >= min_i) and (mid_i < len(self.genes)):
            if self.genes[mid_i].innovation_num == innov_num:
                return True
            elif self.genes[mid_i].innovation_num < innov_num:
                min_i = mid_i + 1
            else:
                max_i = mid_i - 1
            mid_i = (max_i + min_i) / 2
        return False
        
    def have_node(self, node_id):
        min_i = 0
        max_i = len(self.nodes)
        mid_i = (max_i + min_i) / 2
        while (max_i >= min_i) and (mid_i < len(self.nodes)):
            if self.nodes[mid_i].node_id == node_id:
                return True
            elif self.nodes[mid_i].node_id < node_id:
                min_i = mid_i + 1
            else:
                max_i = mid_i - 1
            mid_i = (max_i + min_i) / 2
        return False
    
    ##// Mutate genome by adding a node respresentation 
    def mutate_add_node(self, innovs, curnode_id, curinnov):

        done = False
        trycount = 0
        found = False
        while trycount < 20 and not found:
            genenum = neat.randint(0, len(self.genes)-1)
            thegene = self.genes[genenum]
            if thegene.enable and thegene.lnk.in_node.gen_node_label != NNode.BIAS:
                found = True
            trycount += 1

        #
        if not found:
            return False, curnode_id, curinnov
        #
        thegene.enable = False
        #
        thelink = thegene.lnk
        oldweight = thegene.lnk.weight
        in_node = thelink.in_node
        out_node = thelink.out_node
        #
        innov_i = 0
        while not done:
            if innov_i < len(innovs):
                theinnov = innovs[innov_i]
            if innov_i >= len(innovs):
                if self.have_node(curnode_id):
                    dprint(DEBUG_ERROR, "Already have node with this id:", curnode_id)
                if self.have_innovation(curinnov):
                    dprint(DEBUG_ERROR, "Already have innovation with this id[0]:", curinnov)
                if self.have_innovation(curinnov+1):
                    dprint(DEBUG_ERROR, "Already have innovation with this id[1]:", curinnov+1)
                # new innovation
                trait = thelink.linktrait
                newnode = NNode()
                newnode.SetFromNodeTypeIdAndPlacement(NNode.NEURON, curnode_id, NNode.HIDDEN)
                curnode_id += 1
                newnode.nodetrait = self.traits[0]

                newgene1 = Gene()
                newgene2 = Gene()
                newgene1.SetFromTraitAndValues(trait, 1.0, in_node, newnode, thelink.is_recurrent, curinnov, 0.0)
                newgene2.SetFromTraitAndValues(trait, oldweight, newnode, out_node, False, curinnov+1, 0.0)
                curinnov += 2

                innov = Innovation(in_node.node_id, out_node.node_id, curinnov-2.0)
                innov.SetNewNode(curinnov-1.0, newnode.node_id, thegene.innovation_num)
                innovs.append(innov)
                done = True


            elif ((theinnov.innovation_type == Innovation.NEWNODE) and
                  (theinnov.node_in_id == in_node.node_id) and
                  (theinnov.node_out_id == out_node.node_id) and
                  (theinnov.old_innov_num == thegene.innovation_num) and
                  (not self.have_innovation(theinnov.innovation_num1)) and
                  (not self.have_innovation(theinnov.innovation_num2)) and
                  (not self.have_node(theinnov.newnode_id))):
                trait = thelink.linktrait
                
                newnode = NNode()
                newnode.SetFromNodeTypeIdAndPlacement(NNode.NEURON, theinnov.newnode_id, NNode.HIDDEN)
                newnode.nodetrait = self.traits[0]

                newgene1 = Gene()
                newgene2 = Gene()
                newgene1.SetFromTraitAndValues(trait, 1.0, in_node, newnode, thelink.is_recurrent, theinnov.innovation_num1, 0.0)
                newgene2.SetFromTraitAndValues(trait, oldweight, newnode, out_node, False, theinnov.innovation_num2, 0.0)

                done = True
                
            else:
                innov_i += 1

        #
        self.add_gene(self.genes, newgene1)
        self.add_gene(self.genes, newgene2)
        self.node_insert(self.nodes, newnode)

        return True, curnode_id, curinnov

    ##// Mutate the genome by adding a new link between 2 random NNodes 
    def mutate_add_link(self, innovs, curinnov, tries):
        
        found = False
        
        thresh = len(self.nodes)*len(self.nodes)
        count = 0
        
        trycount = 0
        
        if neat.randfloat() < neat.recur_only_prob:
            do_recur = True
        else:
            do_recur = False

        first_nonsensor = 0
        for thenode1 in self.nodes:
            if thenode1.get_type() != NNode.SENSOR:
                break
            first_nonsensor += 1

        if do_recur:
            while trycount < tries:
                if neat.randfloat() > 0.5:
                    loop_recur = True
                else:
                    loop_recur = False

                if loop_recur:
                    nodenum1 = neat.randint(first_nonsensor, len(self.nodes)-1)
                    nodenum2 = nodenum1
                else:
                    nodenum1 = neat.randint(0, len(self.nodes)-1)
                    nodenum2 = neat.randint(first_nonsensor, len(self.nodes)-1)

                nodep1 = self.nodes[nodenum1]
                nodep2 = self.nodes[nodenum2]

                gene_i = 0
                while ((gene_i < len(self.genes)) and
                       (nodep2.type != NNode.SENSOR) and
                       ( not ((self.genes[gene_i].lnk.in_node == nodep1) and
                              (self.genes[gene_i].lnk.out_node == nodep2) and
                              (self.genes[gene_i].lnk.is_recurrent)))):
                    gene_i += 1
                
                if gene_i < len(self.genes):
                    trycount += 1
                else:
                    count = 0
                    recurflag, count = self.phenotype.is_recur(nodep1.analogue, nodep2.analogue, count, thresh)
                    if nodep1.type == NNode.OUTPUT or nodep2.type == NNode.OUTPUT:
                        recurflag = True

                    if not recurflag:
                        trycount += 1
                    else:
                        trycount = tries
                        found = True
                    #
                #
            #
        else:
            # not do_recur

            while trycount < tries:
                nodenum1 = neat.randint(0, len(self.nodes)-1)
                nodenum2 = neat.randint(first_nonsensor, len(self.nodes)-1)

                nodep1 = self.nodes[nodenum1]
                nodep2 = self.nodes[nodenum2]
                
                gene_i = 0
                while ((gene_i < len(self.genes)) and
                       (nodep2.type != NNode.SENSOR) and
                       ( not ((self.genes[gene_i].lnk.in_node == nodep1) and
                              (self.genes[gene_i].lnk.out_node == nodep2) and
                              (not self.genes[gene_i].lnk.is_recurrent)))):
                    gene_i += 1

                if gene_i < len(self.genes):
                    trycount += 1
                else:
                    count = 0
                    recurflag, count = self.phenotype.is_recur(nodep1.analogue, nodep2.analogue, count, thresh)
                
                    if nodep1.type == NNode.OUTPUT or nodep2.type == NNode.OUTPUT:
                        recurflag = True
                        
                    if recurflag:
                        trycount += 1
                    else:
                        trycount = tries
                        found = True
                #
            #
        #
        if found:
            innov_i = 0

            if do_recur:
                recurflag = True
                
            done = False

            while not done:
                if innov_i < len(innovs):
                    theinnov = innovs[innov_i]
                    
                if innov_i >= len(innovs):
                    if self.phenotype is None:
                        return False, curinnov

                    traitnum = neat.randint(0, len(self.traits)-1)
                    thetrait = self.traits[traitnum]

                    newweight = neat.randposneg() * neat.randfloat() * 1.0
                    
                    newgene = Gene()
                    newgene.SetFromTraitAndValues(thetrait, newweight, nodep1, nodep2, recurflag, curinnov, newweight)

                    innov = Innovation(nodep1.node_id, nodep2.node_id, curinnov)
                    innov.SetNewLink(newweight, traitnum)
                    innovs.append(innov)

                    curinnov += 1

                    done = True

                elif ((theinnov.innovation_type == Innovation.NEWLINK) and
                      (theinnov.node_in_id == nodep1.node_id) and
                      (theinnov.node_out_id == nodep2.node_id) and
                      (theinnov.recur_flag == recurflag)):
                    
                    newgene = Gene()
                    newgene.SetFromTraitAndValues(self.traits[theinnov.new_traitnum], theinnov.new_weight,
                                                  nodep1, nodep2, recurflag, theinnov.innovation_num1, 0.0)
                    done = True
                else:
                    innov_i += 1
                #
            #
            self.add_gene(self.genes, newgene)
            return True, curinnov
            
        else:
            # not found
            return False, curinnov
        #

    # this code doesn't appear to get called
    def mutate_add_sensor(self, innovs, curinnov):
        newweight = 0.0
        sensors = []
        outputs = []
        for node in self.nodes:
            if node.type == NNode.SENSOR:
                sensors.append(node)
            elif node.gen_node_label == NNode.OUTPUT:
                outputs.append(node)

        # eliminate any sensors that are already connected
        # - This code doesn't seem to do what the comment says. - cgl
        keep_sensors = []
        for sensor in sensors:
            outputConnections = 0
            for genes in self.genes:
                if gene.lnk.out_node.gen_node_label == NNode.OUTPUT:
                    outputConnections += 1
            if outputConnections != len(outputs):
                keep_sensors.append(sensor)
        sensors = keep_sensors

        if len(sensors) == 0:
            return False, curinnov
        #

        sensor = random.choice(sensors)

        for output in outputs:
            found = False
            for gene in genes:
                if gene.lnk.in_node == sensor and gene.lnk.out_node == output:
                    found = True
                    break
            #
            if found:
                innov_i = 0
                done = False

                while not done:
                    if innov_i < len(innovs):
                        theinnov = innovs[innov_i]
                        
                    if innov_i >= len(innovs):
                        traitnum = neat.randint(0, len(self.traits)-1)
                        thetrait = self.traits[traitnum]

                        newweight = neat.randposneg() * neat.randfloat() * 3.0

                        newgene = Gene()
                        newgene.SetFromValues(thetrait, newweight, sensor, output, False, curinnov, newweight)

                        innov = Innovation(sensor.node_id, output.node_id, curinnov)
                        innov.SetNewLink(newweight, traitnum)
                        innovs.append(innov)
                        
                        curinnov += 1
                        
                        done = True
                        
                    elif ((theinnov.innovation_type == Innovation.NEWLINK) and
                          (theinnov.node_in_id == sensor.node_id) and
                          (theinnov.node_out_id == output.node_id) and
                          (theinnov.recur_flag == False)):
                        thetrait = self.traits[theinnov.new_traitnum]
                        newgene = Gene()
                        newgene.SetFromTraitAndValues(thetrait, theinnov.new_weight,
                                                      sensor, output, False, theinnov.innovation_num1, 0.0)
                        done = True
                    else:
                        innov_i += 1
                        #
                    # while not done
                self.add_gene(self.genes, newgene)
                # if found
            # for output
        # def mutate_add_sensor
        return True, curinnov
        
    ##// ****** MATING METHODS ***** 

    ##// This method mates this Genome with another Genome g.  
    ##//   For every point in each Genome, where each Genome shares
    ##//   the innovation number, the Gene is chosen randomly from 
    ##//   either parent.  If one parent has an innovation absent in 
    ##//   the other, the baby will inherit the innovation 
    ##//   Interspecies mating leads to all genes being inherited.
    ##//   Otherwise, excess genes come from most fit parent.
    def mate_multipoint(self, g, genomeid, fitness1, fitness2, interspec_flag):
        # Baby's traits
        newtraits = []
        for i in range(len(self.traits)):
            newtrait = Trait()
            newtrait.SetFromAverage(self.traits[i], g.traits[i])
            newtraits.append(newtrait)

        # Identify Best Genome
        if fitness1 > fitness2:
            p1better = True
        elif fitness1 == fitness2:
            if len(self.genes) < len(g.genes):
                p1better = True
            else:
                p1better = False
        else:
            p1better = False

            
        # Copy all sensors and outputs
        # Baby's nodes
        newnodes = []
        for curnode in g.nodes:
            if ((curnode.gen_node_label == NNode.INPUT) or
                (curnode.gen_node_label == NNode.BIAS) or
                (curnode.gen_node_label == NNode.OUTPUT)):
                if curnode.nodetrait is None:
                    nodetraitnum = 0
                else:
                    nodetraitnum = curnode.nodetrait.trait_id - self.traits[0].trait_id

                new_onode = NNode()
                new_onode.SetFromNNodeAndTrait(curnode, newtraits[nodetraitnum])
                self.node_insert(newnodes, new_onode)
                #

        # Baby's genes
        newgenes = []
        disable = False

        # Walk through genes of both parents until both genomes reach an end
        p1_i = 0
        p2_i = 0
        while p1_i < len(self.genes) or p2_i < len(g.genes):

            # choose between next gene of each parent
            skip = False
            if p1_i == len(self.genes):
                chosengene = g.genes[p2_i]
                p2_i += 1
                if p1better:
                    skip = True
            elif p2_i == len(g.genes):
                chosengene = self.genes[p1_i]
                p1_i += 1
                if not p1better:
                    skip = True
            else:
                p1innov = self.genes[p1_i].innovation_num
                p2innov = g.genes[p2_i].innovation_num

                
                if p1innov == p2innov:
                    # same innovation number, randomly chose one
                    if neat.randfloat() < 0.5:
                        chosengene = self.genes[p1_i]
                    else:
                        chosengene = g.genes[p2_i]

                    # if either parent has gene disabled, the offspring likely has it disabled too
                    if (not self.genes[p1_i].enable) or (not g.genes[p2_i]):
                        if neat.randfloat() < 0.75:
                            disable = True
                    p1_i += 1
                    p2_i += 1

                elif p1innov < p2innov:
                    # p1 is earlier, choose it
                    chosengene = self.genes[p1_i]
                    p1_i += 1
                    if not p1better:
                        skip = True

                elif p2innov < p1innov:
                    # p2 is earlier, choose it
                    chosengene = g.genes[p2_i]
                    p2_i += 1;
                    if p1better:
                        skip = True

                else:
                    # error
                    print "THIS SHOULD NEVER HAPPEN"
                    skip = True
                        
                #
                # neither genome has run out yet.
                #

            # check if chosen gene represents the same link as another already chosen gene
            new_i = 0
            while ((new_i < len(newgenes)) and
                   (not ((newgenes[new_i].lnk.in_node.node_id == chosengene.lnk.in_node.node_id) and
                         (newgenes[new_i].lnk.out_node.node_id  == chosengene.lnk.out_node.node_id) and
                         (newgenes[new_i].lnk.is_recurrent == chosengene.lnk.is_recurrent) )) and
                   (not ((newgenes[new_i].lnk.in_node.node_id == chosengene.lnk.out_node.node_id) and
                         (newgenes[new_i].lnk.out_node.node_id == chosengene.lnk.in_node.node_id) and
                         (not newgenes[new_i].lnk.is_recurrent) and
                         (not chosengene.lnk.is_recurrent) ))):
                new_i += 1
            if new_i < len(newgenes):
                skip = True # is a duplicate


            # gene needs to be added
            if not skip:

                # get the trait to use
                if chosengene.lnk.linktrait is None:
                    traitnum = self.traits[0].trait_id - 1
                else:
                    traitnum = chosengene.lnk.linktrait.trait_id - self.traits[0].trait_id

                # get the nodes
                inode = chosengene.lnk.in_node
                onode = chosengene.lnk.out_node

                if inode.node_id < onode.node_id:
                    # inode is first
                    curnode_i = 0
                    while ( (curnode_i < len(newnodes)) and
                            (newnodes[curnode_i].node_id != inode.node_id) ):
                        curnode_i += 1
                    if curnode_i >= len(newnodes):
                        # inode doesn't exist in newnodes, must create it
                        if inode.nodetrait is None:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = inode.nodetrait.trait_id - self.traits[0].trait_id

                        new_inode = NNode()
                        new_inode.SetFromNNodeAndTrait(inode, newtraits[nodetraitnum])
                        self.node_insert(newnodes, new_inode)
                    else:
                        # inode already exists in newnodes
                        new_inode = newnodes[curnode_i]

                    curnode_i = 0
                    while ( (curnode_i < len(newnodes)) and
                            (newnodes[curnode_i].node_id != onode.node_id) ):
                        curnode_i += 1
                    if curnode_i >= len(newnodes):
                        # onode doesn't exist in newnodes, must create it
                        if onode.nodetrait is None:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = onode.nodetrait.trait_id - self.traits[0].trait_id

                        new_onode = NNode()
                        new_onode.SetFromNNodeAndTrait(onode, newtraits[nodetraitnum])
                        self.node_insert(newnodes, new_onode)
                    else:
                        # onode already exists in newnodes
                        new_onode = newnodes[curnode_i]
                else:
                    # onode is first
                    curnode_i = 0
                    while ( (curnode_i < len(newnodes)) and
                            (newnodes[curnode_i].node_id != onode.node_id) ):
                        curnode_i += 1
                    if curnode_i >= len(newnodes):
                        # onode doesn't exist in newnodes, must create it
                        if onode.nodetrait is None:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = onode.nodetrait.trait_id - self.traits[0].trait_id

                        new_onode = NNode()
                        new_onode.SetFromNNodeAndTrait(onode, newtraits[nodetraitnum])
                        self.node_insert(newnodes, new_onode)
                    else:
                        # onode already exists in newnodes
                        new_onode = newnodes[curnode_i]

                    curnode_i = 0
                    while ( (curnode_i < len(newnodes)) and
                            (newnodes[curnode_i].node_id != inode.node_id) ):
                        curnode_i += 1
                    if curnode_i >= len(newnodes):
                        # inode doesn't exist in newnodes, must create it
                        if inode.nodetrait is None:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = inode.nodetrait.trait_id - self.traits[0].trait_id

                        new_inode = NNode()
                        new_inode.SetFromNNodeAndTrait(inode, newtraits[nodetraitnum])
                        self.node_insert(newnodes, new_inode)
                    else:
                        # inode already exists in newnodes
                        new_inode = newnodes[curnode_i]

                newgene = Gene()
                newgene.SetFromGeneAndValues(chosengene, newtraits[traitnum], new_inode, new_onode)
                if disable:
                    newgene.enable = False
                    disable = False
                newgenes.append(newgene)
                # not skipping
            #
            # loop over both parents genes
            #

        new_genome = Genome()
        new_genome.SetFromSpecs(genomeid, newtraits, newnodes, newgenes)
        return new_genome
        #
        # def mate_multipoint


    ##//This method mates like multipoint but instead of selecting one
    ##//   or the other when the innovation numbers match, it averages their
    ##//   weights 
    def mate_multipoint_avg(self, g, genomeid, fitness1, fitness2, interspec_flag):
        
        # Identify Best Genome
        if fitness1 > fitness2:
            p1better = True
        elif fitness1 == fitness2:
            if len(self.genes) < len(g.genes):
                p1better = True
            else:
                p1better = False
        else:
            p1better = False

        # Baby's traits
        newtraits = []
        for i in range(len(self.traits)):
            newtrait = Trait()
            newtrait.SetFromAverage(self.traits[i], g.traits[i])
            newtraits.append(newtrait)

            
        # Copy all sensors and outputs
        # Baby's nodes
        newnodes = []
        for curnode in g.nodes:
            if ((curnode.gen_node_label == NNode.INPUT) or
                (curnode.gen_node_label == NNode.BIAS) or
                (curnode.gen_node_label == NNode.OUTPUT)):
                if curnode.nodetrait is None:
                    nodetraitnum = 0
                else:
                    nodetraitnum = curnode.nodetrait.trait_id - self.traits[0].trait_id

                new_onode = NNode()
                new_onode.SetFromNNodeAndTrait(curnode, newtraits[nodetraitnum])
                self.node_insert(newnodes, new_onode)
                #
        
        # Baby's genes
        newgenes = []
        avgene = Gene()
        avgene.SetFromTraitAndValues(None, 0, None, None, False, 0, 0)

        # Walk through genes of both parents until both genomes reach an end
        p1_i = 0
        p2_i = 0
        while p1_i < len(self.genes) or p2_i < len(g.genes):

            avgene.enable = True

            # choose between next gene of each parent
            skip = False
            if p1_i == len(self.genes):
                chosengene = g.genes[p2_i]
                p2_i += 1
                if p1better:
                    skip = True
            elif p2_i == len(g.genes):
                chosengene = self.genes[p1_i]
                p1_i += 1
                if not p1better:
                    skip = True
            else:
                p1innov = self.genes[p1_i].innovation_num
                p2innov = g.genes[p2_i].innovation_num

                
                if p1innov == p2innov:
                    # same innovation number, average the weights
                    if neat.randfloat() > 0.5:
                        avgene.lnk.linktrait = self.genes[p1_i].lnk.linktrait
                    else:
                        avgene.lnk.linktrait = g.genes[p2_i].lnk.linktrait
                    avgene.lnk.weight = (self.genes[p1_i].lnk.weight + g.genes[p2_i].lnk.weight) / 2.0
                    

                    if neat.randfloat() > 0.5:
                        avgene.lnk.in_node = self.genes[p1_i].lnk.in_node
                    else:
                        avgene.lnk.in_node = g.genes[p2_i].lnk.in_node

                    if neat.randfloat() > 0.5:
                        avgene.lnk.out_node = self.genes[p1_i].lnk.out_node
                    else:
                        avgene.lnk.out_node = g.genes[p2_i].lnk.out_node

                    if neat.randfloat() > 0.5:
                        avgene.lnk.is_recurrent = self.genes[p1_i].lnk.is_recurrent
                    else:
                        avgene.lnk.is_recurrent = g.genes[p2_i].lnk.is_recurrent

                    avgene.innovation_num = self.genes[p1_i].innovation_num
                    avgene.mutation_num = (self.genes[p1_i].mutation_num + g.genes[p2_i].mutation_num) / 2.0
                    
                    # if either parent has gene disabled, the offspring likely has it disabled too
                    if (not self.genes[p1_i].enable) or (not g.genes[p2_i]):
                        if neat.randfloat() < 0.75:
                            avgene.enable = False

                    chosengene = avgene
                    p1_i += 1
                    p2_i += 1

                elif p1innov < p2innov:
                    # p1 is earlier, choose it
                    chosengene = self.genes[p1_i]
                    p1_i += 1
                    if not p1better:
                        skip = True

                elif p2innov < p1innov:
                    # p2 is earlier, choose it
                    chosengene = g.genes[p2_i]
                    p2_i += 1
                    if p1better:
                        skip = True

                else:
                    # error
                    print "THIS SHOULD NEVER HAPPEN"
                    skip = True
                        
                #
                # neither genome has run out yet.
                #

            # check if chosen gene represents the same link as another already chosen gene
            new_i = 0
            while ((new_i < len(newgenes)) and
                   (not ((newgenes[new_i].lnk.in_node.node_id == chosengene.lnk.in_node.node_id) and
                         (newgenes[new_i].lnk.out_node.node_id  == chosengene.lnk.out_node.node_id) and
                         (newgenes[new_i].lnk.is_recurrent == chosengene.lnk.is_recurrent) )) and
                   (not ((newgenes[new_i].lnk.in_node.node_id == chosengene.lnk.out_node.node_id) and
                         (newgenes[new_i].lnk.out_node.node_id == chosengene.lnk.in_node.node_id) and
                         (not newgenes[new_i].lnk.is_recurrent) and
                         (not chosengene.lnk.is_recurrent) ))):
                new_i += 1
            if new_i < len(newgenes):
                skip = True # is a duplicate


            # gene needs to be added
            if not skip:

                # get the trait to use
                if chosengene.lnk.linktrait is None:
                    traitnum = self.traits[0].trait_id - 1
                else:
                    traitnum = chosengene.lnk.linktrait.trait_id - self.traits[0].trait_id

                # get the nodes
                inode = chosengene.lnk.in_node
                onode = chosengene.lnk.out_node

                if inode.node_id < onode.node_id:
                    # inode is first
                    curnode_i = 0
                    while ( (curnode_i < len(newnodes)) and
                            (newnodes[curnode_i].node_id != inode.node_id) ):
                        curnode_i += 1
                    if curnode_i >= len(newnodes):
                        # inode doesn't exist in newnodes, must create it
                        if inode.nodetrait is None:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = inode.nodetrait.trait_id - self.traits[0].trait_id

                        new_inode = NNode()
                        new_inode.SetFromNNodeAndTrait(inode, newtraits[nodetraitnum])
                        self.node_insert(newnodes, new_inode)
                    else:
                        # inode already exists in newnodes
                        new_inode = newnodes[curnode_i]

                    curnode_i = 0
                    while ( (curnode_i < len(newnodes)) and
                            (newnodes[curnode_i].node_id != onode.node_id) ):
                        curnode_i += 1
                    if curnode_i >= len(newnodes):
                        # onode doesn't exist in newnodes, must create it
                        if onode.nodetrait is None:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = onode.nodetrait.trait_id - self.traits[0].trait_id

                        new_onode = NNode()
                        new_onode.SetFromNNodeAndTrait(onode, newtraits[nodetraitnum])
                        self.node_insert(newnodes, new_onode)
                    else:
                        # onode already exists in newnodes
                        new_onode = newnodes[curnode_i]
                else:
                    # onode is first
                    curnode_i = 0
                    while ( (curnode_i < len(newnodes)) and
                            (newnodes[curnode_i].node_id != onode.node_id) ):
                        curnode_i += 1
                    if curnode_i >= len(newnodes):
                        # onode doesn't exist in newnodes, must create it
                        if onode.nodetrait is None:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = onode.nodetrait.trait_id - self.traits[0].trait_id

                        new_onode = NNode()
                        new_onode.SetFromNNodeAndTrait(onode, newtraits[nodetraitnum])
                        self.node_insert(newnodes, new_onode)
                    else:
                        # onode already exists in newnodes
                        new_onode = newnodes[curnode_i]

                    curnode_i = 0
                    while ( (curnode_i < len(newnodes)) and
                            (newnodes[curnode_i].node_id != inode.node_id) ):
                        curnode_i += 1
                    if curnode_i >= len(newnodes):
                        # inode doesn't exist in newnodes, must create it
                        if inode.nodetrait is None:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = inode.nodetrait.trait_id - self.traits[0].trait_id

                        new_inode = NNode()
                        new_inode.SetFromNNodeAndTrait(inode, newtraits[nodetraitnum])
                        self.node_insert(newnodes, new_inode)
                    else:
                        # inode already exists in newnodes
                        new_inode = newnodes[curnode_i]

                newgene = Gene()
                newgene.SetFromGeneAndValues(chosengene, newtraits[traitnum], new_inode, new_onode)
                newgenes.append(newgene)
                # not skipping
            #
            # loop over both parents genes
            #

        new_genome = Genome()
        new_genome.SetFromSpecs(genomeid, newtraits, newnodes, newgenes)
        return new_genome
        #
        # def mate_multipoint_avg

    ##// This method is similar to a standard single point CROSSOVER
    ##//   operator.  Traits are averaged as in the previous 2 mating
    ##//   methods.  A point is chosen in the smaller Genome for crossing
    ##//   with the bigger one.  
    def mate_singlepoint(self, g, genomeid):
        
        # Baby's traits
        newtraits = []
        for i in range(len(self.traits)):
            newtrait = Trait()
            newtrait.SetFromAverage(self.traits[i], g.traits[i])
            newtraits.append(newtrait)

        # Baby's nodes
        newnodes = []
        
        # Baby's genes
        newgenes = []
        avgene = Gene()
        avgene.SetFromTraitAndValues(None, 0, None, None, False, 0, 0)

        # Choose crossover point
        if len(self.genes) < len(g.genes):
            p1genes = self.genes
            p2genes = g.genes
        else:
            p1genes = g.genes
            p2genes = self.genes

        crosspoint = neat.randint(0, len(p1genes)-1)
        p1_i = 0
        p2_i = 0
        stopper_i = len(p2genes)
        p1_stop_i = len(p1genes)
        p2_stop_i = len(p2genes)
        genecounter = 0

        skip = False

        # Walk through genes of both parents until both genomes reach an end
        while p2_i < stopper_i:
            
            avgene.enable = True

            # choose between next gene of each parent
            skip = False
            if p1_i >= p1_stop_i:
                chosengene = p2genes[p2_i]
                p2_i += 1
            elif p2_i >= p2_stop_i:
                chosengene = p1genes[p1_i]
                p1_i += 1
            else:
                p1innov = p1genes[p1_i].innovation_num
                p2innov = p2genes[p2_i].innovation_num

                
                if p1innov == p2innov:
                    # same innovation number, choose gene based on crossover
                    if genecounter < crosspoint:
                        chosengene = p1genes[p1_i]
                    elif genecount > crosspoint:
                        chosengene = p2genes[p2_i]
                    else:
                        # at crossover, average the two genes
                    
                        if neat.randfloat() > 0.5:
                            avgene.lnk.linktrait = p1genes[p1_i].lnk.linktrait
                        else:
                            avgene.lnk.linktrait = p2genes[p2_i].lnk.linktrait
                        avgene.lnk.weight = (p1genes[p1_i].lnk.weight + p2genes[p2_i].lnk.weight) / 2.0
                    
                        if neat.randfloat() > 0.5:
                            avgene.lnk.in_node = p1genes[p1_i].lnk.in_node
                        else:
                            avgene.lnk.in_node = p2genes[p2_i].lnk.in_node
                        if neat.randfloat() > 0.5:
                            avgene.lnk.out_node = p1genes[p1_i].lnk.out_node
                        else:
                            avgene.lnk.out_node = p2genes[p2_i].lnk.out_node

                        if neat.randfloat() > 0.5:
                            avgene.lnk.is_recurrent = p1genes[p1_i].lnk.is_recurrent
                        else:
                            avgene.lnk.is_recurrent = p2genes[p2_i].lnk.is_recurrent

                        avgene.innovation_num = p1genes[p1_i].innovation_num
                        avgene.mutation_num = (p1genes[p1_i].mutation_num + p2genes[p2_i].mutation_num) / 2.0
                        
                        # if either parent has gene disabled, the offspring has it disabled too
                        if (not p1genes[p1_i].enable) or (not p2genes[p2_i]):
                            avgene.enable = False
                        chosengene = avgene
                        
                        # at crossover
                    p1_i += 1
                    p2_i += 1
                    genecount += 1
                    # p1innov == p2innov

                elif p1innov < p2innov:
                    if genecounter < crosspoint:
                        chosengene = p1genes[p1_i]
                        p1_i += 1
                        genecounter += 1
                    else:
                        chosengene = p2genes[p2_i]
                        p2_i += 1
                        
                elif p2innov < p1innov:
                    # p2 is earlier, choose it
                    chosengene = p2genes[p2_i]
                    p2_i += 1
                    skip = True
                    # gene is before crosspoint on wrong genome
                    
                else:
                    # error
                    print "THIS SHOULD NEVER HAPPEN"
                    skip = True
                        
                #
                # neither genome has run out yet.
                #

            # check if chosen gene represents the same link as another already chosen gene
            new_i = 0
            while ((new_i < len(newgenes)) and
                   (not ((newgenes[new_i].lnk.in_node.node_id == chosengene.lnk.in_node.node_id) and
                         (newgenes[new_i].lnk.out_node.node_id  == chosengene.lnk.out_node.node_id) and
                         (newgenes[new_i].lnk.is_recurrent == chosengene.lnk.is_recurrent) )) and
                   (not ((newgenes[new_i].lnk.in_node.node_id == chosengene.lnk.out_node.node_id) and
                         (newgenes[new_i].lnk.out_node.node_id == chosengene.lnk.in_node.node_id) and
                         (not newgenes[new_i].lnk.is_recurrent) and
                         (not chosengene.lnk.is_recurrent) ))):
                new_i += 1
            if new_i < len(newgenes):
                skip = True # is a duplicate


            # gene needs to be added
            if not skip:

                # get the trait to use
                if chosengene.lnk.linktrait is None:
                    traitnum = self.traits[0].trait_id - 1
                else:
                    traitnum = chosengene.lnk.linktrait.trait_id - self.traits[0].trait_id

                # get the nodes
                inode = chosengene.lnk.in_node
                onode = chosengene.lnk.out_node

                if inode.node_id < onode.node_id:
                    # inode is first
                    curnode_i = 0
                    while ( (curnode_i < len(newnodes)) and
                            (newnodes[curnode_i].node_id != inode.node_id) ):
                        curnode_i += 1
                    if curnode_i >= len(newnodes):
                        # inode doesn't exist in newnodes, must create it
                        if inode.nodetrait is None:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = inode.nodetrait.trait_id - self.traits[0].trait_id

                        new_inode = NNode()
                        new_inode.SetFromNNodeAndTrait(inode, newtraits[nodetraitnum])
                        self.node_insert(newnodes, new_inode)
                    else:
                        # inode already exists in newnodes
                        new_inode = newnodes[curnode_i]

                    curnode_i = 0
                    while ( (curnode_i < len(newnodes)) and
                            (newnodes[curnode_i].node_id != onode.node_id) ):
                        curnode_i += 1
                    if curnode_i >= len(newnodes):
                        # onode doesn't exist in newnodes, must create it
                        if onode.nodetrait is None:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = onode.nodetrait.trait_id - self.traits[0].trait_id

                        new_onode = NNode()
                        new_onode.SetFromNNodeAndTrait(onode, newtraits[nodetraitnum])
                        self.node_insert(newnodes, new_onode)
                    else:
                        # onode already exists in newnodes
                        new_onode = newnodes[curnode_i]
                else:
                    # onode is first
                    curnode_i = 0
                    while ( (curnode_i < len(newnodes)) and
                            (newnodes[curnode_i].node_id != onode.node_id) ):
                        curnode_i += 1
                    if curnode_i >= len(newnodes):
                        # onode doesn't exist in newnodes, must create it
                        if onode.nodetrait is None:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = onode.nodetrait.trait_id - self.traits[0].trait_id

                        new_onode = NNode()
                        new_onode.SetFromNNodeAndTrait(onode, newtraits[nodetraitnum])
                        self.node_insert(newnodes, new_onode)
                    else:
                        # onode already exists in newnodes
                        new_onode = newnodes[curnode_i]

                    curnode_i = 0
                    while ( (curnode_i < len(newnodes)) and
                            (newnodes[curnode_i].node_id != inode.node_id) ):
                        curnode_i += 1
                    if curnode_i >= len(newnodes):
                        # inode doesn't exist in newnodes, must create it
                        if inode.nodetrait is None:
                            nodetraitnum = 0
                        else:
                            nodetraitnum = inode.nodetrait.trait_id - self.traits[0].trait_id

                        new_inode = NNode()
                        new_inode.SetFromNNodeAndTrait(inode, newtraits[nodetraitnum])
                        self.node_insert(newnodes, new_inode)
                    else:
                        # inode already exists in newnodes
                        new_inode = newnodes[curnode_i]

                newgene = Gene()
                newgene.SetFromGeneAndValues(chosengene, newtraits[traitnum], new_inode, new_onode)
                newgenes.append(newgene)
                # not skipping
                
            skip = False
            #
            # loop over both parents genes
            #

        new_genome = Genome()
        new_genome.SetFromSpecs(genomeid, newtraits, newnodes, newgenes)
        return new_genome
        #
        # def mate_singlepoint

    ##// ******** COMPATIBILITY CHECKING METHODS ********

    ##// This function gives a measure of compatibility between
    ##//   two Genomes by computing a linear combination of 3
    ##//   characterizing variables of their compatibilty.
    ##//   The 3 variables represent PERCENT DISJOINT GENES, 
    ##//   PERCENT EXCESS GENES, MUTATIONAL DIFFERENCE WITHIN
    ##//   MATCHING GENES.  So the formula for compatibility 
    ##//   is:  disjoint_coeff*pdg+excess_coeff*peg+mutdiff_coeff*mdmg.
    ##//   The 3 coefficients are global system parameters 
    def compatibility(self, g):
        num_disjoint = 0.0
	num_excess = 0.0
        mut_diff_total = 0.0
        num_matching = 0.0

        max_genome_size = max(len(self.genes), len(g.genes))
        p1genes = self.genes
        p2genes = g.genes
        p1_i = 0
        p2_i = 0
        while p1_i < len(p1genes) or p2_i < len(p2genes):
            if p1_i >= len(p1genes):
                p2_i += 1
                num_excess += 1.0
            elif p2_i >= len(p2genes):
                p1_i += 1
                num_excess += 1.0
            else:
                p1innov = p1genes[p1_i].innovation_num
                p2innov = p2genes[p2_i].innovation_num

                if p1innov == p2innov:
                    num_matching += 1.0
                    mut_diff_total += abs(p1genes[p1_i].mutation_num - p2genes[p2_i].mutation_num)
                    p1_i += 1
                    p2_i += 1
                elif p1innov < p2innov:
                    p1_i += 1
                    num_disjoint += 1.0
                elif p2innov < p1innov:
                    p2_i += 1
                    num_disjoint += 1.0
                else:
                    print "THIS SHOULD NEVER HAPPEN"
                    
            # while genes left to look at

        return (neat.disjoint_coeff * num_disjoint +
                neat.excess_coeff * num_excess +
                neat.mutdiff_coeff * mut_diff_total/num_matching)
    
    def trait_compare(self, t1, t2):
        id1 = t1.trait_id
        id2 = t2.trait_id
        params_diff = 0.0

        if id1 == 1 and id2 >= 2:
            return 0.5
        elif id2 == 1 and id1 >= 2:
            return 0.5
        else:
            if id1 >= 2:
                for count in range(3):
                    params_diff += abs(t1.params[count] - t2.params[count])
                return params_diff / 4.0
            else:
                return 0.0
                
    ##// Return number of non-disabled genes 
    def extrons(self):
        total = 0
        for curgene in self.genes:
            if curgene.enable:
                total += 1
        return total
    
    ##// Randomize the trait pointers of all the node and connection genes 
    def randomize_traits(self):
        numtraits = len(self.traits)
        for curnode in self.nodes:
            traitnum = neat.randint(1, numtraits)
            curnode.trait_id = traitnum

            for curtrait in self.traits:
                if curtrait.trait_id == traitnum:
                    break
            curnode.nodetrait = curtrait
            
        for curgene in self.genes:
            traitnum = neat.randint(1, numtraits)
            curgene.lnk.trait_id = traitnum
            
            for curtrait in self.traits:
                if curtrait.trait_id == traitnum:
                    break
            curgene.lnk.linktrait = curtrait

        return
        
    ##//Inserts a NNode into a given ordered list of NNodes in order
    def node_insert(self, nlist, n):
        nid = n.node_id
        for i in range(len(nlist)):
            curnode = nlist[i]
            if curnode.node_id == nid:
                # duplicate node_id, don't add it
                dprint(DEBUG_ERROR, "Should not find duplicate any more.", n)
                dcallstack(DEBUG_ERROR)
                dprint(DEBUG_ERROR, self.deep_string())
                return
            if curnode.node_id > nid:
                # found its place
                nlist.insert(i, n)
                return
        # goes at the end
        nlist.append(n)
        return

    ##//Adds a new gene that has been created through a mutation in the
    ##//*correct order* into the list of genes in the genome
    def add_gene(self, glist, g):
        inum = g.innovation_num
        for i in range(len(glist)):
            curgene = glist[i]
            if curgene.innovation_num == inum:
                # duplicate innovation_num, don't add it
                dprint(DEBUG_ERROR, "Should not find duplicate any more.", g)
                return
            if curgene.innovation_num > inum:
                # found its place
                glist.insert(i, g)
                return
        # goes at the end
        glist.append(g)
        return

    def get_last_node_id(self):
        return self.nodes[-1].node_id + 1

    def get_last_gene_innovnum(self):
        return self.genes[-1].innovation_num + 1

    
##//Calls special constructor that creates a Genome of 3 possible types:
##//0 - Fully linked, no hidden nodes
##//1 - Fully linked, one hidden node splitting each link
##//2 - Fully connected with a hidden layer 
##//num_hidden is only used in type 2
##//Saves to file "auto_genome"
def new_Genome_auto(num_in, num_out, num_hidden, typ, filename):
    g = Genome()
    g.SetFromCounts2(num_in, num_out, num_hidden, typ)
    print_Genome_tofile(g, filename)
    return g

def print_Genome_tofile(g, filename):
    ofile = open(filename, "w")
    g.print_to_file(ofile)
    ofile.close()
    return

def main():
    print "Need Genome exercise code here."
    return
    
if __name__ == "__main__":
    main()

