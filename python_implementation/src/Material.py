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

@dataclass
class Material:
    m: Parameter        # Effective mass
    Eg: Parameter       # Bandgap (eV)
    Egp: Parameter      # L Valley bandgap (eV)
    d0: Parameter       # Spin-split bandgap (eV)
    P: Parameter        # P Kane parameter [eV A]
    Q: Parameter        # Q Kane parameter [eV A]
    V: Parameter        # Conduction band potential [eV]

    def get_alpha0g(self, x):
        Eg_alloy = self.interpolate_parameter(x, self.Eg)
        Egp_alloy = self.interpolate_parameter(x,self.Egp)
        d0_alloy = self.interpolate_parameter(x,self.d0)
        P_alloy = self.interpolate_parameter(x,self.P)
        Q_alloy = self.interpolate_parameter(x,self.Q)
        
        E0_alloy=Egp_alloy-Eg_alloy
        ksi_alloy=P_alloy^4/9/Eg_alloy^3/(Eg_alloy+d0_alloy)^2
        hi_alloy=P_alloy^2*Q_alloy^2/9/E0_alloy/Eg_alloy^2/(Eg_alloy+d0_alloy)^2

        alpha0golubov=-ksi_alloy*(3*Eg_alloy^2+4*Eg_alloy*d0_alloy+2*d0_alloy^2)*(3*Eg_alloy+2*d0_alloy)/(Eg_alloy+d0_alloy)-2*hi_alloy*d0_alloy^2
        beta0golubov=-12*hi_alloy*(3*Eg_alloy^2+4*Eg_alloy*d0_alloy+d0_alloy^2)

        return alpha0golubov, beta0golubov
    
    def get_alpha0gp(self, x):
        m_alloy = self.interpolate_parameter(x, self.m)
        alpha0g, beta0g = self.get_alpha0g(x)

        e = ConstAndScales.E
        A = ConstAndScales.ANGSTROM
        hbar = ConstAndScales.HBAR
        u0 = hbar / ConstAndScales.m0

        alpha0golubobp=-(2*m_alloy*e*A^2/hbar/u0)^2*alpha0g;    # ev^-1 
        beta0golubovp=-(2*m_alloy*e*A^2/hbar/u0)^2*beta0g;      # ev^-1
    
        return alpha0golubobp, beta0golubovp
    
    def get_alpha_kane(self, x):
        Eg_alloy = self.interpolate_parameter(x, self.Eg)
        alpha = 1/ np.asarray(Eg_alloy, dtype=np.float32)      # assumes element-wise division 

        return alpha
            
    def interpolate_parameter(self, x, param: Parameter):
        return param.well + x *(param.barr - param.well)

AlGaAs = Material(
    m   = Parameter(well=0.067, barr=0.15),
    Eg  = Parameter(well=1.424, barr=2.777),
    Egp = Parameter(well=4.48,  barr=4.55),
    d0  = Parameter(well=0.341, barr=0.3),
    P   = Parameter(well=9.88,  barr=8.88),
    Q   = Parameter(well=8.68,  barr=8.07),
    V   = Parameter( well=0.0,  barr=0.67*(2.777-1.424))  # 0.67*(Eg.barr - Eg.well)
)

AlGaSb = Material(
    m   = Parameter(well=0.041,  barr=0.12),
    Eg  = Parameter(well=0.81,   barr=1.7),
    Egp = Parameter(well=3.11,   barr=3.53),
    d0  = Parameter(well=0.76,   barr=0.67),
    P   = Parameter(well=9.69,   barr=8.57),
    Q   = Parameter(well=8.25,   barr=7.8),
    V   = Parameter(well=0.0,    barr=0.55*(1.7-0.81))  # 0.4845
)

InGaAs_InAlAs = Material(
    m   = Parameter(well=0.043,  barr=0.075),
    Eg  = Parameter(well=0.8161, barr=1.5296),
    Egp = Parameter(well=4.508,  barr=4.514),
    d0  = Parameter(well=0.3617, barr=0.3416),
    P   = Parameter(well=9.4189, barr=8.9476),
    Q   = Parameter(well=8.1712, barr=7.888),
    V   = Parameter(well=0.0,    barr=0.73*(1.5296-0.8161))  # 0.520657
)

InGaAs_GaAsSb = Material(
    m   = Parameter(well=0.043,   barr=0.045),
    Eg  = Parameter(well=0.8161,  barr=1.1786),
    Egp = Parameter(well=4.508,   barr=3.8393),
    d0  = Parameter(well=0.3617,  barr=0.39637),
    P   = Parameter(well=9.4189,  barr=9.7869),
    Q   = Parameter(well=8.1712,  barr=8.4693),
    V   = Parameter(well=0.0,     barr=1*(1.1786-0.8161))  # 0.3625
)

materials = {
    "AlGaAs": AlGaAs,
    "AlGaSb": AlGaSb,
    "InGaAs/InAlAs": InGaAs_InAlAs,
    "InGaAs/GaAsSb": InGaAs_GaAsSb
}

def get_material(HeterostructureMaterial) -> Material:
    if HeterostructureMaterial in materials:
        return materials[HeterostructureMaterial]
    else:
        print(f"\nInvalid Heterostructure Material '{HeterostructureMaterial}'\nExpected one of { list(materials.keys()) }\n")
        exit(0)

# a = input("material: ")
# b = get_material(a)
# print(b)