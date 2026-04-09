import numpy as np

class TransitionCalculator:
    def __init__(self) -> None:
        import src.ConstAndScales
        self.m_e = src.ConstAndScales.m0
        self.hbar = src.ConstAndScales.HBAR
        self.meV = src.ConstAndScales.meV
    
    def get_energy_diff(self, energies, i, j):
        if len(energies) < max(i, j):
            return None
        else:
            return energies[i-1] - energies[j-1]
    
    def get_dipole(self, z, psis, i, j):
        if len(psis) < max(i, j):
            return None

        psi_i = psis[i-1]
        psi_j = psis[j-1]

        dz = z[1] - z[0]

        integ=np.abs(psi_i)*np.abs(psi_i)
        temp=0
        for iz in range(1,len(z)):
            temp+= dz * (integ[iz-1]+integ[iz])/2

        integral=0
        integrand = psi_i * z * psi_j
        for iz in range(1,len(z)):
            integral+= dz * (integrand[iz-1]+integrand[iz])/2
        return abs(integral)
    
    def get_oscillator_strength(self, z, energies, psis, i,j):
        e_ij = self.get_energy_diff(energies, i,j)
        if e_ij is None:
            return None
        else:
            d_ij = self.get_dipole(z, psis, i,j)
            if d_ij is None:
                return None
            return (2*self.m_e / self.hbar**2) * e_ij * abs(d_ij)**2
    
    def calculate(self, z, energies, psis, i,j):
        e21 = self.get_energy_diff(energies, i,j)
        d21 = self.get_dipole(z, psis, i,j)
        f21 = self.get_oscillator_strength(z, energies, psis, i,j)
        return e21, d21, f21