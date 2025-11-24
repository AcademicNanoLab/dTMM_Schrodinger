#
#
#
#
# Store classes for different solver types
from abc import ABC, abstractmethod
import math
import numpy as np

import ConstAndScales

class BaseSolver(ABC):
    def __init__(self, Grid, alpha, meff, V) -> None:
        self.G = Grid
        self.alpha = alpha
        self.meff = meff
        self.V = V
        self.hbar_pow2 = math.pow(ConstAndScales.HBAR, 2)

    @abstractmethod
    def get_wavevector(self, j, E):
        pass

    @abstractmethod
    def get_coefficient(self, j, E):
        pass
    
    @abstractmethod
    def get_wavevector_derivative(self, j, E):
        pass
    
    @abstractmethod
    def get_coefficient_derivative(self, j, E):
        pass

    @abstractmethod
    def construct_matrix(self):
        pass


# *** Concrete Classes *** #

class ParabolicSolver(BaseSolver):
    
    def get_wavevector(self, j, E):
        return math.sqrt(2.0*self.meff[j]/self.hbar_pow2*(self.V[j]-E))

    def get_wavevector_derivative(self, j, E):
        kj = self.get_wavevector(j,E)
        return (- self.meff[j] / (kj * self.hbar_pow2))
    
    def get_coefficient(self, j, E):
        p = self.get_wavevector(j-1,E)
        q = self.get_wavevector(j,E)
        return self.meff[j] / self.meff(j - 1) * p / q
    
    def get_coefficient_derivative(self, j, E):
        p = self.get_wavevector(j-1,E)
        q = self.get_wavevector(j,E)
        dp = self.get_wavevector_derivative(j-1,E)
        dq = self.get_wavevector_derivative(j,E)
        return self.meff[j] / self.meff(j - 1) * (q*dp-p*dq)/(q * q)

    def construct_matrix(self):
        nz = self.G.get_nz()
        A = np.zeros(nz)
        scale = math.pow( (ConstAndScales.HBAR / self.G.get_dz()), 2) / 4.0

        for i in range(1,nz):
            if i != 1:
                A[i, i-1] = -scale * (1.0/self.meff[i-1] + 1.0/self.meff[i])
            if i != nz:
                A[i, i+1] = -scale * (1.0/self.meff[i+1] + 1.0/self.meff[i])
            if ( (i != 1) and (i != nz) ):
                A[i, i] = self.V[i] + scale * (1.0/self.meff[i+1] + 2.0/self.meff[i] + 1.0/self.meff[i-1])
        
        A[1, 1] = A[2, 2]
        A[nz, nz] = A[nz-1, nz-1]
        return A

class TaylorSolver(BaseSolver):

    def get_wavevector(self, j, E):
        return math.sqrt(2.0*self.meff[j]/self.hbar_pow2*(self.V[j]-E)/(1.0-self.alpha[j]*(E-self.V[j])))

    def get_wavevector_derivative(self, j, E):
        kj = self.get_wavevector(j,E)
        return ( - self.meff[j] / (kj * self.hbar_pow2) / math.pow(1.0-self.alpha[j]*(E-self.V[j]),2) )
    
    def get_coefficient(self, j, E):
        p = self.get_wavevector(j-1,E)
        q = self.get_wavevector(j,E)
        return self.meff[j] / self.meff(j - 1) / (1.0-self.alpha[j]*(E-self.V[j])) * (1.0-self.alpha(j-1)*(E-self.V(j-1))) * p / q
    
    def get_coefficient_derivative(self, j, E):
        p = self.get_wavevector(j-1, E)
        q = self.get_wavevector(j, E)
        dp = self.get_wavevector_derivative(j-1, E)
        dq = self.get_wavevector_derivative(j, E)
        return self.meff[j] / self.meff(j-1) *(1.0-self.alpha(j-1)*(E-self.V(j-1))) / (1.0-self.alpha[j]*(E-self.V[j]))* (q*dp-p*dq)/(q * q) + p/q * (self.alpha[j]*self.meff[j]/math.pow(1.0-self.alpha[j]*(E-self.V[j]),2) / self.meff(j-1)*(1.0-self.alpha(j-1)*(E-self.V(j-1))) - self.meff[j]/(1.0-self.alpha[j]*(E-self.V[j]))/self.meff(j-1)*self.alpha(j-1))

    def construct_matrix(self):
        nz = self.G.get_nz()
        A = np.zeros(nz)
        B = A
        scale = math.pow(ConstAndScales.HBAR/self.G.get_dz(), 2) / 4.0

        for i in range(1, nz):
            if i != 1:
                B[i, i-1] = -scale * (self.alpha[i] / self.meff[i] + self.alpha[i-1] / self.meff[i-1])
                A[i, i-1] = -scale * ((1.0+self.alpha[i-1] *self.V[i-1]) / self.meff[i-1] + (1.0+self.alpha[i]*self.V[i])/self.meff[i])
            if i != nz:
                B[i, i+1] = -scale * (self.alpha[i] / self.meff[i] + self.alpha[i+1] / self.meff[i+1])
                A[i, i+1] = -scale * ((1.0+self.alpha[i+1]*self.V[i+1])/self.meff[i+1]+(1.0+self.alpha[i]*self.V[i])/self.meff[i])
            if (i!=1) and (i!=nz):
                B[i,i] = 1.0 + scale * (self.alpha[i+1] / self.meff[i+1] + 2.0 * self.alpha[i] / self.meff[i] + self.alpha[i-1] / self.meff[i-1])
                A[i,i] = self.V[i] + scale * ((1.0+self.alpha[i+1]*self.V[i+1])/self.meff[i+1] + 2.0 * (1.0+self.alpha[i]*self.V[i])/self.meff[i] + (1.0+self.alpha[i-1]*self.V[i-1])/self.meff[i-1])
			    
        return A

