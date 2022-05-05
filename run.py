import sys


class Step:
    char: str
    to_node: int
    to_accept: bool = False

    def __init__(self, char, to_node):
        self.char = char
        self.to_node = to_node

    def __init__(self, char, to_node, to_accept):
        self.char = char
        self.to_node = to_node
        self.to_accept = to_accept


class Node:
    ind: int
    accept = False
    steps = []

    def __init__(self, ind, accept, steps):
        self.ind = ind
        self.accept = accept
        self.steps = steps

    def next_steps(self, ch):
        ret = set()
        to_accept = False
        for step in self.steps:
            if step.char == ch:
                ret.add(step.to_node)
                if step.to_accept:
                    to_accept = True

        return to_accept, ret


def simulate(nodes, str):
    ret_str = ""
    cur_nodes = set()
    cur_nodes.add(0)
    for ch in str:
        accept_step = False
        new_cur_nodes = set()
        for node in cur_nodes:
            to_accept, ret = nodes.__getitem__(node).next_steps(ch)
            if to_accept:
                accept_step = to_accept

            for ob in ret:
                new_cur_nodes.add(ob)
        cur_nodes = new_cur_nodes
        if accept_step:
            ret_str += "Y"
        else:
            ret_str += "N"
    return ret_str


if __name__ == '__main__':

    inp = sys.stdin.readline().strip()
    line = sys.stdin.readline()
    numbers = line.split()
    numbers = [int(s) for s in numbers]
    automataNumber = numbers[0]

    line = sys.stdin.readline()
    numbers = line.split()
    numbers = [int(s) for s in numbers]
    accepts = set()
    for numb in numbers:
        accepts.add(numb)

    nodes = []

    for i in range(0, automataNumber):
        line = sys.stdin.readline()
        numbers = line.split()

        steps = []

        for i in range(0, int(numbers[0])):
            char = numbers[i * 2 + 1]
            ind = int(numbers[i * 2 + 2])
            acce = accepts.__contains__(ind)
            steps.append(Step(char=char, to_node=ind, to_accept=acce))
        nodes.append(Node(i, accepts.__contains__(i), steps))

    sys.stdout.write(simulate(nodes, inp)+"\n")

