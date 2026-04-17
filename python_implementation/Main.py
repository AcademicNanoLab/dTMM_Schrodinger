#
#
#   Main.py file to test basic functionality.
#
#

import sys
sys.path.append("/dTMM_Schrodinger/python_implementation/src")

import src.ConstAndScales
from src.Grid import Grid
from src.Visualisation import Visualisation
from src.Solvers_FDM import SolverFactory
from src.Composition import Composition

def main():
    layer_file = "test/Structure1_BTC_GaAs_AlGaAs.txt"
    material = "AlGaAs"
    K = 1.9
    nstmax = 10
    solver = "TMM"
    nonparabolicity = "Parabolic"
    dz = 0.6
    padding=400

    arr = [
        [225, 0.2],
        [80, 0.0],
        [225, 0.2]
    ]

    C = Composition.from_array(arr)
    G = Grid(C, dz, material)
    G.set_K(K)

    Solver = SolverFactory.create(G, solver, nonparabolicity, nstmax)

    [energies, psis] = Solver.get_wavefunctions()
    # print(Solver.get_matrix_j(2, 100))
    print("energies:", energies)
    energies_meV = energies / src.ConstAndScales.E
    V = Visualisation(G, energies, psis)
    fig = V.plot_V_wf()
    fig.show()

    fig = V.plot_energies()
    # fig.show()

    fig = V.plot_energy_diff_thz()
    # fig.show()

    fig = V.plot_QCL(K, padding, False, None)
    # fig.show()

if __name__ == "__main__":
    main()