class KaneSolver(BaseSolver):

    def get_wavevector(self, j, E):
        return math.sqrt(2.0*self.meff[j]*(1.0+self.alpha[j]*(E-self.V[j]))/self.hbar_pow2*(self.V[j]-E))
    
    def get_wavevector_derivative(self, j, E):
        kj = self.get_wavevector(j,E)
        return ( - self.meff[j] / (kj * self.hbar_pow2) * (1.0 + 2.0*self.alpha[j]*(E-self.V[j])) )

    def get_coefficient(self, j, E):
        p = self.get_wavevector(j-1,E)
        q = self.get_wavevector(j,E)
        return self.meff[j] / self.meff(j - 1) * (1.0+self.alpha[j]*(E-self.V[j])) / (1.0+self.alpha(j-1)*(E-self.V(j-1))) * p / q
    
    def get_coefficient_derivative(self, j, E) :
        p = self.get_wavevector(j-1, E)
        q = self.get_wavevector(j, E)
        dp = self.get_wavevector_derivative(j-1, E)
        dq = self.get_wavevector_derivative(j, E)
        return self.meff[j] / self.meff(j-1) * (1.0+self.alpha[j]*(E-self.V[j]))/(1.0+self.alpha(j-1)*(E-self.V(j-1)))* (q*dp-p*dq)/(q * q) + p/q * self.meff[j]/self.meff(j-1)*(self.alpha[j] - self.alpha(j-1) + self.alpha[j]*self.alpha(j-1)*(self.V[j] - self.V(j-1))) / (1.0+self.alpha(j-1)*(E-self.V(j-1))) / (1.0+self.alpha(j-1)*(E-self.V(j-1)))

    def construct_matrix(self):
        nz = self.G.get_nz()
        A = np.zeros(4*nz)
        scale = math.pow(ConstAndScales.HBAR / self.G.get_dz(), 2) / 4.0
        for i in range(1, nz):
            A_i = 1.0 / self.alpha[i]
            M_i = A_i / self.meff[i]
            V_i = self.V[i]

            if (i == 1) or (i == nz):
                A_plus = 1.0/self.alpha[i]
                A_minus = A_plus
                M_plus = A_minus/self.meff[i]
                M_minus = M_plus
                V_plus = self.V[i]
                V_minus = V_plus
            else:
                A_minus = 1.0/self.alpha[i-1]
                A_plus =  1.0/self.alpha[i+1]
                M_minus = A_minus/self.meff[i-1]
                M_plus = A_plus/self.meff[i+1]
                V_minus = self.V[i-1]
                V_plus = self.V[i+1]
            
            B_minus =  A_minus*A_i
            B_0 = A_minus*A_plus
            B_plus = A_plus*A_i

            # Add subdiagonals of A0, A1 and A2
            if i!=1:
                A[3*nz+i,i-1]       = -scale * (1.0-V_plus/A_plus)*(M_minus*B_plus*(1.0 - V_i/A_i) + M_i*B_0*(1.0-V_minus/A_minus)) 	# A0
                A[3*nz+i,nz+i-1]    = -scale * (M_i*(A_minus+A_plus-V_minus-V_plus) + M_minus*(A_plus+A_i-V_i-V_plus))				    # A1
                A[3*nz+i,2*nz+i-1]  = -scale * (M_minus+M_i)																	        # A2

            # Add superdiagonals of A0, A1 and A2
            if i!=nz:
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

class EkenbergSolver(BaseSolver):
    
    def get_wavevector(self, j, E):
        return math.sqrt(self.meff[j]/(self.hbar_pow2*self.alpha[j]) * (math.sqrt(1.0+4.0*self.alpha[j]*(self.V[j]-E))-1.0))
    
    def get_wavevector_derivative(self, j, E):
        kj = self.get_wavevector(j,E)
        return -self.meff[j]/(self.hbar_pow2*kj)/(1.0 + self.hbar_pow2*self.alpha[j]/self.meff[j]*kj*kj)

    def get_coefficient(self, j, E):
        p = self.get_wavevector(j-1,E)
        q = self.get_wavevector(j,E)
        return (self.meff[j] / self.meff(j - 1) * (1.0+self.hbar_pow2*self.alpha(j-1)/self.meff(j-1)*p*p) / (1.0+self.hbar_pow2*self.alpha[j]/self.meff[j]*q*q)	) * p / q
    
    def get_coefficient_derivative(self, j, E) :
        p = self.get_wavevector(j-1, E)
        q = self.get_wavevector(j, E)
        dp = self.get_wavevector_derivative(j-1, E)
        dq = self.get_wavevector_derivative(j, E)
        return self.meff[j] / self.meff(j - 1) / (q+self.hbar_pow2*self.alpha[j]/self.meff[j]*q*q*q) * ((1.0 + 3.0 * self.hbar_pow2*self.alpha(j-1)/self.meff(j-1)*p*p) * dp - (1.0+self.hbar_pow2*self.alpha(j-1)/self.meff(j-1)*p*p) / (1.0+self.hbar_pow2*self.alpha[j]/self.meff[j]*q*q) * p / q * (1.0 + 3.0 * self.hbar_pow2*self.alpha[j]/self.meff[j]*q*q)*dq)