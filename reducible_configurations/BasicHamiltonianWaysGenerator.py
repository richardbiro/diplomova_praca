from HamiltonianWaysGenerator import HamiltonianWaysGenerator
from itertools import chain, combinations, product
from unionfind import unionfind

class BasicHamiltonianWaysGenerator(HamiltonianWaysGenerator):
    generated = None
    generator = None

    def init(self, M_R):
        M_R.setAllEdgesToState(-1)
        self.generated = set()
        self.generator = self.generateHamiltonianWays(M_R)

    def generateHamiltonianWays(self, M_R):
        union = unionfind(M_R.p + M_R.n)
        for u,v in M_R.edgeStates:
            if u < v:
                union.unite(u,v)

        possibleHamiltonianWays = []
        for group in union.groups():
            possibleHamiltonianWays.append([])
            for k in range(0, len(group)+1, 2):
                for takenSemiEdges in combinations(
                        set(group).intersection(set(range(M_R.p))),k):
                    possibleHamiltonianWays[-1].append(takenSemiEdges)
        
        for X in product(*possibleHamiltonianWays):
            M_R.setAllEdgesToState(-1)
            semiEdges = set(chain.from_iterable(X))

            for x in range(M_R.p):
                v = M_R.neigh[x][0]
                if x in semiEdges:
                    newState = 1
                else:
                    newState = 0
                M_R.edgeStates[(x,v)] = newState
                M_R.edgeStates[(v,x)] = newState

            success, _ = M_R.closure()

            if success:
                for hamiltonianWay in M_R.generateHamiltonianWayExtensions():
                    if hamiltonianWay not in self.generated:
                        self.generated.add(hamiltonianWay)
                        yield hamiltonianWay 

    def nextHamiltonianWay(self):
        for hamiltonianWay in self.generator:
            yield hamiltonianWay
