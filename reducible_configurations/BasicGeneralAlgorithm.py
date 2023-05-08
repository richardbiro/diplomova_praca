from BasicColoringGenerator import BasicColoringGenerator
from BasicMultipoleGenerator import BasicMultipoleGenerator
from itertools import product
from GeneralAlgorithm import GeneralAlgorithm

class BasicGeneralAlgorithm(GeneralAlgorithm):
    
    def execute(self, showNotReducible=False):
        colorings = set()
        allMultipoles = []
        multipoles = dict()
        minimalReducible = set()

        print("Generating multipoles with size <=", self.maxsize-1,
              "and <=", self.maxp, "semiedges\n")
        CG = BasicColoringGenerator()
        CG.init(self.maxp)

        for coloring in CG.nextColoring():
            print("Generating multipoles for coloring", coloring)
            multipoles[coloring] = []

            generator = BasicMultipoleGenerator()
            generator.init(coloring, self.maxsize)
            for M in generator.nextMultipole():
                allMultipoles.append((M.p + M.n, coloring, M))
                multipoles[coloring].append((M.p + M.n, M))
        print()                
                        
        allMultipoles.sort(key = lambda x: x[0])
        for coloring in multipoles:
            multipoles[coloring].sort(key = lambda x: x[0])

        counter = 0
        
        for sizeM_G, coloring, M_G in allMultipoles:
            
            if counter%500 == 0:
                print("Iterating through multipoles (" + str(counter)\
                      + "/" + str(len(allMultipoles)) + ")")
                
            counter += 1
            containsReducibleConfiguration = False

            for M in minimalReducible:
                if M.p + M.n < M_G.p + M_G.n and M_G.containsMultipole(M):
                    containsReducibleConfiguration = True
                    break

            if not containsReducibleConfiguration:
                hasReductor = False
                
                for sizeM_R, M_R in multipoles[coloring]:
                    if sizeM_R >= sizeM_G:
                        break
                    
                    isReductor = True
                    self.hamiltonianWaysGenerator.init(M_R)
                    
                    for h in self.hamiltonianWaysGenerator\
                                 .nextHamiltonianWay():
                        if not self.hamiltonianExtensionChecker\
                                   .check(h, M_G):
                            isReductor = False
                            break
                        
                    if isReductor:
                        print("Multipole" + M_G.toString() +\
                              "is reducible to" + M_R.toString())
                        minimalReducible.add(M_G)
                        hasReductor = True
                        break

                if not hasReductor and showNotReducible:
                    print("Multipole" + M_G.toString() + "is not reducible")
