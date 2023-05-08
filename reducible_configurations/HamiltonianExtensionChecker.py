from abc import ABC, abstractmethod

class HamiltonianExtensionChecker(ABC):
    @abstractmethod
    def check(self, h, M_G):
        pass
