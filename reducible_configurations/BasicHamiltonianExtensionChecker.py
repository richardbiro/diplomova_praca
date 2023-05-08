from HamiltonianExtensionChecker import HamiltonianExtensionChecker
from itertools import chain

class BasicHamiltonianExtensionChecker(HamiltonianExtensionChecker):
    
    def check(self, h, M_G):
        M_G.setAllEdgesToState(-1)
        semiEdges = set(chain.from_iterable(h))

        for index in range(len(h)):
            x1,x2 = h[index]

            v1 = M_G.neigh[x1][0]
            if v1 < M_G.p and v1 not in semiEdges:
                return False
            
            v2 = M_G.neigh[x2][0]
            if v2 < M_G.p and v2 not in semiEdges:
                return False

        for x in range(M_G.p):
            v = M_G.neigh[x][0]
            if x not in semiEdges:
                newState = 0
            else:
                newState = 1
            M_G.edgeStates[(x,v)] = newState
            M_G.edgeStates[(v,x)] = newState

        M_G.closure()

        for hamiltonianWay in M_G.generateHamiltonianWayExtensions():
            if hamiltonianWay == h:
                return True

        return False
