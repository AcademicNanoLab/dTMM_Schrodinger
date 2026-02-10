#
#
#

from typing import Self
import numpy as np

class Composition:
    def __init__(self, layer_thickness, alloy_profile) -> None:
        self.layer_thickness = layer_thickness
        self.alloy_profile = alloy_profile

    @classmethod
    def from_file(cls, filepath) -> Self:
        layer_thickness = []
        alloy_profile = []

        with open(filepath, "r") as f:
            for line in f:
                if line.strip():
                    values = line.split()
                    x, y = float(values[0]), float(values[1])
                    layer_thickness.append(x)
                    alloy_profile.append(y)

        return cls(layer_thickness, alloy_profile)
    
    @classmethod
    def from_array(cls, layer_array):
        # for array input of shape [x, y]
        arr = np.asarray(layer_array)
        layer_thickness = arr[:, 0]
        alloy_profile = arr[:, 1]
        
        return cls(layer_thickness, alloy_profile)
    
    def get_alloy_profile(self):
        return self.alloy_profile
    
    def get_layer_thickness(self):
        return self.layer_thickness

