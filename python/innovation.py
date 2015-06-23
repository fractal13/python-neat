class Innovation:

    NEWNODE = 0
    NEWLINK = 1

    def __init__(self, nin, nout, num1):
        self.innovation_type = Innovation.NEWNODE
        self.node_in_id = nin
        self.node_out_id = nout
        self.innovation_num1 = num1
        self.innovation_num2 = 0.
        self.new_weight = 0.
        self.new_traitnum = 0
        self.newnode_id = 0
        self.old_innov_num = 0
        self.recur_flag = False
        return

    def SetNewNode(self, num2, newid, oldinnov):
        self.innovation_type = Innovation.NEWNODE
        self.innovation_num2 = num2
        self.newnode_id = newid
        self.old_innov_num = oldinnov
        return

    def SetNewLink(self, w, t):
        self.innovation_type = Innovation.NEWLINK
        self.new_weight = w
        self.new_traitnum = t
        return

    def SetRecurLink(self, w, t, recur):
        self.innovation_type = Innovation.NEWLINK
        self.new_weight = w
        self.new_traitnum = t
        self.recur_flag = recur
        return

class NewNodeInnovation(Innovation):
    def __init__(self, nin, nout, num1, num2, newid, oldinnov):
        Innovation.__init__(self, nin, nout, num1)
        self.SetNewNode(num2, newid, oldinnov)
        return

class NewLinkInnovation(Innovation):
    def __init__(self, nin, nout, num1, num2, w, t):
        Innovation.__init__(self, nin, nout, num1)
        self.SetNewLink(w, t)
        return
        
class RecurLinkInnovation(Innovation):
    def __init__(self, nin, nout, num1, num2, w, t, recur):
        Innovation.__init__(self, nin, nout, num1)
        self.SetRecurLink(w, t, recur)
        return

def main():
    nni = NewNodeInnovation(1, 2, 3.3, 4.4, 5, 6)
    print nni
    nli = NewLinkInnovation(11, 12, 13.13, 14.14, 0.15, 16)
    print nli
    nli = RecurLinkInnovation(11, 12, 13.13, 14.14, 0.15, 16, True)
    print nli
    return
        
if __name__ == "__main__":
    main()

    
