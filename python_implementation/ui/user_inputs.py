from abc import ABC, abstractmethod
import streamlit as st

class UserInputs(ABC):
    def __init__(self) -> None:
        self.material = None
        self.solver = None
        self.nonparabolicity = None
        self.nstmax = None
        self.dz = None
        self.padding = None

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

    def material_input(self):
        return st.selectbox("Material", ["AlGaAs", "AlGaSb", "InGaAs_InAlAs", "InGaAs_GaAsSb"])

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
    
    @abstractmethod
    def layer_input(self):
        pass

class CalculatorInputs(UserInputs):
    def __init__(self) -> None:
        super().__init__()

    def render_calculator_inputs(self):
        layer_input_type = st.pills("File input or text input?", ["File", "Text"])
        self.composition = self.layer_input(layer_input_type)

        self.render_common_inputs()
        self.K = self.k_input()

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
            C = Composition.from_array(structure_layers)
            return C
        
        elif input_type == "File":
            import tempfile
            file = st.file_uploader("Pick a file", type="TXT")
            
            if file is None:
                return None
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                if file is not None:
                    tmp.write(file.getbuffer())
                    structure_file = tmp.name
            C = Composition.from_file(structure_file)

            return C
    
    def k_input(self):
        return st.number_input("K (kV/cm)", 0.0, 5.0, step=0.1, value=1.9)
