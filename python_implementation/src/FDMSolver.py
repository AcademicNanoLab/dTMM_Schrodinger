#
#
#   Shrodinger Equation solved by Finite Difference Method
#
# 
from src.BaseSolver import BaseSolver
from src.Grid import Grid
from src import ConstAndScales

from abc import abstractmethod
import math
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

# import cmath

class FDMSolver(BaseSolver):
    def __init__(self, Grid:Grid, nEmax) -> None:
        super().__init__(Grid, nEmax)
        self.alpha = Grid.get_alpha_kane()

    @abstractmethod
    def construct_matrix(self):      
        pass

    def sort_and_filter_eigenvalues(self, eigenvalues, Vmin=None, Vmax=None):
        if Vmin is None:
            Vmin = min(self.V)
        if Vmax is None:
            Vmax = max(self.V)

        # Sort by real part
        posEfound = np.argsort(eigenvalues.real)

        # Filter by potential range
        valid_pos = [idx for idx in posEfound if Vmin < eigenvalues[idx].real < Vmax]
        return valid_pos

    def get_wavefunctions(self):
        psis = []
        energies = []

        nz = self.G.get_nz()
        A = self.construct_matrix()

        if A.shape[0] == 4*nz: # type: ignore
            # Recognised Kane matrix, use sparse solver
            A_sparse = sp.csr_matrix(A)
            k = min(max(20, self.nE), A_sparse.shape[0]-2) # type: ignore
            sigma = np.mean([min(self.V), max(self.V)])
            eigenvalues, eigenvectors = spla.eigs(A_sparse, k=k, sigma=sigma, which="LM") # type: ignore
            eigenvectors = eigenvectors.real # type: ignore
            eigenvalues = eigenvalues.real # type: ignore
        else:                   
            # Not Kane matrix, use dense solver.
            eigenvalues, eigenvectors = np.linalg.eig(A) # type: ignore
            eigenvectors = eigenvectors.real
            eigenvalues = eigenvalues.real

        Eidx = self.sort_and_filter_eigenvalues(eigenvalues)

        if self.nE <= 0 or self.nE > len(Eidx):
            nE = len(Eidx)
        else:
            nE = self.nE

        for i in range(nE):
            E = eigenvalues[Eidx[i]]
            psiWhole = eigenvectors[:, Eidx[i]]

            energies.append(E)
            psi = psiWhole[:nz]
            norm_const = math.sqrt(1 / np.trapezoid(abs(psi)**2) ) / self.G.get_dz() * ConstAndScales.ANGSTROM
            psi = norm_const * psi
            psis.append(psi)

        return np.array(energies), psis
