#
#
# Store classes for different FDM Solvers

from src.FDMSolver import FDMSolver
from src import ConstAndScales

import numpy as np
import math

class Parabolic_FDM(FDMSolver): # type: ignore
    def __init__(self, Grid, nEmax) -> None:
        super().__init__(Grid, nEmax)

    def construct_matrix(self):
        nz = self.G.get_nz()
        A = np.zeros((nz, nz))
        scale = math.pow( (ConstAndScales.HBAR / self.G.get_dz()), 2) / 4.0

        for i in range(nz-1):
            if i != 1:
                A[i, i-1] = -scale * (1.0/self.meff[i-1] + 1.0/self.meff[i])
            if i != nz:
                A[i, i+1] = -scale * (1.0/self.meff[i+1] + 1.0/self.meff[i])
            if ( (i != 1) and (i != nz) ):
                A[i, i] = self.V[i] + scale * (1.0/self.meff[i+1] + 2.0/self.meff[i] + 1.0/self.meff[i-1])
        
        A[0, 0] = A[1, 1]
        A[nz-1, nz-1] = A[nz-2, nz-2]
        return A

class Kane_FDM(FDMSolver):      # type: ignore
    def __init__(self, Grid, nEmax) -> None:
        super().__init__(Grid, nEmax)

    def construct_matrix(self):
        nz = self.G.get_nz()
        A = np.zeros((4*nz, 4*nz))
        scale = math.pow(ConstAndScales.HBAR / self.G.get_dz(), 2) / 4.0

        for i in range(nz):
            A_i = 1.0 / self.alpha[i]
            M_i = A_i / self.meff[i]
            V_i = self.V[i]

            # Handle boundaries
            if (i == 1) or (i == nz-1):
                A_plus = 1.0/self.alpha[i]
                A_minus = A_plus
                M_plus = A_minus/self.meff[i]
                M_minus = M_plus
                V_plus = self.V[i]
                V_minus = V_plus
            else:
                A_plus =  1.0/self.alpha[i+1]
                A_minus = 1.0/self.alpha[i-1]
                M_plus = A_plus/self.meff[i+1]
                M_minus = A_minus/self.meff[i-1]
                V_plus = self.V[i+1]
                V_minus = self.V[i-1]
            
            B_minus =  A_minus*A_i
            B_0 = A_minus*A_plus
            B_plus = A_plus*A_i

            # Add subdiagonals of A0, A1 and A2
            if i!=1:
                A[3*nz+i,i-1]       = -scale * (1.0-V_plus/A_plus)*(M_minus*B_plus*(1.0 - V_i/A_i) + M_i*B_0*(1.0-V_minus/A_minus)) 	# A0
                A[3*nz+i,nz+i-1]    = -scale * (M_i*(A_minus+A_plus-V_minus-V_plus) + M_minus*(A_plus+A_i-V_i-V_plus))				    # A1
                A[3*nz+i,2*nz+i-1]  = -scale * (M_minus+M_i)																	        # A2

            # Add superdiagonals of A0, A1 and A2
            if i!=nz-1:
                A[3*nz+i,i+1]       = -scale * (1.0-V_minus/A_minus)*(M_plus*B_minus*(1.0 - V_i/A_i) + M_i*B_0*(1.0-V_plus/A_plus))     # A0
                A[3*nz+i,nz+i+1]    = -scale * (M_i*(A_minus+A_plus-V_minus-V_plus)+M_plus*(A_minus+A_i-V_i-V_minus))				    # A1
                A[3*nz+i,2*nz+i+1]  = -scale * (M_plus+M_i); 																		    # A2

            # Add diagonal of A0 block
            A[3*nz+i,i] = -scale * (V_i * (M_plus*A_minus+M_minus*A_plus) + V_minus * (M_plus*A_i+2.0*M_i*A_plus) + V_plus * (M_minus*A_i+2.0*M_i*A_minus) - M_plus*V_i*V_minus - M_minus*V_i*V_plus - 2.0*M_i*V_plus*V_minus - M_plus*B_minus - 2.0*M_i*B_0 - M_minus*B_plus) + V_i * (1.0-V_i/A_i) * (A_i*B_0 - B_plus*V_minus - B_minus*V_plus + A_i*V_minus*V_plus)
            # Add diagonal of A1 block
            A[3*nz+i,nz+i] = -scale * (M_plus*(V_i+V_minus-A_i-A_minus) + M_minus*(V_i+V_plus-A_i-A_plus) + 2.0*M_i*(V_minus+V_plus-A_minus-A_plus)) - V_i*V_i*(A_plus+A_minus) + V_i * (B_minus+2.0*B_0+B_plus) + V_minus*B_plus + V_plus*B_minus - V_i*V_minus*(2.0*A_plus+A_i) - V_i*V_plus*(2.0*A_minus+A_i) - A_i*V_minus*V_plus + V_i*V_i*(V_minus+V_plus) + 2.0*V_i*V_minus*V_plus - A_i*B_0
            # Add diagonal of A2 block
            A[3*nz+i,2*nz+i] = scale * (M_plus+2.0*M_i+M_minus) - B_plus - B_0 - B_minus + A_plus*(2.0*V_i+V_minus) + A_minus*(2.0*V_i+V_plus) + A_i*(V_i+V_minus+V_plus) - V_i*V_i - 2.0*V_i*(V_minus+V_plus) - V_minus*V_plus
            # Add diagonal of A3 block
            A[3*nz+i,3*nz+i] = V_plus+2.0*V_i+V_minus-A_plus-A_i-A_minus
            
            # Insert identity matrices
            A[i,nz+i] = 1.0
            A[nz+i,2*nz+i] = 1.0
            A[2*nz+i,3*nz+i] = 1.0         

        return A

