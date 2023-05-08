from itertools import product

class BasicColoringGenerator():
    maxp = None
    colorings = None
    
    def init(self, maxp):
        self.maxp = maxp
        self.colorings = set()

    def nextColoring(self):
        for p in range(3, self.maxp+1):
            for coloring in product((0,1),repeat=p):
                wasColoringUsed = False
            
                for rot in range(p):
                    coloring1 = coloring[rot:]+coloring[:rot]
                    if coloring1 in self.colorings or coloring1[::-1] in self.colorings:
                        wasColoringUsed = True
                        break
                    
                    coloring2 = tuple(1-x for x in coloring[rot:]+coloring[:rot])
                    if coloring2 in self.colorings or coloring2[::-1] in self.colorings:
                        wasColoringUsed = True
                        break

                if not wasColoringUsed:
                    self.colorings.add(coloring)
                    yield coloring
    
