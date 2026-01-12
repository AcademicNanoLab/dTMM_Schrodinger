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
import base64
import tempfile

def Home():
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

def set_options(sweep=False):
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

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if sweep:
            kmin = st.number_input("Kmin (kV/cm)", 0.0, 5.0, step=0.1, value = 1)
            kmax = st.number_input("Kmax (kV/cm)", 0.0, 5.0, step=0.1, value = 2)
            kstep = st.number_input("Step (kV/cm)", 0.0, 5.0, step=0.1, value = 0.5)

            k_sweep = kmin, kmax, kstep

        else:
            k = st.number_input("K (kV/cm)", 0.0, 5.0, step=0.1, value = 1.9)

    with c2:
        nstmax = st.number_input("Nst max", 0, 20, value=10)
    with c3:
        dz = st.number_input("dz (Å)", 0, 2, value=1)
    with c4:
        pad = st.number_input("Padding (Å)", 0, 500)
    
    return tmp_path, material, k, nstmax, solver, np_type, dz, pad


def ES_Calculator():
    st.title("Electronic Structure Calculator")

    file, material, K, nstmax, solver, nonparabolicityType, dz, padding= set_options()

    solve = st.button("Calculate") 

    if solve:
        G = Grid(file, dz, material)
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
        
        st.plotly_chart(V.plot_V_wf())
        st.plotly_chart(V.plot_energies())
        st.plotly_chart(V.plot_energy_diff_thz())
        st.plotly_chart(V.plot_QCL(K, padding, False, None))

def Animation_Sweep():
    st.title("Electronic Structure Animation (Bias Sweep)")

    file, material, K, nstmax, solver, nonparabolicityType, dz, padding = set_options(sweep = True)

    st.write("Set Axis Limits")
    col1, col2, = st.columns(2)
    with col1:
        xmin = st.number_input("Xmin: ", 0, 3000, step=100)
        xmax = st.number_input("Xmax: ", 0, 3000, step=100)
            
    with col2:
        ymin = st.number_input("Ymin: ", 0, 200, step=10)
        ymax = st.number_input("Xmax: ", 0, 200, step=10)

    st.write("TODO: Complete Animation Sweep function.")

pg = st.navigation([Home, ES_Calculator, Animation_Sweep])
pg.run()
