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
        print("pre-construction")
        A = self.construct_matrix()
        print("post_construction")

        # Use sparse solver for Kane, dense otherwise
        if A.shape[0] == 4*nz:  # adjust if Kane matrix is 4*nz
            # sparse format
            print("recognised kane matrix, using sparse solver")
            A_sparse = sp.csr_matrix(A)
            k = min(max(20, self.nE), A_sparse.shape[0]-2)
            sigma = np.mean([min(self.V), max(self.V)])
            eigenvalues, eigenvectors = spla.eigs(A_sparse, k=k, sigma=sigma, which="LM")
            eigenvectors = eigenvectors.real
            eigenvalues = eigenvalues.real
        else:
            print("not kane, using dense solver")
            eigenvalues, eigenvectors = np.linalg.eig(A)
            eigenvectors = eigenvectors.real
            eigenvalues = eigenvalues.real

        Eidx = self.sort_and_filter_eigenvalues(eigenvalues)
        print("sorted and filtered eigenvalues")

        if self.nE <= 0 or self.nE > len(Eidx):
            nE = len(Eidx)
        else:
            nE = self.nE

        print("generating wavefunction")
        for i in range(nE):
            E = eigenvalues[Eidx[i]]
            psiWhole = eigenvectors[:, Eidx[i]]

            energies.append(E)
            psi = psiWhole[:nz]
            norm_const = math.sqrt(1 / np.trapezoid(abs(psi)**2) ) / self.G.get_dz() * ConstAndScales.ANGSTROM
            psi = norm_const * psi
            psis.append(psi)

        print("got wavefunction, returning")
        return np.array(energies), psis

    # def sort_and_filter_eigenvalues(self, eigenvalues):
    #     Vmin = min(self.V)
    #     Vmax = max(self.V)
        
    #     # sort
    #     posEfound = np.argsort(eigenvalues)
        
    #     # filter
    #     valid_pos = []
    #     for idx in posEfound:
    #         if Vmin < eigenvalues[idx] < Vmax:
    #             valid_pos.append(idx)
        
    #     return valid_pos
    
    # def get_wavefunctions(self):    
    #     # Can add test later to check that all energy values have small or no imaginary part.
    #     psis = []
    #     energies = []

    #     print("pre-construction")
    #     A = self.construct_matrix()
    #     eigenvalues, eigenvectors = np.linalg.eig(A) # type: ignore

    #     # eigvals = np.diag(eigenvalues)
    #     Eidx = self.sort_and_filter_eigenvalues(eigenvalues)

    #     nz = self.G.get_nz()
    #     if self.nE <= 0 or self.nE > len(Eidx):
    #         nE = len(Eidx)
    #     else:
    #         nE = self.nE

    #     for i in range(nE):
    #         E = eigenvalues[Eidx[i]].real # type: ignore
    #         psiWhole = eigenvectors[:, Eidx[i]].real # type: ignore

    #         energies.append(E)
    #         psi = psiWhole[: nz]
    #         norm_const = math.sqrt( 1 / np.trapezoid(abs(psi)**2) ) / self.G.get_dz()*ConstAndScales.ANGSTROM
    #         psi = norm_const *psi
    #         psis.append(psi)
        
    #     print("got wavefunction, returning")

    #     return np.array(energies), psis