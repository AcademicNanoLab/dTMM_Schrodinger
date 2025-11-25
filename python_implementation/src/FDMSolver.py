#
#
#   Shrodinger Equation solved by Finite Difference Method
#
# 
from Grid import Grid
from SolverTypes import ParabolicSolver, KaneSolver, TaylorSolver
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
        # NOTE: What is the goal of this function?
        # Think there are better ways of doing this for Python.
        Vmin = min(self.V)
        Vmax = max(self.V)
        
        Efound = []
        iEfound = []
        for i in range(len(eigenvalues)):
            Er = eigenvalues[i].real
            if Vmin < Er < Vmax:
                iEfound.append(i)
                Efound.append(Er)
        
        # NOTE: Doesn't return same thing as MATLAB. 
        indices = np.sort(Efound)
        return iEfound
    
    def get_wavefunctions(self):
        psis = []
        energies = []
        A = self.construct_system_matrix()
        eigenvalues, eigenvectors = np.linalg.eig(A)
        eigvals = np.diag(eigenvalues)
        Eid = self.sort_and_filter_eigenvalues(eigvals)

        nz = self.G.get_nz()
        if self.nE <= 0 or self.nE > len(Eid):
            nE = len(Eid)
        
        for i in range(1, nE):
            # E=real(eigvals(Eid(i)));
            idx = Eid[i]
            ev = eigvals[idx]
            E = ev.real # type: ignore

            # NOTE: This is not right. Need to consider how best to translate.
            energies.append(E)
            psiWhole = eigenvectors[Eid[i]].real # type: ignore
            psi = psiWhole[1, nz]
            norm_const = math.sqrt( 1 / np.trapezoid(abs(psi)**2) ) / self.G.get_dz()*ConstAndScales.ANGSTROM
            psi = norm_const *psi
            psis = [psis, psi]

        return energies, psis





    # def construct_parabolic_matrix(self):
    #     nz = self.G.get_nz()
    #     A = np.zeros(nz)
    #     scale = math.pow( (ConstAndScales.HBAR / self.G.get_dz()), 2) / 4.0

    #     for i in range(1,nz):
    #         if i != 1:
    #             A[i, i-1] = -scale * (1.0/self.meff[i-1] + 1.0/self.meff[i])
    #         if i != nz:
    #             A[i, i+1] = -scale * (1.0/self.meff[i+1] + 1.0/self.meff[i])
    #         if ( (i != 1) and (i != nz) ):
    #             A[i, i] = self.V[i] + scale * (1.0/self.meff[i+1] + 2.0/self.meff[i] + 1.0/self.meff[i-1])
        
    #     A[1, 1] = A[2, 2]
    #     A[nz, nz] = A[nz-1, nz-1]
    #     return A
    
    # def construct_kane_matrix(self):
    #     nz = self.G.get_nz()
    #     A = np.zeros(4*nz)
    #     scale = math.pow(ConstAndScales.HBAR / self.G.get_dz(), 2) / 4.0
    #     for i in range(1, nz):
    #         A_i = 1.0 / self.alpha[i]
    #         M_i = A_i / self.meff[i]
    #         V_i = self.V[i]

    #         if (i == 1) or (i == nz):
    #             A_plus = 1.0/self.alpha[i]
    #             A_minus = A_plus
    #             M_plus = A_minus/self.meff[i]
    #             M_minus = M_plus
    #             V_plus = self.V[i]
    #             V_minus = V_plus
    #         else:
    #             A_minus = 1.0/self.alpha[i-1]
    #             A_plus =  1.0/self.alpha[i+1]
    #             M_minus = A_minus/self.meff[i-1]
    #             M_plus = A_plus/self.meff[i+1]
    #             V_minus = self.V[i-1]
    #             V_plus = self.V[i+1]
            
    #         B_minus =  A_minus*A_i
    #         B_0 = A_minus*A_plus
    #         B_plus = A_plus*A_i

    #         # Add subdiagonals of A0, A1 and A2
    #         if i!=1:
    #             A[3*nz+i,i-1]       = -scale * (1.0-V_plus/A_plus)*(M_minus*B_plus*(1.0 - V_i/A_i) + M_i*B_0*(1.0-V_minus/A_minus)) 	# A0
    #             A[3*nz+i,nz+i-1]    = -scale * (M_i*(A_minus+A_plus-V_minus-V_plus) + M_minus*(A_plus+A_i-V_i-V_plus))				    # A1
    #             A[3*nz+i,2*nz+i-1]  = -scale * (M_minus+M_i)																	        # A2

    #         # Add superdiagonals of A0, A1 and A2
    #         if i!=nz:
    #             A[3*nz+i,i+1]       = -scale * (1.0-V_minus/A_minus)*(M_plus*B_minus*(1.0 - V_i/A_i) + M_i*B_0*(1.0-V_plus/A_plus))     # A0
    #             A[3*nz+i,nz+i+1]    = -scale * (M_i*(A_minus+A_plus-V_minus-V_plus)+M_plus*(A_minus+A_i-V_i-V_minus))				    # A1
    #             A[3*nz+i,2*nz+i+1]  = -scale * (M_plus+M_i); 																		    # A2

    #         # Add diagonal of A0 block
    #         A[3*nz+i,i] = -scale * (V_i * (M_plus*A_minus+M_minus*A_plus) + V_minus * (M_plus*A_i+2.0*M_i*A_plus) + V_plus * (M_minus*A_i+2.0*M_i*A_minus) - M_plus*V_i*V_minus - M_minus*V_i*V_plus - 2.0*M_i*V_plus*V_minus - M_plus*B_minus - 2.0*M_i*B_0 - M_minus*B_plus) + V_i * (1.0-V_i/A_i) * (A_i*B_0 - B_plus*V_minus - B_minus*V_plus + A_i*V_minus*V_plus)
    #         # Add diagonal of A1 block
    #         A[3*nz+i,nz+i] = -scale * (M_plus*(V_i+V_minus-A_i-A_minus) + M_minus*(V_i+V_plus-A_i-A_plus) + 2.0*M_i*(V_minus+V_plus-A_minus-A_plus)) - V_i*V_i*(A_plus+A_minus) + V_i * (B_minus+2.0*B_0+B_plus) + V_minus*B_plus + V_plus*B_minus - V_i*V_minus*(2.0*A_plus+A_i) - V_i*V_plus*(2.0*A_minus+A_i) - A_i*V_minus*V_plus + V_i*V_i*(V_minus+V_plus) + 2.0*V_i*V_minus*V_plus - A_i*B_0
    #         # Add diagonal of A2 block
    #         A[3*nz+i,2*nz+i] = scale * (M_plus+2.0*M_i+M_minus) - B_plus - B_0 - B_minus + A_plus*(2.0*V_i+V_minus) + A_minus*(2.0*V_i+V_plus) + A_i*(V_i+V_minus+V_plus) - V_i*V_i - 2.0*V_i*(V_minus+V_plus) - V_minus*V_plus
    #         # Add diagonal of A3 block
    #         A[3*nz+i,3*nz+i] = V_plus+2.0*V_i+V_minus-A_plus-A_i-A_minus
            
    #         # Insert identity matrices
    #         A[i,nz+i] = 1.0
    #         A[nz+i,2*nz+i] = 1.0
    #         A[2*nz+i,3*nz+i] = 1.0           
    #     return A
    
    # def construct_taylor_matrix(self):
    #     nz = self.G.get_nz()
    #     A = np.zeros(nz)
    #     B = A
    #     scale = math.pow(ConstAndScales.HBAR/self.G.get_dz(), 2) / 4.0

    #     for i in range(1, nz):
    #         if i != 1:
    #             B[i, i-1] = -scale * (self.alpha[i] / self.meff[i] + self.alpha[i-1] / self.meff[i-1])
    #             A[i, i-1] = -scale * ((1.0+self.alpha[i-1] *self.V[i-1]) / self.meff[i-1] + (1.0+self.alpha[i]*self.V[i])/self.meff[i])
    #         if i != nz:
    #             B[i, i+1] = -scale * (self.alpha[i] / self.meff[i] + self.alpha[i+1] / self.meff[i+1])
    #             A[i, i+1] = -scale * ((1.0+self.alpha[i+1]*self.V[i+1])/self.meff[i+1]+(1.0+self.alpha[i]*self.V[i])/self.meff[i])
    #         if (i!=1) and (i!=nz):
    #             B[i,i] = 1.0 + scale * (self.alpha[i+1] / self.meff[i+1] + 2.0 * self.alpha[i] / self.meff[i] + self.alpha[i-1] / self.meff[i-1])
    #             A[i,i] = self.V[i] + scale * ((1.0+self.alpha[i+1]*self.V[i+1])/self.meff[i+1] + 2.0 * (1.0+self.alpha[i]*self.V[i])/self.meff[i] + (1.0+self.alpha[i-1]*self.V[i-1])/self.meff[i-1])
			    
    #     return A