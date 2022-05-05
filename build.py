class Step:
    char: str
    to_node: int
    to_accept: bool = False

    def __init__(self, char, to_node):
        self.char = char
        self.to_node = to_node


class Node:
    ind: int
    accept = False
    steps = []
    char: str
    isRecursive = False

    def __init__(self, ind, accept, steps):
        self.ind = ind
        self.accept = accept
        self.steps = steps
        self.steps = []

    def __init__(self, ind, accept, char):
        self.ind = ind
        self.accept = accept
        self.char = char
        self.steps = []


    def addStep(self, char, to_node):
        self.steps.append(Step(char=char, to_node=to_node))

    def addRecursion(self):
        self.isRecursive = True
        self.steps.append(Step(char=self.char, to_node=self.ind))

class Nfa:
    curInd: int = 0
    regex: str = ""
    openedCures: int = 0
    nodeList = []
    activeBranches = set()
    newBranches = set()
    newNfa = set()
    lastOperation: str = ""

    def __init__(self, curInd, regex, openedCures, nodeList):
        self.curInd = curInd
        self.regex = regex
        self.openedCures = openedCures
        self.nodeList = nodeList
        self.activeBranches = set()
        self.newBranches = set()
        self.newNfa = set()

    def convert(self):
        for i in range(self.curInd, len(self.regex)):
            curChar = self.regex[i]
            print("start curINd: " + self.curInd.__str__() + " curChar: " + curChar)

            if curChar == "." or curChar == "|":
                print(curChar)
                self.lastOperation = curChar
            elif curChar == "*":
                print("*")
            elif curChar == ")":
                self.lastOperation = curChar
                self.openedCures -= 1
                if self.openedCures == 0:
                    self.joinBranches()
                    return
            elif curChar == "(":
                print("(")
                self.lastOperation = curChar
                self.openedCures += 1
                newNfa = Nfa(curInd=i + 1, regex=self.regex, openedCures=1, nodeList=self.nodeList)
                newNfa.convert()
                self.curInd = newNfa.curInd
                self.newNfa.add(newNfa)

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

    def addNewNode(self, lastOperation, newNode):
        if lastOperation == "." or lastOperation == "(" or lastOperation == ")":
            self.joinBranches()
            self.newBranches.add(newNode.ind)
        elif lastOperation == "":
            self.newBranches.add(newNode.ind)
        elif lastOperation == "|":
            self.newBranches.add(newNode.ind)

    def joinBranches(self):
        for ind in self.activeBranches:
            for i in self.newBranches:
                self.nodeList[ind].addStep(self.nodeList[i].char, self.nodeList[i].ind)

        self.activeBranches.clear()
        self.activeBranches.update(self.newBranches)
        self.newBranches.clear()

    def printNfa(self):
        nd: Node
        for nd in self.nodeList:
            pr = nd.ind.__str__()

            for st in nd.steps:
                if self.nodeList[st.to_node].isRecursive:
                    childs = self.getAllChildSteps(st.to_node)
                    pr += childs
                else:
                    pr = pr + " " + st.char.__str__() + " " + st.to_node.__str__()
            print(pr)

    def getAllChildSteps(self,ind):
        nd:Node = self.nodeList[ind]
        pr = ""
        for st in nd.steps:
            if self.nodeList[st.to_node].isRecursive and nd.ind != st.to_node:
                childs = self.getAllChildSteps(st.to_node)
                pr += childs
            else:
                pr = pr + " " + st.char.__str__() + " " + st.to_node.__str__()
        return pr



def addPlus(regex):
    ret = ""
    for i, v in enumerate(regex):
        if regex[i] == "|" or regex[i] == "(" or regex[i] == ")":
            ret += v
        elif regex[i] == "*":
            if i + 1 != len(regex):
                if regex[i + 1] == "|":
                    ret += v
                else:
                    ret = ret + v + "."
        elif i + 1 != len(regex):
            if regex[i + 1] == "|" or regex[i + 1] == "(" or regex[i + 1] == ")" or regex[i + 1] == "*":
                ret += v
            else:
                ret = ret + v + "."
        else:
            ret += v

    return ret


def main():
    # regex = input()
    regex = "a*bd|c"
    regex = addPlus(regex)
    nodeList = []
    nodeList.append(Node(ind=0, accept=False, char=""))
    nfa = Nfa(curInd=0, regex=regex, openedCures=0, nodeList=nodeList)
    nfa.activeBranches.add(0)
    nfa.convert()
    print(regex)
    nfa.printNfa()


if __name__ == "__main__":
    main()
