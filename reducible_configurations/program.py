from BasicMultipoleGenerator import BasicMultipoleGenerator
from BasicHamiltonianWaysGenerator import BasicHamiltonianWaysGenerator
from BasicHamiltonianExtensionChecker import BasicHamiltonianExtensionChecker
from BasicGeneralAlgorithm import BasicGeneralAlgorithm

MG = BasicMultipoleGenerator()
HWG = BasicHamiltonianWaysGenerator()
HEC = BasicHamiltonianExtensionChecker()
maxsize = 15
maxp = 7

BasicGeneralAlgorithm(MG, HWG, HEC, maxsize, maxp).execute()
