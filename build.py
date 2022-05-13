import sys


class Step:
    char: str
    to_node: int
    to_accept: bool = False

    def __init__(self, char, to_node):
        self.char = char
        self.to_node = to_node

    def __hash__(self):
        return hash((self.char, self.to_node, self.to_accept))

    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.char == other.char and self.to_node == other.to_node and self.to_accept == other.to_accept

class Node:
    ind: int
    accept = False
    steps = set()
    char: str
    isRecursive = False
    isRecursive2 = False
    isSubStarter = False
    isSubRecursive = False
    accept = False
    nfa = None
    emptyNfa = False
    recursed = False
    recursedForisRecursive = False
    finisher = -1

    def __init__(self, ind, accept, steps):
        self.ind = ind
        self.accept = accept
        self.steps = steps
        self.steps = set()

    def __init__(self, ind, accept, char):
        self.ind = ind
        self.accept = accept
        self.char = char
        self.steps = set()


    def addStep(self, char, to_node):
        self.steps.add(Step(char=char, to_node=to_node))

    def addRecursion(self):
        self.isRecursive = True
        self.steps.add(Step(char=self.char, to_node=self.ind))

class Nfa:
    curInd: int = 0
    regex: str = ""
    openedCures: int = 0
    nodeList = []
    activeBranches = set()
    newBranches = set()
    newNfa = set()
    lastOperation: str = ""
    acceptStates = set()
    starterInd = 0
    finisherSize = 0

    def __init__(self, curInd, regex, openedCures, nodeList):
        self.curInd = curInd
        self.regex = regex
        self.openedCures = openedCures
        self.nodeList = nodeList
        self.activeBranches = set()
        self.newBranches = set()
        self.newNfas = set()
        self.acceptStates = set()

    def convert(self):
        for i in range(self.curInd, len(self.regex)):
            curChar = self.regex[i]
            if i >= self.curInd:
                self.curInd = i

                if curChar == "." or curChar == "|":
                    self.lastOperation = curChar
                elif curChar == "*":
                    nextChar = ""
                    if i + 1 != len(self.regex):
                        nextChar = self.regex[i + 1]

                elif curChar == ")":
                    self.openedCures -= 1
                    self.joinBranches()
                    if len(self.activeBranches) == 0:
                        self.nodeList[self.starterInd].emptyNfa = True
                        self.activeBranches.add(self.starterInd)
                    self.setAccepters()
                    nextChar = ""
                    if i + 1 != len(self.regex):
                        nextChar = self.regex[i + 1]
                    self.curInd += 1
                    self.finisherSize = len(self.nodeList)
                    self.nodeList[self.starterInd].nfa = self
                    if nextChar == "*":
                        self.nodeList[self.starterInd].isSubRecursive = True
                        self.nodeList[self.starterInd].finisher = self.finisherSize-1
                        self.addSubRecursionNfa()
                        self.nodeList[self.finisherSize-1].isRecursive2 = True
                    return
                elif curChar == "(":
                    self.openedCures += 1
                    nd = Node(ind=len(self.nodeList), accept=False, char="")
                    nd.isSubStarter = True
                    self.nodeList.append(nd)
                    newNfa = Nfa(curInd=i + 1, regex=self.regex, openedCures=1, nodeList=self.nodeList)
                    newNfa.activeBranches.add(nd.ind)
                    newNfa.starterInd = nd.ind
                    newNfa.convert()
                    self.curInd = newNfa.curInd
                    self.addNewNfa(self.lastOperation, newNfa)

                else:
                    nextChar = ""
                    if i+1 != len(self.regex):
                        nextChar = self.regex[i+1]
                    newNode = Node(ind=len(self.nodeList), accept=False, char=curChar)
                    if nextChar == "*":
                        newNode.addRecursion()
                    self.nodeList.append(newNode)
                    self.addNewNode(self.lastOperation, newNode)

        self.joinBranches()
        self.setAccepters()

    def addNewNode(self, lastOperation, newNode):
        if lastOperation == "." or lastOperation == "(" or lastOperation == ")":
            self.joinBranches()
            self.newBranches.add(newNode.ind)
        elif lastOperation == "":
            self.newBranches.add(newNode.ind)
        elif lastOperation == "|":
            self.newBranches.add(newNode.ind)

    def addNewNfa(self, lastOperation, newNode):
        if lastOperation == "." or lastOperation == "(" or lastOperation == ")":
            self.joinBranches()
            self.newNfas.add(newNode)
        elif lastOperation == "":
            self.newNfas.add(newNode)
        elif lastOperation == "|":
            self.newNfas.add(newNode)

    def joinBranches(self):
        for ind in self.activeBranches:
            for i in self.newBranches:
                self.nodeList[ind].addStep(self.nodeList[i].char, self.nodeList[i].ind)
            for i in self.newNfas:
                self.nodeList[ind].addStep("",i.starterInd)

        self.activeBranches.clear()
        self.activeBranches.update(self.newBranches)
        self.newBranches.clear()

        for nf in self.newNfas:
            for k in nf.acceptStates:
                self.activeBranches.add(k)
        self.newNfas.clear()

    def setAccepters(self):
        for st in self.activeBranches:
            self.acceptStates.add(st)



    def addSubRecursionNfa(self):

        for st in self.acceptStates:
            for ste in self.nodeList[self.starterInd].steps:
                self.nodeList[st].addStep(self.nodeList[ste.to_node].char,ste.to_node)

    def getAllChildSteps(self, ind):
        nd: Node = self.nodeList[ind]
        steps = set()
        changed = False
        for st in nd.steps:
            if self.nodeList[st.to_node].isRecursive and nd.ind != st.to_node:
                childs, ch = self.getAllChildSteps(st.to_node)
                if not childs.issubset(steps):
                    changed = True
                    steps.update(childs)
            elif self.nodeList[st.to_node].isSubStarter and nd.ind != st.to_node:
                if self.nodeList[st.to_node].isSubRecursive:
                    self.updateSubRecursion(st.to_node,nd.ind)
                    childs, ch = self.getAllChildSteps(self.nodeList[st.to_node].finisher)
                    changed = True
                    steps.update(childs)
                childs, ch = self.getAllChildSteps(st.to_node)
                if not childs.issubset(steps):
                    changed = True
                    steps.update(childs)
            else:
                if not steps.__contains__(st):
                    changed = True
                    steps.add(st)

        return steps, changed



    def printNfaFull(self):
        acc = ""
        nd: Node
        pr = ""
        stepCounter  = 0
      #  self.putInSteps()
        for nd in self.nodeList:
            steps = set()

            for st in nd.steps:
                if self.nodeList[st.to_node].isRecursive:
                    childs,ch = self.getAllChildSteps(st.to_node)
                    steps.update(childs)
                elif self.nodeList[st.to_node].isSubStarter:
                    if self.nodeList[st.to_node].isSubRecursive or self.nodeList[st.to_node].emptyNfa:
                        self.updateSubRecursion(st.to_node,nd.ind)
                        childs, ch = self.getAllChildSteps(self.nodeList[st.to_node].finisher)
                        steps.update(childs)
                    childs,ch = self.getAllChildSteps(st.to_node)
                    steps.update(childs)
                else:
                    steps.add(st)

            #pr += len(steps).__str__()
            pr += nd.ind.__str__()
            stepCounter += len(steps)
            for st in steps:
                pr = pr + " " + st.char.__str__() + " " + st.to_node.__str__()
            pr += "\n"
        self.antiRecursion()
        self.antiRecursionForRecusive()

        for ind in self.acceptStates:
            acc = acc + ind.__str__() + " "
        header = ""
        header += len(self.nodeList).__str__() +" " + len(self.acceptStates).__str__() + " " + stepCounter.__str__()
        sys.stdout.write((header) +"\n")
        sys.stdout.write((acc) +"\n")
        sys.stdout.write((pr))

    def antiRecursionForRecusive(self):
        for nd in self.nodeList:
            for st in nd.steps:
                if self.nodeList[st.to_node].isRecursive and self.acceptStates.__contains__(st.to_node) and (not self.nodeList[st.to_node].recursedForisRecursive):
                    self.acceptStates.add(nd.ind)
                    self.nodeList[st.to_node].recursedForisRecursive = True
                    self.antiRecursionForRecusive()







    def antiRecursion(self):
        nd: Node
        for nd in self.nodeList:
            for st in nd.steps:
                if  (not self.nodeList[nd.ind].recursed)  and self.nodeList[st.to_node].isSubStarter and self.nodeList[st.to_node].emptyNfa and self.acceptStates.__contains__(st.to_node):
                    self.acceptStates.add(nd.ind)
                    self.nodeList[nd.ind].recursed = True
                    self.antiRecursion()
                if (not self.nodeList[nd.ind].recursed) and self.nodeList[st.to_node].isSubStarter and self.acceptStates.__contains__(st.to_node):
                    self.acceptStates.add(nd.ind)
                    self.nodeList[nd.ind].recursed = True
                    self.antiRecursion()





    def updateSubRecursion(self,index,starterInd):
        if self.nodeList[index].nfa.finisherSize == len(self.nodeList):
            self.acceptStates.add(starterInd)
        else:
            for accepters in self.nodeList[index].nfa.acceptStates:
                self.nodeList[index].steps.update(self.nodeList[accepters].steps)



def addPlus(regex):
    ret = ""
    for i, v in enumerate(regex):
        if regex[i] == "|" or regex[i] == "(":
            ret += v
        elif regex[i] == ")":
            if i + 1 != len(regex):
                if regex[i + 1] == "*" or regex[i+1] == "|":
                    ret += v
                else:
                    ret = ret + v + "."
            else:
                ret += v
        elif regex[i] == "*":
            if i + 1 != len(regex):
                if regex[i + 1] == "|":
                    ret += v
                else:
                    ret = ret + v + "."
            else:
                ret += v
        elif i + 1 != len(regex):
            if regex[i + 1] == "|" or regex[i + 1] == ")" or regex[i + 1] == "*":
                ret += v
            else:
                ret = ret + v + "."
        else:
            ret += v

    return ret


def main():
    regex = sys.stdin.readline().strip()
    regex = addPlus(regex)
    nodeList = []
    nodeList.append(Node(ind=0, accept=False, char=""))
    nfa = Nfa(curInd=0, regex=regex, openedCures=0, nodeList=nodeList)
    nfa.isSubStarter = True
    nfa.activeBranches.add(0)
    nfa.convert()
    nfa.printNfaFull()


if __name__ == "__main__":
    main()
