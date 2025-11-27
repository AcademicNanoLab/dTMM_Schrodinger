#
#
#   Shrodinger Equation solved by Finite Difference Method
#
# 
from Grid import Grid
import ConstAndScales

import cmath
import math
import numpy as np

class FDMSolver:
    def __init__(self, solverType, Grid:Grid, nEmax) -> None:
        self.solverType = solverType
        self.G = Grid
        self.nEmax = nEmax
        self.V = self.G.get_bandstructure_potential()
        self.meff = self.G.get_effective_mass()
        self.alpha = self.G.get_alpha_kane()
        self.nE = nEmax
    
    # NOTE: Currently implemented in "solverTypes" class. Same functions commented at the end of this file.
    def construct_system_matrix(self):      
        if self.solverType == "Parabolic":
            Solver = ParabolicSolver(self.G, self.alpha, self.meff, self.V)
        elif self.solverType == "Kane":
            Solver = KaneSolver(self.G, self.alpha, self.meff, self.V)
        elif self.solverType == "Taylor":
            Solver = TaylorSolver(self.G, self.alpha, self.meff, self.V)
        
        return Solver.construct_matrix()

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
        eigenvalues, eigenvectors = np.linalg.eig(A)

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