class Taylor_FDM(FDMSolver):    # type: ignore
    def __init__(self, Grid, nEmax) -> None:
        super().__init__(Grid, nEmax)

    def construct_matrix(self):
        nz = self.G.get_nz()
        A = np.zeros((nz, nz))
        B = A
        scale = math.pow(ConstAndScales.HBAR/self.G.get_dz(), 2) / 4.0

        for i in range(nz):
            if i != 1:
                B[i, i-1] = -scale * (self.alpha[i] / self.meff[i] + self.alpha[i-1] / self.meff[i-1])
                A[i, i-1] = -scale * ((1.0+self.alpha[i-1] *self.V[i-1]) / self.meff[i-1] + (1.0+self.alpha[i]*self.V[i])/self.meff[i])
            if i != nz-1:
                B[i, i+1] = -scale * (self.alpha[i] / self.meff[i] + self.alpha[i+1] / self.meff[i+1])
                A[i, i+1] = -scale * ((1.0+self.alpha[i+1]*self.V[i+1])/self.meff[i+1]+(1.0+self.alpha[i]*self.V[i])/self.meff[i])
            if (i!=1) and (i!=nz-1):
                B[i,i] = 1.0 + scale * (self.alpha[i+1] / self.meff[i+1] + 2.0 * self.alpha[i] / self.meff[i] + self.alpha[i-1] / self.meff[i-1])
                A[i,i] = self.V[i] + scale * ((1.0+self.alpha[i+1]*self.V[i+1])/self.meff[i+1] + 2.0 * (1.0+self.alpha[i]*self.V[i])/self.meff[i] + (1.0+self.alpha[i-1]*self.V[i-1])/self.meff[i-1])
			    
        return A
    
class SolverFactory:
    from src.Solvers_FDM import Parabolic_FDM, Taylor_FDM, Kane_FDM
    from src.Solvers_TMM import Parabolic_TMM, Taylor_TMM, Kane_TMM, Ekenberg_TMM
    solver_map = {
        ("FDM", "Parabolic"): Parabolic_FDM,
        ("FDM", "Taylor"): Taylor_FDM,
        ("FDM", "Kane"): Kane_FDM,
        ("TMM", "Parabolic"): Parabolic_TMM,
        ("TMM", "Taylor"): Taylor_TMM,
        ("TMM", "Kane"): Kane_TMM,
        ("TMM", "Ekenberg"): Ekenberg_TMM,
    }

    @staticmethod
    def create(grid, solver, np_type, nstmax):
        return SolverFactory.solver_map[(solver, np_type)](grid, nstmax)