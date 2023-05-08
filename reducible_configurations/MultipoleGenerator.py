from abc import ABC, abstractmethod

class MultipoleGenerator(ABC):
    @abstractmethod
    def init(self, coloring, maximum=None):
        pass

    @abstractmethod
    def nextMultipole(self):
        pass
