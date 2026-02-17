#
#   Class to store all user-initialised parameters
#

class InputParameters:
    def __init__(self, structure_layers, structure_file, material, solver, np_type, nst_max, dz, padding):
        self.material = material
        self.solver = solver
        self.np_type = np_type
        self.nst_max = nst_max
        self.dz = dz
        self.padding = padding

        self.structure_layers = structure_layers
        self.structure_file = structure_file
        # self.composition = self.set_composition()

    def set_composition(self):
        from src.Composition import Composition
        if self.structure_layers is not None:
            C = Composition.from_array(self.structure_layers)
        elif self.structure_file is not None:
            C = Composition.from_file(self.structure_file)
        return C