#
# 
# Schrodinger equation solver class using dTMM method4
from src.BaseSolver import BaseSolver
from src.Grid import Grid
from src import ConstAndScales

from abc import abstractmethod
import numpy as np
import math
from scipy import optimize
# import cmath

class TMMSolver(BaseSolver):
    def __init__(self, Grid: Grid, nEmax) -> None:
        super().__init__(Grid, nEmax)

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

    def get_matrix_j(self, j, E):
        Mj = np.identity(2)
        if (j>1):
            p = self.get_wavevector(j-1,E)
            q = self.get_wavevector(j,E)
            qpq = self.get_coefficient(j,E)
            zj = self.G.get_zj(j)
            Mj[1,1]=0.5*(1+qpq)*math.exp((p-q)*zj)  # type: ignore
            Mj[1,2]=0.5*(1-qpq)*math.exp(-(p+q)*zj) # type: ignore
            Mj[2,1]=0.5*(1-qpq)*math.exp((p+q)*zj)  # type: ignore
            Mj[2,2]=0.5*(1+qpq)*math.exp(-(p-q)*zj) # type: ignore

        return Mj

    def get_matrix_derivative_j(self, j, E):
        dMj = np.identity(2)
        if (j>1):
            p = self.get_wavevector(j-1,E)
            q = self.get_wavevector(j,E)
            dp = self.get_wavevector_derivative(j-1,E)
            dq = self.get_wavevector_derivative(j,E)
            qpq=self.get_coefficient(j,E)
            dqpq=self.get_coefficient_derivative(j,E)
            zj = self.G.get_zj(j)
            dMj[1,1]= 0.5*( dqpq + (1.0+qpq)*zj*(dp-dq))*math.exp((p-q)*zj)  # type: ignore
            dMj[1,2]= 0.5*(-dqpq - (1.0-qpq)*zj*(dp+dq))*math.exp(-(p+q)*zj) # type: ignore
            dMj[2,1]= 0.5*(-dqpq + (1.0-qpq)*zj*(dp+dq))*math.exp((p+q)*zj)  # type: ignore
            dMj[2,2]= 0.5*( dqpq - (1.0+qpq)*zj*(dp-dq))*math.exp(-(p-q)*zj) # type: ignore
        
        return dMj

    def get_left_TMM_cumulative_sum(self, E):
        nz=self.G.get_nz()
        TM_left = np.zeros((2, 2, nz))
        TM_left[:,:,1]=np.identity(2)
        for j in range(2, nz):
            Mj=self.get_matrix_j(j,E)
            TM_left[:,:,j]= np.multiply(Mj, TM_left[:,:,j-1])

        return TM_left
    
    def get_right_TMM_cumulative_sum(self, E):
        nz = self.G.get_nz()
        TM_right = np.zeros((2, 2, nz))
        TM_right[:,:,nz] = self.get_matrix_j(nz, E)
        for j in range(1, nz-1, -1):
            Mj = self.get_matrix_j(j, E)
            TM_right[:,:,j] = TM_right[:,:,j+1]*Mj
        TM_right[:,:,1] = TM_right[:,:,2]
        
        return TM_right

    def get_m11(self, E):
        nz = self.G.get_nz()
        TM = np.identity(2)
        for j in range(2, nz):
            Mj = self.get_matrix_j(j, E)
            TM = Mj*TM
        m11=abs(TM[1,1])

        return m11
    
    def get_m11_derivative(self, E):
        dTM = np.zeros((2, 2))
        TM_left = self.get_left_TMM_cumulative_sum(E)
        TM_right = self.get_right_TMM_cumulative_sum(E)
        nz = self.G.get_nz()
        
        for j in range(2, nz-1):
            dMj = self.get_matrix_derivative_j(j, E)
            A = TM_right[:,:,j+1]
            B = TM_left[:,:,j-1]
            dTM = dTM + A*dMj*B
        
        dTM = dTM + self.get_matrix_derivative_j(nz, E) *TM_left[:,:,nz-1]
        m11 = TM_left[1,1,nz]
        dTM11 = dTM[1,1]
        dm11 = 1/abs(m11)* ( dTM11.real*m11.real + dTM11.imag*m11.imag )
        
        return dm11

    def get_wavefunction(self, E):
        nz = self.G.get_nz()
        A1B1 = np.zeros((2, 1))
        A1B1[1] = 1.0
        psi = np.zeros((1, nz))

        for j in range(2, nz):
            qjzj = self.get_wavevector(j, E) *self.G.get_zj(j)
            Mj = self.get_matrix_j(j, E)
            A1B1 = Mj *A1B1
            tmp = A1B1[1]*math.exp(qjzj) + A1B1[2]*math.exp(-qjzj)
            psi[j] = tmp.real
        
        norm_const = math.sqrt(1/np.trapezoid(np.power(abs(psi), 2))/ self.G.get_dz()*ConstAndScales.ANGSTROM)
        psi = norm_const*psi

        return psi
    
    def get_wavefunctions(self):
        found = 0
        energies = []
        psis = []
        dE = self.G.get_dE()
        Emax = max(self.V)
        E = min(self.V) + 3*dE
        m11_km1 = self.get_m11(E-dE)
        m11_km2 = self.get_m11(E-2*dE)

        while E<Emax:
            m11_k = self.get_m11(E)
            if ((m11_k>m11_km1) and (m11_km1<m11_km2)):
                found = found + 1
                Elo = E-2*dE
                Ehi = E
                f = self.get_m11_derivative

                Ex = optimize.brentq(f, Elo, Ehi, rtol=self.tolerance)
                psi = self.get_wavefunction(Ex)
                energies.append(Ex)
                psis.append(psi)
            
            m11_km2 = m11_km1
            m11_km1 = m11_k
            E = E + dE
            if self.nE>0 and found == self.nE:
                break

        return np.array(energies), psis
                

