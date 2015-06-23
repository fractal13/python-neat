from link import Link

class Gene:
    
    def __init__(self):
        self.lnk = None # Link object
        self.innovation_num = 0.0 # float
        self.mutation_num = 0.0 # float, how much mutation has changed link
        self.enable = False # bool, is Gene enabled?
        self.frozen = False # bool, True == linkweight cannot be mutated
        return


    def SetFromValues(self, w, inode, onode, recur, innov, mnum):
        self.lnk = Link()
        self.lnk.SetFromWeight(w, inode, onode, recur)
        self.innovation_num = innov
        self.mutation_num = mnum
        self.enable = True
        self.frozen = False
        return

    def SetFromTraitAndValues(self, trait, weight, inode, onode, recur, innov, mnum):
        self.lnk = Link()
        self.lnk.SetFromTrait(trait, weight, inode, onode, recur)
        self.innovation_num = innov
        self.mutation_num = mnum
        self.enable = True
        self.frozen = False
        return

    def SetFromGeneAndValues(self, gene, trait, inode, onode):
        self.lnk = Link()
        self.lnk.SetFromTrait(trait, gene.lnk.weight, inode, onode, gene.lnk.is_recurrent)
        self.innovation_num = gene.innovation_num
        self.mutation_num = gene.mutation_num
        self.enable = gene.enable
        self.frozen = gene.frozen
        return

    def SetFromString(self, argline, traits, nodes):
        parts = argline.split()
        traitnum = int(parts[0])
        inodenum = int(parts[1])
        onodenum = int(parts[2])
        weight = float(parts[3])
        recur = bool(parts[4])
        self.innovation_num = float(parts[5])
        self.mutation_num = float(parts[6])
        self.enable = bool(parts[7])

        # find relevant trait
        if traitnum == 0:
            tr = None
        else:
            tr = None
            for curtrait in traits:
                if curtrait.trait_id == traitnum:
                    tr = curtrait
                    break
        
        inode = None
        onode = None
        for curnode in nodes:
            if curnode.node_id == inodenum:
                inode = curnode
            if curnode.node_id == onodenum:
                onode = curnode
            if inode and onode:
                break

        self.lnk = Link()
        self.lnk.SetFromTrait(trait, weight, inode, onode, recur)
        return

    def SetFromGene(self, gene):
        self.innovation_num = gene.innovation_num
        self.mutation_num = gene.muntation_num
        self.enable = gene.enable
        self.frozen = gene.frozen
        self.lnk = Link()
        self.lnk.SetFromOther(gene.lnk)
        return

    def print_to_file(self, fout):
        s = "gene "
        if self.lnk.linktrait is None:
            s += "0 "
        else:
            s += str(self.lnk.linktrait.trait_id) + " "
        s += str(self.lnk.in_node.node_id) + " "
        s += str(self.lnk.out_node.node_id) + " "
        s += str(self.lnk.weight) + " "
        s += str(self.lnk.is_recurrent) + " "
        s += str(self.innovation_num) + " "
        s += str(self.mutation_num) + " "
        s += str(self.enable) + "\n"
        fout.write(s)
        return

        
def main():
    print "Need Gene exercise code here."
    return
    
if __name__ == "__main__":
    main()
