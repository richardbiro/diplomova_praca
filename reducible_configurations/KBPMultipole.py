from networkx import Graph, line_graph 
from networkx.algorithms import isomorphism
from unionfind import unionfind

class KBPMultipole:
    neigh = None
    n = None
    p = None
    edgeStates = None
    G = None
    
    def __init__(self, neigh):
        self.neigh = neigh
        self.p = len([deg for deg in neigh if len(deg) == 1])
        self.n = len([deg for deg in neigh if len(deg) == 3])
        self.setAllEdgesToState(-1)
        self.G = Graph()
        self.G.add_edges_from(self.edgeStates)

    def setEdgeToState(self, edge, state):
        u,v = edge
        self.edgeStates[(u,v)] = state
        self.edgeStates[(v,u)] = state

    def setEdgesToState(self, edges, state):
        for edge in edges:
            self.setEdgeToState(edge, state)
                
    def setAllEdgesToState(self, state):
        self.edgeStates = dict()
        for vx in range(self.p + self.n):
            for u in self.neigh[vx]:
                self.setEdgeToState((u,vx), state)

    def getEdgeStatesFromVertex(self, v):
        u1,u2,u3 = self.neigh[v]
        return sorted([self.edgeStates[(u1,v)],
                       self.edgeStates[(u2,v)],
                       self.edgeStates[(u3,v)]])

    def toString(self,taken=False):
        string = "\n"
        for u,v in self.edgeStates:
            if u < v and (not taken or self.edgeStates[(u,v)] > 0):
                string += str(u) + " " + str(v) + "\n"
        return string
        

    def containsCycle(self):
        union = unionfind(self.n)
        for v in range(self.p, self.p + self.n):
            for u in self.neigh[v]:
                if v > u >= self.p and self.edgeStates[(u,v)] > 0:
                    if union.issame(u - self.p, v - self.p):
                        return True
                    union.unite(u - self.p, v - self.p)    
        return False

    def isCovered(self):
        for x in range(self.p):
            v = self.neigh[x][0]
            if self.edgeStates[(x,v)] == -1:
                return False
            
        for v in range(self.p, self.p + self.n):
            if not self.isVertexDetermined(v):
                return False
                
        return True
    

    def isHamiltonianWay(self):
        return not self.containsCycle() and self.isCovered()
    

    def getHamiltonianWay(self):
        if self.isHamiltonianWay():
            hamiltonianWay = []
            semiEdges = set()
            
            for x in range(self.p):
                v = self.neigh[x][0]
                
                if self.edgeStates[(x,v)] > 0:
                    if x not in semiEdges:
                        semiEdges.add(x)
                        prev = x

                        while v >= self.p:
                            for u in self.neigh[v]:
                                if self.edgeStates[(u,v)] > 0:
                                    if u != prev:
                                        prev = v
                                        v = u
                                        break

                        semiEdges.add(v)
                        hamiltonianWay.append((x,v))

            return tuple(hamiltonianWay)

    def generateHamiltonianWayExtensions(self):
        if self.isHamiltonianWay():
            yield self.getHamiltonianWay()
            
        else:
            edge = self.getNotDeterminedEdge()
            
            if edge is not None:
                u,v = edge
                for newState in {0,1}:
                    self.setEdgeToState((u,v), newState)
                    sucess, determinedEdges = self.closure()
                    
                    if sucess and not self.containsCycle():
                        for hamiltonianWay in \
                                self.generateHamiltonianWayExtensions():
                            yield hamiltonianWay
                            
                    for determinedEdge in determinedEdges:
                        self.edgeStates[determinedEdge] = -1
                    
                self.setEdgeToState((u,v), -1)
                

    def getBipartiteColoring(self):
        coloring = (self.p + self.n)*[-1]
        stack = [(0,0)]

        while len(stack) > 0:
            v,color = stack.pop()
            coloring[v] = color
            
            for u in self.neigh[v]:
                if coloring[u] == -1:
                    stack.append((u,1-color))
                elif coloring[u] == color:
                    return

        return coloring[:self.p]

    def isVertexDetermined(self, v):
        states = self.getEdgeStatesFromVertex(v)
        return states[0] == 0 and states[1] > 0 and states[2] == states[1] 

    def canVertexBeDetermined(self, v):
        states = self.getEdgeStatesFromVertex(v)
        return states[0] == -1 and (states[1] > -1 or states[2] == 0)

    def getNotDeterminedEdge(self):
        for u in range(self.p, self.n + self.p):
            if (not self.canVertexBeDetermined(u)
                    and self.isVertexSolvable(u)):
                for v in self.neigh[u]:
                    if v >= self.p:
                        if (not self.canVertexBeDetermined(v)
                                and self.isVertexSolvable(v)
                                and self.edgeStates[(u,v)] == -1):
                            return (u,v)

    def determineVertex(self, v):
        states = self.getEdgeStatesFromVertex(v)
        changedEdges = []
        
        if states.count(0) == 1:
            newState = 1
        else:
            newState = 0
            
        for u in self.neigh[v]:
            if self.edgeStates[(u,v)] == -1:
                self.setEdgeToState((u,v), newState)
                changedEdges.append((u,v))
                changedEdges.append((v,u))
        return changedEdges

    def isVertexSolvable(self, v):
        states = self.getEdgeStatesFromVertex(v)
        return states.count(0) <= 1 and states[0] <= 0

    def closure(self):
        changedEdges = []
        toBeDetermined = set(v for v in range(self.p, self.p + self.n))

        while True:
            if self.containsCycle():
                return (False, changedEdges)
                
            determine = set()
            for v in list(toBeDetermined):
                if not self.isVertexSolvable(v):
                    return (False, changedEdges)
                if not self.isVertexDetermined(v) and self.canVertexBeDetermined(v):
                    determine.add(v)
                    toBeDetermined.remove(v)
                    
            if len(determine) == 0:
                break
                    
            for v in determine:
                changedEdges += self.determineVertex(v)
                
        return (True, changedEdges)

    def containsMultipole(self, M):
        matcher = isomorphism.GraphMatcher(line_graph(self.G), line_graph(M.G))
        return matcher.subgraph_is_isomorphic()

    def isCorrect(self):
        diamond = KBPMultipole(((2,),
                                (5,),
                                (0,3,7),
                                (2,4,8),
                                (3,5,9),
                                (1,4,6),
                                (5,7,9),
                                (2,6,8),
                                (3,7,9),
                                (4,6,8)))
        if self.containsMultipole(diamond):
            return False
        
        diamondBig = KBPMultipole(((2,),
                                   (5,),
                                   (0,3,7),
                                   (2,4,10),
                                   (3,5,11),
                                   (1,4,6),
                                   (5,7,13),
                                   (2,6,8),
                                   (7,9,13),
                                   (8,10,12),
                                   (3,9,11),
                                   (4,10,12),
                                   (9,11,13),
                                   (6,8,12)))
        if self.containsMultipole(diamondBig):
            return False

        return True
