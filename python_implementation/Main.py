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
from src.Visualisation import Visualisation
from src.Solvers_FDM import SolverFactory
from src.Material import Material

def main():
    layer_file = "test/Structure1_BTC_GaAs_AlGaAs.txt"
    # layer_file = "test/Structure2_LO_InGaAs_InAlAs.txt"
    # layer_file = "test/Structure3_LO_InGaAs_GaAsSb.txt"
    material = "AlGaAs"
    K = 8
    nstmax = 5
    solver = "FDM"
    nonparabolicityType = "Parabolic"
    dz = 0.6
    padding=400
    dz_vals = [2, 1, 0.7, 0.5, 0.2]
    arr = [
        [225, 0.2],
        [200, 0],
        [225, 0.2]
    ]

    # C = Composition.from_file(layer_file)
    C = Composition.from_array(arr)

    # -------- test time -------- #
    # import timeit
    # print("TMM, simple arr, 40 iterations, parallelised bisect finding")
    # get_wfs_times = []
    # for dz in dz_vals:
    #     print("\ndz: ", dz)
    #     G = Grid(C, dz, material)
    #     G.set_K(K)

    #     Solver = SolverFactory.create(G, solver, nonparabolicityType, nstmax)
    #     energies, psis = Solver.get_wavefunctions()

    #     t = timeit.repeat(lambda: Solver.get_wavefunctions(), repeat=2, number=1)
    #     print("get_wavefunctions", min(t))  # best timing
    #     get_wfs_times.append(min(t))

    # print("full times list:", get_wfs_times)

    # -------- test energies -------- #
    # nps = ["Parabolic", "Kane", "Taylor"]
    # for np in nps:
    #     G = Grid(C, dz, material)
    #     G.set_K(K)

    #     Solver = SolverFactory.create(G, solver, np, nstmax)
    #     [energies, psis] = Solver.get_wavefunctions()
    #     energies_meV = energies / src.ConstAndScales.meV
    #     energy_table_comparison(np, energies_meV)

    # -------- plot graphs -------- #
    G = Grid(C, dz, material)
    G.set_K(K)

    Solver = SolverFactory.create(G, solver, nonparabolicityType, nstmax)
    [energies, psis] = Solver.get_wavefunctions()
    energies_meV = energies / src.ConstAndScales.meV

    V = Visualisation(G, energies, psis)
    fig = V.plot_V_wf()
    fig.show()

    # fig = V.plot_energies()
    # fig.show()

    # fig = V.plot_energy_diff_thz()
    # fig.show()

    # fig = V.plot_QCL(K, padding, False, None)
    # fig.show()

    # -------- plot energy differences ------- #
    # from src.Parameters import InputParameters
    # IP = InputParameters(C, material, solver, nonparabolicityType, nstmax, dz, padding)
    # fig = plot_E2E1_diff(90, 100, 10, IP, K)
    # fig = plot_E2E1_diff(50, 200, 10, IP, K)
    # fig.show()

def plot_E2E1_diff(start, end, inc, IP, K):
    fig = go.Figure()

    M = Material(IP.material)
    c_band_offset = 100 # meV
    x = ( c_band_offset * src.ConstAndScales.meV / src.ConstAndScales.E) / M.V.barr

    x_axis = []
    E1_list = []
    E2_list = []
    E3_list = []
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
        print(i, len(energies_meV), energies_meV)
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
        xaxis=dict(
            title=dict(
                text='Width [Å]',
                font=dict(size=24)
            ),
            tickfont=dict(size=24)
        ),
        yaxis=dict(
            title=dict(
                text='Energy [meV]',
                font=dict(size=24)
            ),
            tickfont=dict(size=24)
        ),
        title=dict(
            text='Energy levels in a GaAs single quantum well, with constant effective mass',
            font=dict(size=28)
        )
    )
    fig.show()
    return fig

def energy_table_comparison(np, energies_meV):
    file_path = "test/St3_FDM.csv"
    import csv
    import os
    # Create header if file doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Level", np])
            for i, e in enumerate(energies_meV, start=1):
                writer.writerow([f"E{i} [meV]", f"{e:.4f}"])
    else:
        # Read existing data
        with open(file_path, mode="r", newline="") as f:
            rows = list(csv.reader(f))

        # Add new column header
        rows[0].append(np)

        # Add corresponding energy values
        for i, e in enumerate(energies_meV, start=1):
            if i < len(rows):
                rows[i].append(f"{e:.4f}")
            else:
                rows.append([f"E{i} [meV]", f"{e:.4f}"])

        # Write updated data back
        with open(file_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

if __name__ == "__main__":
    main()