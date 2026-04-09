import streamlit as st

class CalculatorPage:
    def render(self):
        st.title("Electronic Structure Calculator")

        from src.Visualisation import Visualisation
        from ui.user_inputs import CalculatorInputs

        Inputs = CalculatorInputs()
        Inputs.render_calculator_inputs()

        if Inputs.solver is None or Inputs.composition is None:
            st.markdown(":red-badge[**<Calculate> button only appears once all fields are filled.**]")

        else:
            if st.button("Calculate"):
                from src.Grid import Grid
                from src.Solvers_FDM import SolverFactory

                # setup for calculation
                G = Grid(Inputs.composition, Inputs.dz, Inputs.material)
                G.set_K(Inputs.K)

                # get solver outputs: energies, psis
                solver = SolverFactory.create(G, Inputs.solver, Inputs.nonparabolicity, Inputs.nstmax)
                energies, psis = solver.get_wavefunctions()

                # plot graphs using plotly
                V = Visualisation(G, energies, psis)

                st.plotly_chart(V.plot_V_wf())
                st.plotly_chart(V.plot_energies())
                st.plotly_chart(V.plot_energy_diff_thz())
                st.plotly_chart(V.plot_QCL(Inputs.K, Inputs.padding, False, None)) # type: ignore
