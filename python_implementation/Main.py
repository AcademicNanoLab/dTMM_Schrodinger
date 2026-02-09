#
#
#   Main.py file to test basic functionality.
#
#

import sys
sys.path.append("/dTMM_Schrodinger/python_implementation/src")

import src.ConstAndScales
from src.Grid import Grid
from src.Composition import Composition
from src.Visualiation import Visualisation
from src.Solvers_FDM import Parabolic_FDM, Taylor_FDM, Kane_FDM
from src.Solvers_TMM import Parabolic_TMM, Taylor_TMM, Kane_TMM, Ekenberg_TMM

def main():
    layer_file = "test/Structure1_BTC_GaAs_AlGaAs.txt"
    material = "AlGaAs"
    K = 1.9
    nstmax = 10
    solver = "FDM"
    nonparabolicityType = "Parabolic"
    dz = 0.6
    padding=400

    arr = [
        [225, 0.1],
        [144, 0],
        [10, 0.1],
        [118, 0],
        [10, 0.1],
        [126, 0],
        [225, 0.1]
    ]

    C = Composition.from_file(layer_file)
    C2 = Composition.from_array(arr)
    G = Grid(C2, dz, material)
    G.set_K(K)

    if solver == "FDM":
        if nonparabolicityType == "Parabolic":
            Solver = Parabolic_FDM(G, nstmax)
        elif nonparabolicityType == "Taylor":
            Solver = Taylor_FDM(G, nstmax)
        elif nonparabolicityType == "Kane":
            Solver = Kane_FDM(G, nstmax)

    elif solver == "TMM":
        if nonparabolicityType == "Parabolic":
            Solver = Parabolic_TMM(G, nstmax)
        elif nonparabolicityType == "Taylor":
            Solver = Taylor_TMM(G, nstmax)
        elif nonparabolicityType == "Kane":
            Solver = Kane_TMM(G, nstmax)
        elif nonparabolicityType == "Ekenberg":
            Solver = Ekenberg_TMM(G, nstmax)

    [energies, psis] = Solver.get_wavefunctions()
    energies_meV = energies / src.ConstAndScales.E
    V = Visualisation(G, energies, psis)
    fig = V.plot_V_wf()
    fig.show()

    fig = V.plot_energies()
    fig.show()

    fig = V.plot_energy_diff_thz()
    fig.show()

    fig = V.plot_QCL(K, padding, False, None)
    fig.show()

if __name__ == "__main__":
    main()
