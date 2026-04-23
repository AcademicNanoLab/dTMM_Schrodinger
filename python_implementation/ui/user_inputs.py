import streamlit as st
from src.Material import Material

class UserInputs:
    def __init__(self) -> None:
        self.material = None
        self.M = None
        self.solver = None
        self.nonparabolicity = None
        self.nstmax = None
        self.dz = None
        self.padding = None
        self.K = None

    def render_common_inputs(self):
        self.material = self.material_input()
        self.solver = self.solver_input()

        self.nonparabolicity = self.np_input(self.solver)

        c1, c2, c3 = st.columns(3)

        with c1:
            self.nstmax = self.nst_input()
        with c2:
            self.dz = self.dz_input()
        with c3:
            self.padding = self.padding_input()
        
        self.K = self.k_input()

    def material_input(self):
        choice = st.selectbox("Material", ["AlGaAs", "AlGaSb", "InGaAs_InAlAs", "InGaAs_GaAsSb"])
        self.M = Material(choice)
        return choice

    def solver_input(self):
        return st.pills("Solver", ["FDM", "TMM"])

    def np_input(self, solver_type):
        np_options = ["Parabolic", "Taylor", "Kane", "Ekenberg"] if solver_type == "TMM" else ["Parabolic", "Taylor", "Kane"]
        return st.radio("Non-parabolicity type", np_options, horizontal=True)

    def nst_input(self):
        return st.number_input("Nst max", 0, 20, value=10)

    def dz_input(self):
        return st.number_input("dz (Å)", 0, 2, value=1)

    def padding_input(self):
        return st.number_input("Padding (Å)", 0, 500, step=50)

    def k_input(self):
        return st.number_input("K (kV/cm)", 0.0, 5.0, step=0.1, value=1.9)

    def layer_input(self, input_type): 
        from src.Composition import Composition
        import pandas as pd

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
                width='stretch'
            )
            structure_layers = edited_df[["Thickness", "Alloy Profile"]].values.tolist()
            
            return Composition.from_array(structure_layers)
        
        elif input_type == "File":
            import tempfile
            file = st.file_uploader("Pick a file", type="TXT")
            
            if file is None:
                return None
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                if file is not None:
                    tmp.write(file.getbuffer())
                    structure_file = tmp.name

            return Composition.from_file(structure_file)


class CalculatorInputs(UserInputs):
    def render_calculator_inputs(self):
        layer_input_type = st.pills("File input or text input?", ["File", "Text"])
        self.composition = self.layer_input(layer_input_type)

        self.render_common_inputs()
    

class EnergyDiffInputs(UserInputs):
    def render_energy_diff_inputs(self):
        st.text("Base Composition")
        self.composition = self.layer_input("Text")
        
        self.render_common_inputs()

        ij = st.pills("Select energy levels to compare.", ["1", "2", "3", "4", "5"], selection_mode="multi")
        if ij:
            ijs = list(map(int, ij))
            if len(ijs) != 2:
                st.markdown(":red-badge[**Please select 2 energy levels.**]")

            self.i = max( ijs )
            self.j = min( ijs )
        
        self.sweep_param = st.pills("Choose sweep parameter: ", ["Sweep Well Width", "Sweep Barrier Height", "Sweep Both"])
        if self.sweep_param is not None:
            self.heights, self.widths = self.get_sweep_ranges(self.sweep_param)
        
    def get_sweep_ranges(self, graph_type):
        import numpy as np
        match graph_type:
            case "Sweep Well Width":
                st.text("Set ranges for width")
                w_start, w_end, w_step = self.range_well_width()

                widths = [i for i in range(w_start, w_end, w_step)]
                heights = [0.1]

            case "Sweep Barrier Height":
                st.text("Set ranges for height")
                h_start, h_end, h_step = self.range_barrier_height()
                
                heights = [j for j in np.arange(h_start, h_end, h_step)]
                widths = [90]
                
            case "Sweep Both":
                st.text("Set ranges for width and height")
                w_start, w_end, w_step = self.range_well_width()
                h_start, h_end, h_step = self.range_barrier_height()

                widths = [i for i in range(w_start, w_end, w_step)]
                heights = [j for j in np.arange(h_start, h_end, h_step)]
        
        return heights, widths

    def range_well_width(self):
        st.text("Width:")
        c1, c2, c3 = st.columns(3)
        with c1:
            w_start = st.number_input("Start", 5, 300, value=50, step=50)
        with c2:
            w_end = st.number_input("End", 5, 300, value=150, step=50)
        with c3:
            w_step = st.number_input("Step", 5, 100, value=10, step=10)
        return w_start, w_end, w_step

    def range_barrier_height(self):
        st.text("Height:")
        c1, c2, c3 = st.columns(3)
        with c1:
            h_start = st.number_input("Start", 0.0, 1.0, value=0.0, step=0.1)
        with c2:
            h_end = st.number_input("End", 0.0, 1.0, value=0.5, step=0.1)
        with c3:
            h_step = st.number_input("Step", 0.0, 1.0, value=0.1, step=0.01)
        return h_start, h_end, h_step