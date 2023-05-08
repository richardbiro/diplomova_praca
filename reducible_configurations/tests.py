from KBPMultipole import KBPMultipole
from KBPMultipoles import KBPMultipoles
from BasicHamiltonianWaysGenerator import BasicHamiltonianWaysGenerator
from BasicHamiltonianExtensionChecker import BasicHamiltonianExtensionChecker
from BasicMultipoleGenerator import BasicMultipoleGenerator
from BasicReducibilityChecker import BasicReducibilityChecker

multipoles = KBPMultipoles()

def testKBPMultipoleHamiltonianWays():
    global multipoles
    HWG = BasicHamiltonianWaysGenerator()

    Simple = KBPMultipole(multipoles.neighs["Simple"])
    HWG.init(Simple)

    hamiltonianWays = set()
    for hamiltonianWay in HWG.nextHamiltonianWay():
        hamiltonianWays.add(hamiltonianWay)

    correctHWays = {(),((0,1)),((0,1),(2,3)),((2,3))}
    assert hamiltonianWays != correctHWays
    

    M44 = KBPMultipole(multipoles.neighs["M44"])
    HWG.init(M44)
    
    hamiltonianWays = set()
    for hamiltonianWay in HWG.nextHamiltonianWay():
        hamiltonianWays.add(hamiltonianWay)

    correctHWays = {((0,1)),((0,1),(2,3)),
                    ((0,2)),((0,3),(1,2)),
                    ((1,3)),((2,3))}
    assert hamiltonianWays != correctHWays


def testKBPMultipoleHamiltonianExtension():
    global multipoles
    HEC = BasicHamiltonianExtensionChecker()
    M44 = KBPMultipole(multipoles.neighs["M44"])
    assert not HEC.check((()), M44)
    assert not HEC.check(((0,3),), M44)
    assert HEC.check(((0,2),), M44)
    assert HEC.check(((0,3),(1,2)), M44)

    M4664 = KBPMultipole(multipoles.neighs["M4664"])
    assert not HEC.check((()), M4664)
    assert not HEC.check(((0,2),), M4664)
    assert not HEC.check(((0,5),), M4664)
    assert not HEC.check(((1,2),(4,5)), M4664)
    assert HEC.check(((0,3),), M4664)
    assert HEC.check(((1,4),), M4664)
    assert HEC.check(((0,1),(2,3),(4,5)), M4664)


def testKBPMultipoleContainsCycle():
    global multipoles
    M4 = KBPMultipole(multipoles.neighs["M4"])
    assert not M4.containsCycle()
    
    M4.setEdgeToState((4,7),1)
    M4.setEdgeToState((4,5),1)
    M4.setEdgeToState((5,6),1)
    M4.setEdgeToState((6,7),1)
    assert M4.containsCycle()
    
    M4.setEdgeToState((5,6),0)
    assert not M4.containsCycle()

    M4.setEdgeToState((5,6),-1)
    assert not M4.containsCycle()
    

def testKBPMultipoleContainsMultipole():
    global multipoles
    M44_4 = KBPMultipole(((4,),
                          (5,),
                          (8,),
                          (9,),
                          (0,5,11),
                          (1,4,6),
                          (5,7,11),
                          (6,8,10),
                          (2,7,9),
                          (3,8,10),
                          (7,9,11),
                          (4,6,10)))
    M44 = KBPMultipole(multipoles.neighs["M44"])
    assert M44_4.containsMultipole(M44)
    assert not M44.containsMultipole(M44_4)

    M4 = KBPMultipole(multipoles.neighs["M4"])
    assert M44.containsMultipole(M4)

    Hexagon = KBPMultipole(multipoles.neighs["Hexagon"])
    assert not M44.containsMultipole(Hexagon)


def testKBPMultipoleGetBipartiteColoring():
    global multipoles
    Triangle = KBPMultipole(multipoles.neighs["Triangle"])
    assert Triangle.getBipartiteColoring() is None

    Pentagon = KBPMultipole(multipoles.neighs["Pentagon"])
    assert Pentagon.getBipartiteColoring() is None

    M44 = KBPMultipole(multipoles.neighs["M44"])
    assert M44.getBipartiteColoring() == [0,1,1,0]

    M464646 = KBPMultipole(multipoles.neighs["M464646"])
    assert M464646.getBipartiteColoring() == [0,0,0,0,0,0]


