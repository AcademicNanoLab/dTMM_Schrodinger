import streamlit as st

class HomePage:
    def __init__(self, calculator_page, transition_page) -> None:
        self.calculator_page = calculator_page
        self.transition_page = transition_page
        
    def render(self):
        st.title("DTMM Schrödinger Calculator")
        st.write("### Select Calculator Option")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Electronic Structure Calculator", icon=":material/link:"):
                st.switch_page(self.calculator_page)
            
            st.image("python_implementation/ui/Bandstructure_Plot.png")

        with col2:
            if st.button("Transition Calculator", icon=":material/link:"):
                st.switch_page(self.transition_page)
            st.image("python_implementation/ui/TransitionCalc_Plot.png")