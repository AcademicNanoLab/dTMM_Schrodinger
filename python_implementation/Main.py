#
#
#   Main.py file to test basic functionality.
#
#

import sys

import src.Material
sys.path.append("/dTMM_Schrodinger/python_implementation/src")

import plotly.graph_objects as go
import numpy as np

import src.ConstAndScales
from src.Grid import Grid
from src.Composition import Composition
from src.Visualisation import Visualisation
from src.Solvers_FDM import SolverFactory
from src.Material import Material

def main():
    layer_file = "test/Structure1_BTC_GaAs_AlGaAs.txt"
    material = "AlGaAs"
    K = 0.1
    nstmax = 10
    solver = "FDM"
    nonparabolicityType = "Parabolic"
    dz = 0.6
    padding=100

    from src.Parameters import InputParameters
    arr = [
        [225, 0.2],
        [200, 0],
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
    # fig = V.plot_V_wf()
    # fig.show()

    # fig = V.plot_wavefunction()
    # fig.show()

    # fig = V.plot_energies()
    # fig.show()

    # fig = V.plot_energy_diff_thz()
    # fig.show()

    # fig = V.plot_QCL(K, padding, False, None)
    # fig.show()
    
    fig = plot_E2E1_diff(90, 100, 10, IP, K)
    # fig = plot_E2E1_diff(50, 200, 10, IP, K)
    # fig.show()

def plot_E2E1_diff(start, end, inc, IP, K):
    fig = go.Figure()

    M = Material(IP.material)
    c_band_offset = 100 # meV
    x = ( c_band_offset * src.ConstAndScales.meV / src.ConstAndScales.E) / M.V.barr

    # for j in np.arange(0.30, 0.40, 0.05):
    x_axis = []
    E1_list = []
    E2_list = []
    E3_list = []
    # print(f"Calculating for height = {x:.2f}")
    for i in range(10, 210, 10):
        x_axis.append(i)
        arr = [
            [225, x],
            [i, 0],
            [225, x]
        ]

        # C = Composition.from_file(layer_file)
        C2 = Composition.from_array(arr)
        G = Grid(C2, IP.dz, IP.material)
        G.set_K(K)

        Solver = SolverFactory.create(G, IP.solver, IP.np_type, IP.nst_max)

        [energies, psis] = Solver.get_wavefunctions()
        energies_meV = energies / src.ConstAndScales.meV

        if len(energies_meV) > 2:
            E1_list.append(energies_meV[0])
            E2_list.append(energies_meV[1])
            E3_list.append(energies_meV[2])
        elif len(energies_meV) > 1:
            E1_list.append(energies_meV[0])
            E2_list.append(energies_meV[1])
            E3_list.append(None)
        elif len(energies_meV) > 0:
            E1_list.append(energies_meV[0])
            E2_list.append(None)
            E3_list.append(None)
        else:
            E1_list.append(None)
            E2_list.append(None)
            E3_list.append(None)
            

        # print(energies_meV)
    fig.add_trace(go.Scatter(x=x_axis, y=E1_list, mode='lines+markers', name=f'E1 (x={x:.2f})'))
    fig.add_trace(go.Scatter(x=x_axis, y=E2_list, mode='lines+markers', name=f'E2 (x={x:.2f})'))
    fig.add_trace(go.Scatter(x=x_axis, y=E3_list, mode='lines+markers', name=f'E3 (x={x:.2f})'))

    fig.update_layout(
        xaxis_title = 'Width (Angstrom)',
        yaxis_title = 'Energy (meV)',
        title = 'Energy levels in a GaAs single quantum well, with constant effective mass'
    )
    fig.show()
    return fig

if __name__ == "__main__":
    main()
