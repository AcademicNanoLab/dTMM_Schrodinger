#
#
#   Main.py file to test basic functionality.
#
#

import sys
sys.path.append("/dTMM_Schrodinger/python_implementation/src")

import plotly.graph_objects as go
import numpy as np

import src.ConstAndScales
from src.Grid import Grid
from src.Composition import Composition
from src.Visualiation import Visualisation
from src.Solvers_FDM import SolverFactory

def main():
    layer_file = "test/Structure1_BTC_GaAs_AlGaAs.txt"
    material = "AlGaAs"
    K = 5
    nstmax = 10
    solver = "TMM"
    nonparabolicityType = "Parabolic"
    dz = 0.6
    padding=100

    from src.Parameters import InputParameters
    arr = [
        [225, 0.2],
        [80, 0],
        [225, 0.2]
    ]

    # C = Composition.from_file(layer_file)
    C = Composition.from_array(arr)
    IP = InputParameters(C, material, solver, nonparabolicityType, nstmax, dz, padding)
    G = Grid(C, IP.dz, IP.material)
    G.set_K(K)

    Solver = SolverFactory.create(G, IP.solver, IP.np_type, IP.nst_max)
    [energies, psis] = Solver.get_wavefunctions()
    # energies_meV = energies / src.ConstAndScales.E

    V = Visualisation(G, energies, psis)
    fig = V.plot_V_wf()
    fig.show()

    # fig = V.plot_energies()
    # fig.show()

    # fig = V.plot_energy_diff_thz()
    # fig.show()

    # fig = V.plot_QCL(K, padding, False, None)
    # fig.show()
    
    # fig = plot_E2E1_diff(50, 200, 10, IP, K)
    # fig.show()

def plot_E2E1_diff(start, end, inc, IP, K):
    fig = go.Figure()
    for j in np.arange(0.15, 0.40, 0.05):
        x_axis = []
        trace = []
        print(f"Calculating for height = {j:.2f}")
        for i in range(start, end, inc):
            arr = [
                [225, j],
                [i, 0],
                [225, j]
            ]

            # C = Composition.from_file(layer_file)
            C2 = Composition.from_array(arr)
            G = Grid(C2, IP.dz, IP.material)
            G.set_K(K)

            Solver = SolverFactory.create(G, IP.solver, IP.np_type, IP.nst_max)

            [energies, psis] = Solver.get_wavefunctions()
            energies_meV = energies / src.ConstAndScales.meV

            if len(energies) > 1:
                print(f"Energy_diff: @{i}, {energies_meV[1] - energies_meV[0]:.2f}")
                x_axis.append(i)
                trace.append(energies_meV[1] - energies_meV[0])
        
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=trace,
            mode='lines+markers',
            name=f"x = {j:.2f}"
        ))

    fig.update_layout(
        title="(E2 - E1) vs. quantum well width",
        xaxis_title="Width (Å)",
        yaxis_title="Energy difference (meV)"
    )
    return fig

if __name__ == "__main__":
    main()
