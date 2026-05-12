import streamlit as st

class HomePage:
    def render(self):
        st.title("DTMM Schrödinger Calculator")
        st.write("### Select option using sidebar")

        col1, col2 = st.columns(2)

        with col1:
            st.write("Electronic Structure Calculator")
            st.image("matlab_implementation/src/optionPng.png")

        with col2:
            st.write("Transition Calculator")
            st.image("python_implementation/ui/TransitionCalc_Plot.png")