#
#
#   Shrodinger Equation solved by Finite Difference Method
#
# 
from BaseSolver import BaseSolver
from Grid import Grid
import ConstAndScales

from abc import abstractmethod
import math
import numpy as np
# import cmath

class FDMSolver(BaseSolver):
    def __init__(self, Grid:Grid, nEmax) -> None:
        super().__init__(Grid, nEmax)
        self.alpha = Grid.get_alpha_kane()

    @abstractmethod
    def construct_system_matrix(self):      
        pass

    def sort_and_filter_eigenvalues(self, eigenvalues):
        Vmin = min(self.V)
        Vmax = max(self.V)
        
        # sort
        posEfound = np.argsort(eigenvalues)
        
        # filter
        valid_pos = []
        for idx in posEfound:
            if Vmin < eigenvalues[idx] < Vmax:
                valid_pos.append(idx)
        
        return valid_pos
    
    def get_wavefunctions(self):    
        # Can add test later to check that all energy values have small or no imaginary part.
        psis = []
        energies = []

        A = self.construct_system_matrix()
        eigenvalues, eigenvectors = np.linalg.eig(A) # type: ignore

        # eigvals = np.diag(eigenvalues)
        Eidx = self.sort_and_filter_eigenvalues(eigenvalues)

        nz = self.G.get_nz()
        if self.nE <= 0 or self.nE > len(Eidx):
            nE = len(Eidx)

        for i in range(nE):
            E = eigenvalues[Eidx[i]].real # type: ignore
            psiWhole = eigenvectors[:, Eidx[i]].real # type: ignore

            energies.append(E)
            psi = psiWhole[: nz]
            norm_const = math.sqrt( 1 / np.trapezoid(abs(psi)**2) ) / self.G.get_dz()*ConstAndScales.ANGSTROM
            psi = norm_const *psi
            psis.append(psi)

        return np.array(energies), psis