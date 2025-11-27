#
#
#
#
# Store classes for different TMM Solvers
import math
import TMMSolver

# *** Concrete Classes *** #
class Parabolic_TMM(TMMSolver): # type: ignore
    def __init__(self, Grid, nEmax) -> None:
        super().__init__(Grid, nEmax)
    
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

class Taylor_TMM(TMMSolver): # type: ignore
    def __init__(self, Grid, nEmax) -> None:
        super().__init__(Grid, nEmax)

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

class Kane_TMM(TMMSolver): # type: ignore
    def __init__(self, Grid, nEmax) -> None:
        super().__init__(Grid, nEmax)

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

class Ekenberg_TMM(TMMSolver): # type: ignore
    def __init__(self, Grid, nEmax) -> None:
        super().__init__(Grid, nEmax)
    
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
    
