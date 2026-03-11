import streamlit as st
from .fields import *

def solve_structure(IP, K):
    from src.Grid import Grid
    from src.Solvers_FDM import SolverFactory

    G = Grid(IP.composition, IP.dz, IP.material)
    G.set_K(K)

    solver = SolverFactory.create(G, IP.solver, IP.np_type, IP.nst_max)
    energies, psis = solver.get_wavefunctions()

    return G, energies, psis

def set_options():
    layer_input_type = st.pills("File input or text input?", ["File", "Text"])
    composition = layer_input(layer_input_type)

    material = material_input()
    solver = solver_input()

    nonparabolicity = np_input(solver)

    c1, c2, c3 = st.columns(3)

    with c1:
        nstmax = nst_input()
    with c2:
        dz = dz_input()
    with c3:
        pad = padding_input()
    
    from src.Parameters import InputParameters
    Params = InputParameters(composition, material, solver, nonparabolicity, nstmax, dz, pad)

    return Params