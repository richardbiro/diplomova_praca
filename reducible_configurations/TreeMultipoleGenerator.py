from itertools import chain
from KBPMultipole import KBPMultipole
from MultipoleGenerator import MultipoleGenerator

class TreeMultipoleGenerator(MultipoleGenerator):
    p = None
    coloring = None
    vertices = None
    generator = None
    
    def init(self, coloring, maximum=None):
        self.p = len(coloring)
        self.coloring = list(coloring)
        self.vertices = dict()
        self.generator = self.getTreeKBPMultipoles()

    def getEdge(self, u, v):
        return (min(u,v),max(u,v))
    
    def getTree2KBPMultipoles(self):
        newVertex = self.p
        
        T2 = []
        for i in range(self.p):
            T2.append([])
            for j in range(self.p):
                T2[i].append([])
                for _ in range(2):
                    T2[i][j].append(set())

        for i in range(self.p):
            T2[i][i][self.coloring[i]].add(i)

        for size in range(1, self.p):
            for i in range(self.p):
                j = i + size
                if j >= self.p: break
                
                for k in range(i,j):
                    for c in range(2):
                        for u in T2[i][k][1-c]:
                            for v in T2[k+1][j][1-c]:
                                
                                T2[i][j][c].add(newVertex)
                                self.vertices[newVertex] = (u,v)
                                newVertex += 1
        
        return T2


    def getEdgesFrom(self, vertex):
        if vertex < self.p:
            yield set()
            
        else:
            u,v = self.vertices[vertex]
            for edges1 in self.getEdgesFrom(u):
                for edges2 in self.getEdgesFrom(v):
                    yield edges1.union(edges2)\
                                .union({self.getEdge(u, vertex)})\
                                .union({self.getEdge(v, vertex)})


    def getTreeKBPMultipoles(self):
        T2 = self.getTree2KBPMultipoles()
        root = self.p + len(self.vertices)
        
        for k in range(1, self.p-1):
            for u in T2[1][k][self.coloring[0]]:
                for v in T2[k+1][self.p-1][self.coloring[0]]:                    
                    for edges1 in self.getEdgesFrom(u):
                        for edges2 in self.getEdgesFrom(v):
                            yield edges1.union(edges2)\
                                        .union({self.getEdge(0, root)})\
                                        .union({self.getEdge(u, root)})\
                                        .union({self.getEdge(v, root)})
        
        
        

    def nextMultipole(self):
        for edges in self.generator:
            used = sorted(set(chain.from_iterable(edges)))
            newLabels = {used[index]: index for index in range(len(used))}
  
            neigh = []
            
            for uu,vv in edges:
                u = newLabels[uu]
                v = newLabels[vv]
                for _ in range(len(neigh), max(u,v)+1):
                    neigh.append(set())
                neigh[u].add(v)
                neigh[v].add(u)
                
            for index in range(len(neigh)):
                neigh[index] = tuple(neigh[index])
                    
            yield KBPMultipole(tuple(neigh))
