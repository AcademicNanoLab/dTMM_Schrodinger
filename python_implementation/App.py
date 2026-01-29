#
#   Using streamlit to create an online app
#

import sys
sys.path.append("/dTMM_Schrodinger/python_implementation/src")

import src.ConstAndScales
from src.Grid import Grid
from src.Visualiation import Visualisation
from src.Solvers_FDM import Parabolic_FDM, Taylor_FDM, Kane_FDM
from src.Solvers_TMM import Parabolic_TMM, Taylor_TMM, Kane_TMM, Ekenberg_TMM

import streamlit as st
import imageio.v2 as imageio
import numpy as np
import base64
import tempfile

class ElectronicStructureApp:
    def run(self):
        pg = st.navigation([self.Home, self.ES_Calculator, self.Animation_Sweep])
        pg.run()

    def Home(self):
        st.write("# Electronic Structure Calculator")
        st.write("### Select option using sidebar")

        col1, col2 = st.columns(2)
        with col1:
            st.write("Electronic Structure Calculator")
            st.image("matlab_implementation/src/optionPng.png")
        
        with col2:
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

        file, material, nstmax, solver, nonparabolicityType, dz, padding= set_options()
        K = st.number_input("K (kV/cm)", 0.0, 5.0, step=0.1, value = 1.9)

        solve = st.button("Calculate") 

        if solve:
            G = Grid(file, dz, material)
            G.set_K(K)

            Solver = SolverFactory.create(G, solver, nonparabolicityType, nstmax)

            [energies, psis] = Solver.get_wavefunctions()
            energies_meV = energies / src.ConstAndScales.E
            V = Visualisation(G, energies, psis)
            
            st.plotly_chart(V.plot_V_wf())
            st.plotly_chart(V.plot_energies())
            st.plotly_chart(V.plot_energy_diff_thz())
            st.plotly_chart(V.plot_QCL(K, padding, False, None))

    def Animation_Sweep(self):
        st.title("Electronic Structure Animation (Bias Sweep)")

        file, material, nstmax, solver, nonparabolicityType, dz, padding = set_options()

        c1, c2, c3 = st.columns(3)
        with c1:
            kmin = st.number_input("Kmin (kV/cm)", 0.0, 5.0, step=0.1, value =1.0)
        with c2:
            kmax = st.number_input("Kmax (kV/cm)", 0.0, 5.0, step=0.1, value =2.0)
        with c3:
            kstep = st.number_input("Step (kV/cm)", 0.0, 5.0, step=0.1, value = 0.5)

        st.write("Set Axis Limits")
        col1, col2, = st.columns(2)
        with col1:
            xmin = st.number_input("Xmin: ", 0, 3000, step=100, value=0)
            xmax = st.number_input("Xmax: ", 0, 3000, step=100, value=2000)
                
        with col2:
            ymin = st.number_input("Ymin: ", 0, 200, step=10, value=0)
            ymax = st.number_input("Ymax: ", 0, 200, step=10, value=120)

        solve = st.button("Calculate") 
        if solve:
            frames = []

            G = Grid(file, dz, material)
            k_values: list[float] = np.arange(kmin, kmax, kstep).tolist()
            for k in k_values:
                G.set_K(k)

                Solver = SolverFactory().create(G, solver, nonparabolicityType, nstmax)
                [energies, psis] = Solver.get_wavefunctions()
                V = Visualisation(G, energies, psis)
                axisLimits = [xmin, xmax, ymin, ymax]
                fig = V.plot_QCL(k, padding, True, axisLimits)

                with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
                    fig.write_image(tmp.name)
                    frames.append(imageio.imread(tmp.name))
            
            # write gif
            gif_path = tempfile.NamedTemporaryFile(delete=False, suffix=".gif").name
            imageio.mimsave(gif_path, frames, fps=4)

            # show in streamlit
            st.image(gif_path)


class SolverFactory:
    solver_map = {
        ("FDM", "Parabolic"): Parabolic_FDM,
        ("FDM", "Taylor"): Taylor_FDM,
        ("FDM", "Kane"): Kane_FDM,
        ("TMM", "Parabolic"): Parabolic_TMM,
        ("TMM", "Taylor"): Taylor_TMM,
        ("TMM", "Kane"): Kane_TMM,
        ("TMM", "Ekenberg"): Ekenberg_TMM,
    }

    @staticmethod
    def create(grid, solver, np_type, nstmax):
        return SolverFactory.solver_map[(solver, np_type)](grid, nstmax)

def set_options():
    st.markdown("### Select your options")

    file = st.file_uploader("Pick a file", type="TXT")

    tmp_path = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        if file is not None:
            tmp.write(file.getbuffer())
            tmp_path = tmp.name

    material = st.selectbox("Material", ["AlGaAs", "AlGaSb", "InGaAs_InAlAs", "InGaAs_GaAsSb"])
    solver = st.pills("Solver", ["FDM", "TMM"])

    np_options = ["Parabolic", "Taylor", "Kane", "Ekenberg"] if solver == "TMM" else ["Parabolic", "Taylor", "Kane"]
    np_type = st.radio("Non-parabolicity type", np_options, horizontal=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        nstmax = st.number_input("Nst max", 0, 20, value=10)
    with c2:
        dz = st.number_input("dz (Å)", 0, 2, value=1)
    with c3:
        pad = st.number_input("Padding (Å)", 0, 500)
    
    return tmp_path, material, nstmax, solver, np_type, dz, pad

app = ElectronicStructureApp()
app.run()
