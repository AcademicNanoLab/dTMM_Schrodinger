#
#   Using streamlit to create an online app
#
import streamlit as st
import sys

sys.path.append("/dTMM_Schrodinger/python_implementation/ui")

from ui.home import HomePage
from ui.calculator import CalculatorPage
from ui.energy_diff import EnergyDifferencePage
# from ui.animation import AnimationPage

class ElectronicStructureApp:
    def run(self):
        pages = [
            st.Page(HomePage().render, title="Home", url_path="home"),
            st.Page(CalculatorPage().render, title="Calculator", url_path="calculator"),
            st.Page(EnergyDifferencePage().render, title="Energy Difference", url_path="energy-difference"),
        ]
        pg = st.navigation(list(pages))
        pg.run()

app = ElectronicStructureApp()
app.run()

# @st.cache_resource
# def build_grid(IP: InputParameters, K):
#     from src.Grid import Grid
#     C = IP.set_composition()
#     G = Grid(C, IP.dz, IP.material)
#     G.set_K(K)
#     return G

# @st.cache_data
# def solve_structure(G, solver, np_type, nst):
#     from src.Solvers_FDM import SolverFactory
#     Solver = SolverFactory.create(G, solver, np_type, nst)
#     return Solver.get_wavefunctions()
