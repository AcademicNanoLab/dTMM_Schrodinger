#
# 
# Schrodinger equation solver class using dTMM method4
from src.BaseSolver import BaseSolver
from src.Grid import Grid
from src import ConstAndScales

from abc import abstractmethod
import numpy as np
import math
import timeit
from concurrent.futures import ProcessPoolExecutor

# from numba import njit
# from scipy import optimize
# import cmath

# @njit(cache=True, fastmath=True)
# def _matmul2x2(A, B):
#     C = np.empty((2, 2), dtype=np.complex128)
#     C[0,0] = A[0,0]*B[0,0] + A[0,1]*B[1,0]
#     C[0,1] = A[0,0]*B[0,1] + A[0,1]*B[1,1]
#     C[1,0] = A[1,0]*B[0,0] + A[1,1]*B[1,0]
#     C[1,1] = A[1,0]*B[0,1] + A[1,1]*B[1,1]
#     return C

class TMMSolver(BaseSolver):
    def __init__(self, Grid: Grid, nEmax) -> None:
        super().__init__(Grid, nEmax)
        self.hbar_pow2 = ConstAndScales.HBAR **2

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
        if j == 0:
            return np.identity(2, dtype=np.complex128)
        
        p = self.get_wavevector(j-1,E)
        q = self.get_wavevector(j,E)
        qpq = self.get_coefficient(j,E)
        zj = self.G.get_zj(j)

        Mj = np.empty((2,2), dtype=np.complex128)
        Mj[0,0]=0.5*(1+qpq)*np.exp((p-q)*zj)  # type: ignore
        Mj[0,1]=0.5*(1-qpq)*np.exp(-(p+q)*zj) # type: ignore
        Mj[1,0]=0.5*(1-qpq)*np.exp((p+q)*zj)  # type: ignore
        Mj[1,1]=0.5*(1+qpq)*np.exp(-(p-q)*zj) # type: ignore
        
        return Mj

    def get_matrix_derivative_j(self, j, E):
        dMj = np.identity(2, dtype=complex)
        if (j>0):
            p = self.get_wavevector(j-1,E)
            q = self.get_wavevector(j,E)
            dp = self.get_wavevector_derivative(j-1,E)
            dq = self.get_wavevector_derivative(j,E)
            qpq=self.get_coefficient(j,E)
            dqpq=self.get_coefficient_derivative(j,E)
            zj = self.G.get_zj(j)
            dMj[0,0]= 0.5*( dqpq + (1.0+qpq)*zj*(dp-dq))*np.exp((p-q)*zj)  # type: ignore
            dMj[0,1]= 0.5*(-dqpq - (1.0-qpq)*zj*(dp+dq))*np.exp(-(p+q)*zj) # type: ignore
            dMj[1,0]= 0.5*(-dqpq + (1.0-qpq)*zj*(dp+dq))*np.exp((p+q)*zj)  # type: ignore
            dMj[1,1]= 0.5*( dqpq - (1.0+qpq)*zj*(dp-dq))*np.exp(-(p-q)*zj) # type: ignore
        
        return dMj

    def get_left_TMM_cumulative_sum(self, E):
        nz=self.G.get_nz()
        TM_left = np.zeros((2, 2, nz), dtype=complex)
        TM_left[:,:,0]=np.identity(2, dtype=complex)
        for j in range(1, nz):
            Mj=self.get_matrix_j(j,E)
            TM_left[:,:,j]= Mj @ TM_left[:,:,j-1]

        return TM_left
    
    def get_right_TMM_cumulative_sum(self, E):
        nz = self.G.get_nz()
        TM_right = np.zeros((2, 2, nz), dtype=complex)
        TM_right[:,:,nz-1] = self.get_matrix_j(nz-1, E)

        for j in range(nz-2, 0, -1):
            Mj = self.get_matrix_j(j, E)
            TM_right[:,:,j] = TM_right[:,:,j+1] @ Mj
        
        TM_right[:,:,0] = TM_right[:,:,1]
        return TM_right

    def get_m11(self, E):
        nz = self.G.get_nz()
        TM = np.identity(2, dtype=complex)
        for j in range(1, nz):
            Mj = self.get_matrix_j(j, E)
            TM = Mj @ TM
        m11=abs(TM[0,0])

        return m11
    
    def get_m11_derivative(self, E):
        nz = self.G.get_nz()
        dTM = np.zeros((2, 2), dtype=complex)
        TM_left = self.get_left_TMM_cumulative_sum(E)
        TM_right = self.get_right_TMM_cumulative_sum(E)
        
        for j in range(1, nz-1):
            dMj = self.get_matrix_derivative_j(j, E)
            A = TM_right[:,:,j+1]
            B = TM_left[:,:,j-1]
            dTM += A @ dMj @ B

        dTM += self.get_matrix_derivative_j(nz-1, E) @ TM_left[:,:,nz-2]
        m11 = TM_left[0,0,nz-1]
        dTM11 = dTM[0,0]
        dm11 = 1/abs(m11) * ( dTM11.real*m11.real + dTM11.imag*m11.imag )

        return dm11

    def get_wavefunction(self, E):
        nz = self.G.get_nz()
        A1B1 = np.zeros((2,1), dtype=complex)
        A1B1[0,0] = 1.0
        psi = np.zeros(nz, dtype=complex)

        psi[0] = 1.0
        for j in range(1, nz):
            qjzj = self.get_wavevector(j, E) * self.G.get_zj(j)
            Mj = self.get_matrix_j(j, E)

            A1B1 = Mj @ A1B1
            psi[j] = np.real( A1B1[0,0]*np.exp(qjzj) + A1B1[1,0]*np.exp(-qjzj) )        
        
        norm_const = math.sqrt(1/np.trapezoid(np.power(abs(psi), 2))/ self.G.get_dz()*ConstAndScales.ANGSTROM)
        psi *= norm_const
        # print(np.trapezoid(abs(psi)**2))

        return psi
    
    def bisect(self,f,Elo,Ehi,tol):
        a=Elo
        b=Ehi
        fa = f(a)
        for i in range(40):
            Ex=(a+b)/2
            fx=f(Ex)
            if abs(fx)<tol:
                break
            if (fx*fa<0):
                b=Ex
            else:
                a=Ex
        return Ex

    def _solve_root(self, args):
        Elo, Ehi = args
        f = self.get_m11_derivative
        Ex = self.bisect(f, Elo, Ehi, 1e-8)
        psi = self.get_wavefunction(Ex)
        return Ex, psi

    def get_wavefunctions(self):
        found = 0
        energies = []
        psis = []
        dE = self.G.get_dE()
        Emax = max(self.V-5*dE)
        E = min(self.V) + 3*dE
        m11_km1 = self.get_m11(E-dE)
        m11_km2 = self.get_m11(E-2*dE)

        tasks = []
        while E<Emax:
            m11_k = self.get_m11(E)
            if ((m11_k>m11_km1) and (m11_km1<m11_km2)):
                tasks.append((E-2*dE, E))

            m11_km2 = m11_km1
            m11_km1 = m11_k
            E = E + dE
            if self.nE>0 and found == self.nE:
                break

        with ProcessPoolExecutor() as ex:
            results = list(ex.map(self._solve_root, tasks))

        energies, psis = zip(*results)
        return np.array(energies), list(psis)
                

