#
#   Using streamlit to create an online app
#
import streamlit as st
import sys

sys.path.append("/dTMM_Schrodinger/python_implementation/ui")

from ui.home import HomePage
from ui.calculator import CalculatorPage
from ui.energy_diff import EnergyDifferencePage

class ElectronicStructureApp:
    def run(self):
        calculator_page = st.Page(CalculatorPage().render, title="Calculator", url_path="calculator")
        transition_page = st.Page(EnergyDifferencePage().render, title="Transition Calculator", url_path="transition-calculator")
        home_page = st.Page(HomePage(calculator_page, transition_page).render, title="Home", url_path="home")
        
        pages = [home_page, calculator_page, transition_page]
        pg = st.navigation(list(pages))
        pg.run()

st.set_page_config(layout="centered")
app = ElectronicStructureApp()
app.run()
