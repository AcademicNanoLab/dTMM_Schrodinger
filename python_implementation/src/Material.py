#
# Material class containing parameters of material system typically used
# for muliple quantum well structures. Units are chosen as typically given
# in literature, the Grid class converts them to SI units for further use
# by the solvers.

from dataclasses import dataclass
import numpy as np

import ConstAndScales

@dataclass
class Parameter:
    well: float
    barr: float

class Material:
    def __init__(self, HeterostructureMaterial):
        if HeterostructureMaterial == "AlGaAs":
            self.set_AlGaAs()
        elif HeterostructureMaterial == "AlGaSb":
            self.set_AlGaSb()
        elif HeterostructureMaterial == "InGaAs_InAlAs":
            self.set_InGaAs_InAlAs()
        elif HeterostructureMaterial == "InGaAs_GaAsSb":
            self.set_InGaAs_GaAsSb()

    def set_AlGaAs(self):
        self.m   = Parameter(well=0.067, barr=0.15)
        self.Eg  = Parameter(well=1.424, barr=2.777)
        self.Egp = Parameter(well=4.48,  barr=4.55)
        self.d0  = Parameter(well=0.341, barr=0.3)
        self.P   = Parameter(well=9.88,  barr=8.88)
        self.Q   = Parameter(well=8.68,  barr=8.07)
        self.V   = Parameter( well=0.0,  barr=0.67*(self.Eg.barr - self.Eg.well))

    def set_AlGaSb(self):
        self.m   = Parameter(well=0.041,  barr=0.12)
        self.Eg  = Parameter(well=0.81,   barr=1.7)
        self.Egp = Parameter(well=3.11,   barr=3.53)
        self.d0  = Parameter(well=0.76,   barr=0.67)
        self.P   = Parameter(well=9.69,   barr=8.57)
        self.Q   = Parameter(well=8.25,   barr=7.8)
        self.V   = Parameter(well=0.0,    barr=0.55*(self.Eg.barr - self.Eg.well))

    def set_InGaAs_InAlAs(self):
        self.m   = Parameter(well=0.043,  barr=0.075)
        self.Eg  = Parameter(well=0.8161, barr=1.5296)
        self.Egp = Parameter(well=4.508,  barr=4.514)
        self.d0  = Parameter(well=0.3617, barr=0.3416)
        self.P   = Parameter(well=9.4189, barr=8.9476)
        self.Q   = Parameter(well=8.1712, barr=7.888)
        self.V   = Parameter(well=0.0,    barr=0.73*(self.Eg.barr - self.Eg.well))

    def set_InGaAs_GaAsSb(self):
        self.m   = Parameter(well=0.043,   barr=0.045)
        self.Eg  = Parameter(well=0.8161,  barr=1.1786)
        self.Egp = Parameter(well=4.508,   barr=3.8393)
        self.d0  = Parameter(well=0.3617,  barr=0.39637)
        self.P   = Parameter(well=9.4189,  barr=9.7869)
        self.Q   = Parameter(well=8.1712,  barr=8.4693)
        self.V   = Parameter(well=0.0,     barr=1*(self.Eg.barr - self.Eg.well))

    def get_alpha0g(self, x):
        Eg_alloy = self.interpolate_parameter(x, self.Eg)
        Egp_alloy = self.interpolate_parameter(x,self.Egp)
        d0_alloy = self.interpolate_parameter(x,self.d0)
        P_alloy = self.interpolate_parameter(x,self.P)
        Q_alloy = self.interpolate_parameter(x,self.Q)
        
        E0_alloy=Egp_alloy-Eg_alloy
        ksi_alloy=P_alloy**4/9/Eg_alloy**3/(Eg_alloy+d0_alloy)**2
        hi_alloy=P_alloy**2*Q_alloy**2/9/E0_alloy/Eg_alloy**2/(Eg_alloy+d0_alloy)**2

        alpha0golubov=-ksi_alloy*(3*Eg_alloy**2+4*Eg_alloy*d0_alloy+2*d0_alloy**2)*(3*Eg_alloy+2*d0_alloy)/(Eg_alloy+d0_alloy)-2*hi_alloy*d0_alloy**2
        beta0golubov=-12*hi_alloy*(3*Eg_alloy**2+4*Eg_alloy*d0_alloy+d0_alloy**2)

        return alpha0golubov, beta0golubov
    
    def get_alpha0gp(self, x):
        m_alloy = self.interpolate_parameter(x, self.m)
        alpha0g, beta0g = self.get_alpha0g(x)

        e = ConstAndScales.E
        A = ConstAndScales.ANGSTROM
        hbar = ConstAndScales.HBAR
        u0 = hbar / ConstAndScales.m0

        alpha0golubobp=-(2*m_alloy*e*A**2/hbar/u0)**2*alpha0g;    # ev^-1 
        beta0golubovp=-(2*m_alloy*e*A**2/hbar/u0)**2*beta0g;      # ev^-1
    
        return alpha0golubobp, beta0golubovp
    
    def get_alpha_kane(self, x):
        Eg_alloy = self.interpolate_parameter(x, self.Eg)
        alpha = 1/ np.asarray(Eg_alloy, dtype=np.float32)      # assumes element-wise division 

        return alpha
            
    def interpolate_parameter(self, x, param: Parameter):
        return param.well + x *(param.barr - param.well)

# a = input("material: ")
# b = Material(a)
# print(b.Eg.well)