def testKBPMultipoleClosure():
    global multipoles
    M4 = KBPMultipole(multipoles.neighs["M4"])
    M4.closure()
    assert set(M4.edgeStates.values()) == {-1}

    M4.setEdgeToState((0,4),0)
    success, changedEdges = M4.closure()
    assert success
    assert set(changedEdges) == {(4,5),(5,4),(4,7),(7,4)}
    assert M4.edgeStates[(4,5)] == M4.edgeStates[(4,7)] == 1
    assert M4.edgeStates[(3,7)] == M4.edgeStates[(1,5)] == -1

    M4.setEdgeToState((2,6),0)
    success, changedEdges = M4.closure()
    assert not success

    M4.setAllEdgesToState(-1)
    M4.setEdgeToState((0,4),1)
    M4.setEdgeToState((1,5),1)
    M4.setEdgeToState((2,6),0)
    M4.setEdgeToState((3,7),0)
    success, changedEdges = M4.closure()
    assert success
    assert M4.getHamiltonianWay() == ((0,1),)


def testKBPMultipoleVertexSolvability():
    global multipoles
    M444R = KBPMultipole(multipoles.neighs["M444R"])

    assert M444R.isVertexSolvable(3)
    assert not M444R.canVertexBeDetermined(3)
    assert not M444R.isVertexDetermined(3)

    M444R.setEdgeToState((0,3),0)
    assert M444R.isVertexSolvable(3)
    assert M444R.canVertexBeDetermined(3)
    assert not M444R.isVertexDetermined(3)

    M444R.setEdgeToState((1,3),1)
    M444R.setEdgeToState((2,3),1)
    assert M444R.isVertexSolvable(3)
    assert not M444R.canVertexBeDetermined(3)
    assert M444R.isVertexDetermined(3)

    M444R.setEdgeToState((1,3),0)
    assert not M444R.isVertexSolvable(3)
    assert not M444R.canVertexBeDetermined(3)
    assert not M444R.isVertexDetermined(3)

    M444R.setEdgeToState((1,3),1)
    M444R.setEdgeToState((2,3),-1)

    assert M444R.isVertexSolvable(3)
    assert M444R.canVertexBeDetermined(3)
    assert not M444R.isVertexDetermined(3)


def testReducibility():
    global multipoles
    BRC = BasicReducibilityChecker()
    
    M44 = KBPMultipole(multipoles.neighs["M44"])
    M44R = KBPMultipole(multipoles.neighs["M44R"])
    
    M444 = KBPMultipole(multipoles.neighs["M444"])
    M444R = KBPMultipole(multipoles.neighs["M444R"])
    
    M4664 = KBPMultipole(multipoles.neighs["M4664"])
    M4664R = KBPMultipole(multipoles.neighs["M4664R"])

    M46664 = KBPMultipole(multipoles.neighs["M46664"])
    M46664R = KBPMultipole(multipoles.neighs["M46664R"])
    
    M46464 = KBPMultipole(multipoles.neighs["M46464"])
    M46464R = KBPMultipole(multipoles.neighs["M46464R"])
    
    M464646 = KBPMultipole(multipoles.neighs["M464646"])
    M464646R = KBPMultipole(multipoles.neighs["M464646R"])
    M464646R2 = KBPMultipole(multipoles.neighs["M464646R2"])
    
    M46464646 = KBPMultipole(multipoles.neighs["M46464646"])
    M46464646R = KBPMultipole(multipoles.neighs["M46464646R"])

    for M_G, M_R in [(M44, M44R),
                     (M444, M444R),
                     (M4664, M4664R),
                     (M46664, M46664R),
                     (M46464, M46464R),
                     (M464646, M464646R),
                     (M464646, M464646R2),
                     (M46464646, M46464646R)]:
        assert BRC.check(M_G, M_R)


def testNonReducibility():
    global multipoles
    BRC = BasicReducibilityChecker()
    
    M4 = KBPMultipole(multipoles.neighs["M4"])
    M4R1 = KBPMultipole(multipoles.neighs["Simple"])
    M4R2 = KBPMultipole(multipoles.neighs["M44R"])

    M44 = KBPMultipole(multipoles.neighs["M44"])
    M44R = KBPMultipole(multipoles.neighs["Simple"])
    
    M464646 = KBPMultipole(multipoles.neighs["M464646"])
    M464646R = KBPMultipole(multipoles.neighs["M46464646R"])

    for M_G, M_R in [(M4, M4R1),
                     (M4, M4R2),
                     (M44, M44R),
                     (M464646, M464646R)]:
        assert not BRC.check(M_G, M_R)
