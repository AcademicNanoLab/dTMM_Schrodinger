#
#
# Abstract Class for all solvers

from abc import ABC, abstractmethod
from Grid import Grid

import numpy as np

class BaseSolver(ABC):
    def __init__(self, solver:str, solverType:str, Grid:Grid, nEmax) -> None:
        """Base Solver class for all TMM and FDM solvers

        Args:
            solver (str): 'TMM' or 'FDM' parent solver
            solverType (str): Parabolic, Taylor, Kane or Ekenberg(TMM Only)
            Grid (Grid): Grid object for bandstructure and effective mass
            nEmax (int?): Max number of energy levels
        """
        self.solver = solver
        self.solverType = solverType
        self.G = Grid
        self.V = self.G.get_bandstructure_potential()
        self.meff = self.G.get_effective_mass()
        self.nE = nEmax
        
        self.tolerance = np.float64(8.88e-16)

    @abstractmethod
    def get_wavefunctions(self):
        pass