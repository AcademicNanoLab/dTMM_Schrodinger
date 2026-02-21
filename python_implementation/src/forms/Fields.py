import streamlit as st
import pandas as pd

def material_input():
    return st.selectbox("Material", ["AlGaAs", "AlGaSb", "InGaAs_InAlAs", "InGaAs_GaAsSb"])

def solver_input():
    return st.pills("Solver", ["FDM", "TMM"])

def np_input(solver_type):
    np_options = ["Parabolic", "Taylor", "Kane", "Ekenberg"] if solver_type == "TMM" else ["Parabolic", "Taylor", "Kane"]
    return st.radio("Non-parabolicity type", np_options, horizontal=True)

def nst_input():
    return st.number_input("Nst max", 0, 20, value=10)

def dz_input():
    return st.number_input("dz (Å)", 0, 2, value=1)

def padding_input():
    return st.number_input("Padding (Å)", 0, 500, step=50)

def layer_input(input_type):
    from src.Composition import Composition

    structure_layers = None
    structure_file = None

    if input_type == "Text":

        default_layers = pd.DataFrame({
            "Thickness": [200, 100, 200],
            "Alloy Profile": [0.1, 0, 0.1],
        })

        edited_df = st.data_editor(
            default_layers,
            num_rows="dynamic",
            use_container_width=True
        )
        structure_layers = edited_df[["Thickness", "Alloy Profile"]].values.tolist()
        C = Composition.from_array(structure_layers)
        return C
    
    elif input_type == "File":
        import tempfile
        file = st.file_uploader("Pick a file", type="TXT")
        
        if structure_file is None:
            return None
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            if file is not None:
                tmp.write(file.getbuffer())
                structure_file = tmp.name
        C = Composition.from_file(structure_file)

        return C

def range_well_width():
    c1, c2, c3 = st.columns(3)
    st.text("Width:")
    with c1:
        w_start = st.number_input("Start", 5, 300, value=50, step=50)
    with c2:
        w_end = st.number_input("End", 5, 300, value=150, step=50)
    with c3:
        w_step = st.number_input("Step", 5, 100, value=10, step=10)
    return w_start, w_end, w_step

def range_barrier_height():
    c1, c2, c3 = st.columns(3)
    st.text("Height:")
    with c1:
        h_start = st.number_input("Start", 0, 1, value=50, step=50)
    with c2:
        h_end = st.number_input("End", 0, 1, value=150, step=50)
    with c3:
        h_step = st.number_input("Step", 0.1, 1, value=10, step=10)
    return h_start, h_end, h_step

def range_k():
    c1, c2, c3 = st.columns(3)
    with c1:
        kmin = st.number_input("Kmin (kV/cm)", 0.0, 5.0, step=0.1, value =1.0)
    with c2:
        kmax = st.number_input("Kmax (kV/cm)", 0.0, 5.0, step=0.1, value =2.0)
    with c3:
        kstep = st.number_input("Step (kV/cm)", 0.0, 5.0, step=0.1, value = 0.5)

    return kmin, kmax, kstep

def axis_limits():
    st.write("Set Axis Limits")
    col1, col2, = st.columns(2)
    with col1:
        xmin = st.number_input("Xmin: ", 0, 3000, step=100, value=0)
        xmax = st.number_input("Xmax: ", 0, 3000, step=100, value=2000)
            
    with col2:
        ymin = st.number_input("Ymin: ", 0, 200, step=10, value=0)
        ymax = st.number_input("Ymax: ", 0, 200, step=10, value=120)
    
    return xmin, xmax, ymin, ymax