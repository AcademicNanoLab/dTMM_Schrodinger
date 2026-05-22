import streamlit as st

class HomePage:
    def __init__(self, calculator_page, transition_page) -> None:
        self.calculator_page = calculator_page
        self.transition_page = transition_page
        
    def render(self):
        st.set_page_config(layout="wide")
        st.title("DTMM Schrödinger Calculator")
        st.write("### Select Calculator Option")

        col1, col2 = st.columns(2)

        with col1:
            tile1 = col1.container(border=True)
            if tile1.button("Electronic Structure Calculator", icon=":material/link:", use_container_width=True):
                st.switch_page(self.calculator_page)
            tile1.image("python_implementation/ui/Bandstructure_Plot.png")

        with col2:
            tile2 = col2.container(border=True)
            if tile2.button("Transition Calculator", icon=":material/link:", use_container_width=True):
                st.switch_page(self.transition_page)
            tile2.image("python_implementation/ui/TransitionCalc_Plot.png")