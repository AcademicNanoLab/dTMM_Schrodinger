#
#   Using streamlit to create an online app
#
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

import sys
sys.path.append("/dTMM_Schrodinger/python_implementation/src")
from src.Fields import *

class ElectronicStructureApp:
    def run(self):
        pg = st.navigation([self.Home, self.ES_Calculator, self.Animation_Sweep, self.Energy_Difference])
        pg.run()

    def Home(self):
        st.write("# Electronic Structure Calculator")
        st.write("### Select option using sidebar")

        col1, col2 = st.columns(2)
        with col1:
            st.write("Electronic Structure Calculator")
            st.image("matlab_implementation/src/optionPng.png")
        
        with col2:
            import base64
            st.write("Electronic Structure Animation (Bias Sweep)")

            file_ = open("matlab_implementation/src/optionGif.gif", "rb")
            contents = file_.read()
            data_url = base64.b64encode(contents).decode("utf-8")
            file_.close()

            st.markdown(
                f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
                unsafe_allow_html=True,
            )    

    def ES_Calculator(self):
        st.title("Electronic Structure Calculator")

        IP = set_options()
        K = st.number_input("K (kV/cm)", 0.0, 5.0, step=0.1, value = 1.9)

        solve = st.button("Calculate") 

        if solve:
            from src.Grid import Grid
            from src.Visualiation import Visualisation
            from src.Solvers_FDM import SolverFactory
            
            G = Grid(IP.composition, IP.dz, IP.material)
            G.set_K(K)

            Solver = SolverFactory.create(G, IP.solver, IP.np_type, IP.nst_max)

            [energies, psis] = Solver.get_wavefunctions()
            V = Visualisation(G, energies, psis)
            
            st.plotly_chart(V.plot_V_wf())
            st.plotly_chart(V.plot_energies())
            st.plotly_chart(V.plot_energy_diff_thz())
            st.plotly_chart(V.plot_QCL(K, IP.padding, False, None))

    def Animation_Sweep(self):
        st.title("Electronic Structure Animation (Bias Sweep)")

        IP = set_options()

        kmin, kmax, kstep = range_k()
        xmin, xmax, ymin, ymax = axis_limits()

        solve = st.button("Calculate") 
        if solve:
            from src.Grid import Grid
            from src.Solvers_FDM import SolverFactory
            from src.Visualiation import Visualisation
            import imageio.v2 as imageio
            import tempfile
            frames = []

            G = Grid(IP.composition, IP.dz, IP.material)
            k_values: list[float] = np.arange(kmin, kmax, kstep).tolist()
            for k in k_values:
                G.set_K(k)

                Solver = SolverFactory().create(G, IP.solver, IP.np_type, IP.nst_max)
                [energies, psis] = Solver.get_wavefunctions()
                V = Visualisation(G, energies, psis)
                axisLimits = [xmin, xmax, ymin, ymax]
                fig = V.plot_QCL(k, IP.padding, True, axisLimits)

                with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
                    fig.write_image(tmp.name)
                    frames.append(imageio.imread(tmp.name))
            
            # write gif
            gif_path = tempfile.NamedTemporaryFile(delete=False, suffix=".gif").name
            imageio.mimsave(gif_path, frames, fps=4)

            # show in streamlit
            st.image(gif_path)

    def Energy_Difference(self):
        from src.Grid import Grid
        from src.Solvers_FDM import SolverFactory
        from src.Composition import Composition
        from src.Parameters import InputParameters
        import src.ConstAndScales

        st.title("Energy Difference Plots")

        # composition = layer_input("Text")    
        material = material_input()
        solver = solver_input()
        nonparabolicity = np_input(solver)

        c1, c2, c3 = st.columns(3)

        with c1:
            nst_max = nst_input()
        with c2:
            dz = dz_input()
        with c3:
            pad = padding_input()
        
        K = st.number_input("K (kV/cm)", 0.0, 5.0, step=0.1, value = 1.9)

        st.text("Set ranges for width and height")
        w_start, w_end, w_step = range_well_width()
        
        ### Calculate
        solve_width = st.button("Sweep Barrier Width")
        solve_type = st.pills("Choose graph type: ", ["Sweep Well Width", "Sweep Barrier Height", "Sweep Both"]) 
        calculate = st.button("Calculate")
        if solve_width:
            fig = go.Figure()
            x_axis = []
            trace = []
            for i in range(w_start, w_end, w_step):
                arr = [
                    [225, 0.1],
                    [i, 0],
                    [225, 0.1]
                ]

                C2 = Composition.from_array(arr)
                IP = InputParameters(C2, material, solver, nonparabolicity, nst_max, dz, pad)
                G = Grid(C2, IP.dz, IP.material)
                G.set_K(K)

                Solver = SolverFactory.create(G, IP.solver, IP.np_type, IP.nst_max)

                [energies, _] = Solver.get_wavefunctions()
                energies_meV = energies / src.ConstAndScales.meV

                if len(energies) > 1:
                    # print(f"Energy_diff: @{j}, {energies_meV - energies_meV[0]:.2f}")
                    x_axis.append(i)
                    trace.append(energies_meV[1] - energies_meV[0])
            
            fig.add_trace(go.Scatter(
                x=x_axis,
                y=trace,
                mode='lines+markers',
                name=f"x = {i:.2f}"
            ))

            st.plotly_chart(fig)

        h_start, h_end, h_step = range_barrier_height()
        solve_height = st.button("Sweep Barrier Height") 

        if solve_height:
            fig = go.Figure()
            x_axis = []
            trace = []
            for j in np.arange(h_start, h_end, h_step):
                arr = [
                    [225, j],
                    [90, 0],
                    [225, j]
                ]

                C2 = Composition.from_array(arr)
                IP = InputParameters(C2, material, solver, nonparabolicity, nst_max, dz, pad)
                G = Grid(C2, IP.dz, IP.material)
                G.set_K(K)

                Solver = SolverFactory.create(G, IP.solver, IP.np_type, IP.nst_max)

                [energies, _] = Solver.get_wavefunctions()
                energies_meV = energies / src.ConstAndScales.meV

                if len(energies) > 1:
                    # print(f"Energy_diff: @{j}, {energies_meV - energies_meV[0]:.2f}")
                    x_axis.append(j)
                    trace.append(energies_meV[1] - energies_meV[0])
            
            fig.add_trace(go.Scatter(
                x=x_axis,
                y=trace,
                mode='lines+markers',
                name=f"x = {j:.2f}"
            ))

            st.plotly_chart(fig)
        
        # if solve_type == "Sweep Both":




def set_options():
    st.markdown("### Select your options")

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

app = ElectronicStructureApp()
app.run()
