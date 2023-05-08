from BasicHamiltonianWaysGenerator import BasicHamiltonianWaysGenerator
from BasicHamiltonianExtensionChecker import BasicHamiltonianExtensionChecker

class BasicReducibilityChecker():
    
    def check(self, M_G, M_R):
        HWG = BasicHamiltonianWaysGenerator()
        HWG.init(M_R)
        HEC = BasicHamiltonianExtensionChecker()

        for hamiltonianWay in HWG.nextHamiltonianWay():
            if not HEC.check(hamiltonianWay, M_G):
                return False
        return True
        
        
        
