
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
        
        # duplicaate Genes
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
        wordcount = len(words)
        curwordnum = 0
        while not done:
            if curwordnum > wordcount or wordcount == 0:
                words = fin.readline().strip().split()
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
                argline = " ".join(words[wordcount+1:])
                curwordnum = wordcount + 1
                newtrait = Trait()
                newtrait.SetFromString(argline)
                self.traits.append(newtrait)

            elif curword == "node":
                argline = " ".join(words[wordcount+1:])
                curwordnum = wordcount + 1
                newnode = NNode()
                newnode.SetFromStringAndTraits(argline, self.traits)
                self.nodes.append(newnode)

            elif curword == "gene":
                argline = " ".join(words[wordcount+1:])
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
            newnode.SetFromNodeTypeAndId(curnode.type, curnode.node_id)

            # Trait parameters
            curtrait = curnode.nodetrait
            newnode.derive_trait(curtrait)

            # Placement
            if curnode.gen_node_label == NNode.INPUT:
                inlist.append(curnode)
            elif curnode.gen_node_label == NNode.BIAS:
                inlist.append(curnode)
            elif curnode.gen_node_label == NNode.OUTPUT:
                outlist.append(curnode)
            all_list.append(curnode)

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
                        
            newnode = Node()
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
            trait = curgene.lnk.linktrait
            if trait is None:
                assoc_trait = None
            else:
                assoc_trait = None
                for curtrait in traits_dup:
                    if curtrait.trait_id == curnode.nodetrait.trait_id:
                        assoc_trait = curtrait
                        break
            
            newgene = Gene()
            newgene.SetFromGeneAndValues(curgene, assoc_trait, inode, onode)
            genes_dup.append(newgene)
            
        # Genome
        newgenome = Genome()
        newgenome.SetFromSpecs(new_id, traits_dup, nodes_dup, genes_dup)

        return newgenome

    ##// For debugging: A number of tests can be run on a genome to check its
    ##// integrity
    ##// Note: Some of these tests do not indicate a bug, but rather are meant
    ##// to be used to detect specific system states
    def verify(self):

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
            if not Found:
                return False
                
            found = False
            for curnode in self.nodes:
                if curnode == onode:
                    found = True
                    break
            if not Found:
                return False

        # Check nodes are in order
        last_id = 0
        for curnode in self.nodes:
            if curnode.node_id < last_id:
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
            return False
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
                # new innovation
                trait = thelink.linktrait
                newnode = NNode()
                newnode.SetFromNodeTypeIdAndPlacement(NNode.NEURON, curnode_id[0], NNode.HIDDEN)
                curnode_id[0] += 1
                newnode.nodetrait = self.traits[0]

                newgene1 = Gene()
                newgene2 = Gene()
                newgene1.SetFromTraitAndValues(trait, 1.0, in_node, newnode, thelink.is_recurrent, curinnov[0], 0.0)
                newgene2.SetFromTraitAndValues(trait, oldweight, newnode, out_node, False, curinnov[0]+1.0, 0.0)
                curinnov[0] += 2.0

                innov = Innovation(in_node.node_id, out_node.node_id, curinnov[0]-2.0)
                innov.SetNewNode(curinnov[0]-1.0, newnode.node_id, thegene.innovation_num)
                innovs.append(innov)
                done = True

            elif ((theinnov.innovation_type == Innovation.NEWNODE) and
                  (theinnov.node_in_id == in_node.node_id) and
                  (theinnov.node_out_id == out_node.node_id) and
                  (theinnov.old_innov_num == thegene.innovation_num)):
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
        self.add_gene(self.genes, newgenes1)
        self.add_gene(self.genes, newgenes2)
        self.node_insert(self.nodes, newnode)

        return True

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
                    recurflag = self.phenotype.is_recur(nodep1.analogue, nodep2.analogue, count, thresh)
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
                    recurflag = self.phenotype.is_recur(nodep1.analogue, nodep2.analogue, count, thresh)
                
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
                        return False

                    traitnum = neat.randint(0, len(self.traits)-1)
                    thetrait = self.traits[traitnum]

                    newweight = neat.randposneg() * neat.randfloat() * 1.0
                    
                    newgene = Gene()
                    newgene.SetFromValues(thetrait, newweight, nodep1, nodep2, recurflag, curinnov[0], newweight)

                    innov = Innovation(nodep1.node_id, nodep2.node_id, curinnov[0])
                    innov.SetNewLink(newweight, traitnum)
                    innovs.append(innov)

                    curinnov[0] += 1.0

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
            return True
            
        else:
            # not found
            return False
        #

    def mutate_add_sensor(self, innovs, curinnov):
        ???
        return
        
    ##// ****** MATING METHODS ***** 

    ##// This method mates this Genome with another Genome g.  
    ##//   For every point in each Genome, where each Genome shares
    ##//   the innovation number, the Gene is chosen randomly from 
    ##//   either parent.  If one parent has an innovation absent in 
    ##//   the other, the baby will inherit the innovation 
    ##//   Interspecies mating leads to all genes being inherited.
    ##//   Otherwise, excess genes come from most fit parent.
    def mate_multipoint(self, g, genomeid, fitness1, fitness2, interspec_flag):
        ???
        return

    ##//This method mates like multipoint but instead of selecting one
    ##//   or the other when the innovation numbers match, it averages their
    ##//   weights 
    def mate_multipoint_avg(self, g, genomeid, fitness1, fitness2, interspec_flag):
        ???
        return

    ##// This method is similar to a standard single point CROSSOVER
    ##//   operator.  Traits are averaged as in the previous 2 mating
    ##//   methods.  A point is chosen in the smaller Genome for crossing
    ##//   with the bigger one.  
    def mate_singlepoint(self, g, genomeid):
        ???
        return

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
        ???
        return
    
    def trait_compare(self, t1, t2):
        ???
        return
                
    ##// Return number of non-disabled genes 
    def extrons(self):
        ???
        return
    
    ##// Randomize the trait pointers of all the node and connection genes 
    def randomize_traits(self):
        ???
        return
        
    ##//Inserts a NNode into a given ordered list of NNodes in order
    def node_insert(self, nlist, n):
        ???
        return

    ##//Adds a new gene that has been created through a mutation in the
    ##//*correct order* into the list of genes in the genome
    def add_gene(self, glist, g):
        ???
        return

    def get_last_node_id(self):
        return self.nodes[-1].node_id + 1

    def get_last_gene_innovnum(self):
        return self.genes[-1].innovation_num + 1

    def print_genome(self):
        ???
        return

    
##//Calls special constructor that creates a Genome of 3 possible types:
##//0 - Fully linked, no hidden nodes
##//1 - Fully linked, one hidden node splitting each link
##//2 - Fully connected with a hidden layer 
##//num_hidden is only used in type 2
##//Saves to file "auto_genome"
def new_Genome_auto(num_in, num_out, num_hidden, typ, filename):
    ???
    return

def print_Genome_tofile(g, filename):
    ???
    return

def main():
    print "Need Genome exercise code here."
    return
    
if __name__ == "__main__":
    main()

