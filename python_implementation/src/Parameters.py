#
#   Class to store all user-initialised parameters
#

class InputParameters:
    def __init__(self, composition, material, solver, np_type, nst_max, dz, padding):
        self.composition = composition
        self.material = material
        self.solver = solver
        self.np_type = np_type
        self.nst_max = nst_max
        self.dz = dz
        self.padding = padding