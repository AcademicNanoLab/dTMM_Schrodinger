#
#   Abstract Class for all solvers
#

from abc import ABC, abstractmethod
from src.Grid import Grid

import numpy as np

class BaseSolver(ABC):
    def __init__(self, Grid:Grid, nEmax) -> None:
        """Base Solver class for all TMM and FDM solvers

        Args:
            Grid (Grid): Grid object for bandstructure and effective mass
            nEmax (int?): Max number of energy levels
        """

        self.G = Grid
        self.V = self.G.get_bandstructure_potential()
        self.meff = self.G.get_effective_mass()
        self.nE = nEmax
        
        self.tolerance = np.float64(8.88e-6)

    @abstractmethod
    def get_wavefunctions(self):
        pass