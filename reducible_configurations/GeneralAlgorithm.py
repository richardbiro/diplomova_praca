from abc import ABC, abstractmethod

class GeneralAlgorithm(ABC):
    multipoleGenerator = None
    hamiltonianWaysGenerator = None
    hamiltonianExtensionChecker = None

    maxsize = None
    maxp = None

    def __init__(self, MG, HWG, HEC, maxsize, maxp):
        self.multipoleGenerator = MG
        self.hamiltonianWaysGenerator = HWG
        self.hamiltonianExtensionChecker = HEC
        self.maxsize = maxsize+1
        self.maxp = maxp
    
    @abstractmethod
    def execute(self, showNotReducible=False):
        pass
