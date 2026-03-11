import streamlit as st
import base64

class HomePage:
    def render(self):
        st.title("DTMM Schrödinger Calculator")
        st.write("### Select option using sidebar")

        col1, col2 = st.columns(2)

        with col1:
            st.write("Electronic Structure Calculator")
            st.image("matlab_implementation/src/optionPng.png")

        with col2:
            st.write("Electronic Structure Animation (Bias Sweep)")

            with open("matlab_implementation/src/optionGif.gif", "rb") as f:
                contents = f.read()

            data_url = base64.b64encode(contents).decode("utf-8")

            st.markdown(
                f'<img src="data:image/gif;base64,{data_url}">',
                unsafe_allow_html=True,
            )