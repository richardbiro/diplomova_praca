from abc import ABC, abstractmethod

class HamiltonianWaysGenerator(ABC):
    @abstractmethod
    def init(self, M_R):
        pass

    @abstractmethod
    def nextHamiltonianWay(self):
        pass
