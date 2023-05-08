from itertools import chain
from KBPMultipole import KBPMultipole
from MultipoleGenerator import MultipoleGenerator

class BasicMultipoleGenerator(MultipoleGenerator):
    p = None
    generator = None
    
    def init(self, coloring, maximum=None):
        self.p = len(coloring)
        sequence = [x for x in range(self.p)]
        self.generator = self.processSequence(list(sequence),
                                              list(coloring),
                                              self.p, maximum, set())

    def getEdge(self, u, v):
        return (min(u,v),max(u,v))
    
    def canBeConnected(self, u, v, ucolor, vcolor, edges):
        return self.getEdge(u,v) not in edges and ucolor != vcolor

    def connectTwoVertices(self, sequence, coloring, edges):
        u,v = sequence[0],sequence[1]
        ucolor,vcolor = coloring[0],coloring[1]
        
        if self.canBeConnected(u, v, ucolor, vcolor, edges):
            yield edges.union({self.getEdge(u,v)})

    def splitSequence(self, index, sequence, coloring, n, maximum, edges):
        length = len(sequence)
        u,v = sequence[index],sequence[length-1]
        ucolor,vcolor = coloring[index],coloring[length-1]
        
        if self.canBeConnected(u, v, ucolor, vcolor, edges):
            for edges1 in self.processSequence(
                    sequence[:index],
                    coloring[:index],
                    n, maximum, edges.union({self.getEdge(u,v)})):
                for edges2 in self.processSequence(
                        sequence[index+1:length-1],
                        coloring[index+1:length-1],
                        n, maximum, edges1):
                    yield edges2

    def addNewVertex(self, v, sequence, coloring, n, maximum, edges):
        u = sequence.pop()
        ucolor = coloring.pop()
        
        for newEdges in self.processSequence(
                sequence+[v,v],
                coloring+[1-ucolor,1-ucolor],
                n+1, maximum, edges.union({self.getEdge(u,v)})):
            yield newEdges.union({self.getEdge(u,v)})

    def processSequence(self, sequence, coloring, n, maximum, edges):
        length = len(sequence) 
        if length == 0:
            yield edges
            
        elif length == 2:
            for newEdges in self.connectTwoVertices(
                    sequence,
                    coloring,
                    edges):
                yield newEdges

        elif length > 2:        
            for index in range(length-1):
                for newEdges in self.splitSequence(
                        index,
                        sequence,
                        coloring,
                        n, maximum, edges):
                    yield newEdges
            
            newVertex = max(sequence)+1
            if len(edges) > 0:
                newVertex = max(newVertex,
                                max(chain.from_iterable(edges))+1)
                
            if newVertex < maximum:
                for newEdges in self.addNewVertex(
                        newVertex,
                        sequence,
                        coloring,
                        n, maximum, edges):
                    yield newEdges
    
    def nextMultipole(self):
        for edges in self.generator:
            neigh = []
            
            for u,v in edges:
                for _ in range(len(neigh), max(u,v)+1):
                    neigh.append(set())
                neigh[u].add(v)
                neigh[v].add(u)
                
            for index in range(len(neigh)):
                neigh[index] = tuple(neigh[index])
                    
            M = KBPMultipole(tuple(neigh))

            if M.isCorrect():
                yield M
