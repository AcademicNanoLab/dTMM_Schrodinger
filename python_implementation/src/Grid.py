# Structure grid object that sets up a multiple quantum well system defined in
# the corresponding <layers.txt> file.
# 
# This class generates:
# - The x-axis
# - Bandstructure potential profile
# - Effective mass profile
# - Nonparabolicity parameter profile
#
# These profiles are generated through interpolation of material system
# parameters that define wells and barriers. Interpolation is assumed to be
# linear, depending on the fraction of dopant material in the system.

# from local
from src import ConstAndScales
from src import Material

# from libraries
import numpy as np

class Grid:
    def __init__(self, composition, dz, HeterostructureMaterial):
        # self.filename = filename
        # layer_thickness, alloy_profile = self.extract_thickness_composition()
        layer_thickness = composition.get_layer_thickness()
        alloy_profile = composition.get_alloy_profile()
        
        self.dz = dz*ConstAndScales.ANGSTROM
        self.z = np.arange(0, np.sum(layer_thickness) + dz, dz)     # Check if dz is necessary in layer thickness + dz.
        self.nz = np.size(self.z)
        self.material = Material.Material(HeterostructureMaterial)

        # Find the cumulative sum of the thickness of each layer and append to x.
        self.x = [0] * self.nz
        layer = 0                               # NOTE: 0 indexing instead of 1
        cum_sum = layer_thickness[layer]
        for i in range(self.nz):
            if (self.z[i] >= cum_sum) and (layer < len(layer_thickness)-1):
                layer += 1
                cum_sum = cum_sum + layer_thickness[layer]
            self.x[i] = alloy_profile[layer]
        
        self.z = self.z*ConstAndScales.ANGSTROM
        self.K = 0
        self.dE = 0.05e-3

    # Set methods
    def set_K(self, val):
        self.K = val

    def set_dE(self, val):
        self.dE = val
    
    def get_K(self):
        return self.K / ConstAndScales.kVcm
    
    def get_nz(self):
        return self.nz
    
    def get_dz(self):
        return self.dz
    
    def get_z(self):
        return self.z
    
    def get_zj(self, j):
        return self.z[j]
    
    def get_x(self):
        return self.x
    
    def get_dE(self):
        return self.dE *ConstAndScales.E
    
    def get_Vmax(self, K):
        return ConstAndScales.E *(max(self.x)*self.material.V.barr + max(self.z) * K * ConstAndScales.kVcm)

    def get_bandstructure_potential(self):      # assuming K in kV/cm
        V = np.zeros(self.nz)
        for i in range(self.nz):
            V[i] = ConstAndScales.E *self.material.interpolate_parameter(self.x[i], self.material.V)
        
        V = V - ConstAndScales.E * self.K * ConstAndScales.kVcm * self.z
        V = V - np.min(V)       # Applying bias will create negative potential, 
                                # so we offset this so that the lowest energy is 0
        return V
    
    # Get effective mass profile vs z
    def get_effective_mass(self):
        m = np.zeros(self.nz)
        for i in range(self.nz):
            m[i] = ConstAndScales.m0 * self.material.interpolate_parameter(self.x[i], self.material.m)
        return m
    
    def get_alpha_kane(self):
        alpha = np.zeros(self.nz)
        for i in range(self.nz):
            alpha[i] = self.material.get_alpha_kane(self.x[i]) / ConstAndScales.E
        return alpha
    
    def get_alphap_ekenberg(self):
        alphap = np.zeros(self.nz)
        for i in range(self.nz):
            alpha0gp, beta0gp = self.material.get_alpha0gp(self.x[i])
            alphap[i] = alpha0gp / ConstAndScales.E    # NOTE: assumed we're using only alpha0gp here?
        return alphap