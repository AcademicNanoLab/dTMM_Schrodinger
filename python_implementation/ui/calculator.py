import streamlit as st

class CalculatorPage:
    def render(self):
        st.title("Electronic Structure Calculator")

        from src.Visualisation import Visualisation
        from ui.solver_service import solve_structure, set_options
        IP = set_options()
        K = st.number_input("K (kV/cm)", 0.0, 5.0, step=0.1, value=1.9)

        if IP.solver is None or IP.composition is None:
            st.markdown(":red-badge[**<Calculate> button only appears once all fields are filled.**]")

        else:
            if st.button("Calculate"):

                G, energies, psis = solve_structure(IP, K)
                V = Visualisation(G, energies, psis)

                st.plotly_chart(V.plot_V_wf())
                st.plotly_chart(V.plot_energies())
                st.plotly_chart(V.plot_energy_diff_thz())
                st.plotly_chart(V.plot_QCL(K, IP.padding, False, None))
