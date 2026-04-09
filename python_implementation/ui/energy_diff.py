import streamlit as st

class EnergyDifferencePage:
    def render(self):
        st.title("Energy Difference Plots")

        from src.Composition import Composition
        from src.Solvers_FDM import SolverFactory
        from src.Grid import Grid

        from .user_inputs import EnergyDiffInputs

        Inputs = EnergyDiffInputs()
        Inputs.render_energy_diff_inputs()

        ### Calculate
        import plotly.graph_objects as go
        from src.TransitionCalculator import TransitionCalculator
        fig = go.Figure()

        if None in (Inputs.solver, Inputs.composition, Inputs.sweep_param, Inputs.plot_diff):
            st.markdown(":red-badge[**<Calculate> button only appears once all fields are filled.**]")
        else:
            if st.button("Calculate"):
                progress_text = "Calculating. Please wait."
                pbar_val = 0
                p_bar = st.progress(pbar_val, text=progress_text)
                fig = go.Figure()
                height_fig = go.Figure()
                h_trace = []
                for h in Inputs.heights:
                    x_width = []
                    trace = []
                    for w in Inputs.widths:
                        arr = Inputs.composition.as_array() # type: ignore
                        arr[1][0] = w
                        arr[0][1] = h
                        arr[-1][1] = h

                        C2 = Composition.from_array(arr)
                        
                        # setup for calculation
                        G = Grid(C2, Inputs.dz, Inputs.material)
                        G.set_K(Inputs.K)

                        # get solver outputs: energies, psis
                        solver = SolverFactory.create(G, Inputs.solver, Inputs.nonparabolicity, Inputs.nstmax)
                        energies, wavefunctions = solver.get_wavefunctions()

                        i = 2
                        j = 1

                        T = TransitionCalculator()

                        ediff, dipoles, osc_str = T.calculate(G.z, energies, wavefunctions, i, j)
                        if None not in (ediff, dipoles, osc_str):
                            x_width.append(w)


                        if Inputs.plot_diff == "Energy Difference":
                            trace.append(T.get_energy_diff(energies, i,j))
                        elif Inputs.plot_diff == "Dipole matrix element":
                            tmp = T.get_dipole(G.z, wavefunctions, i,j)
                            if tmp is not None:
                                trace.append(tmp /1e-9)
                        elif Inputs.plot_diff == "Oscillator Strength":
                            trace.append(T.get_oscillator_strength(G.z, energies, wavefunctions, i,j))
                        x_width.append(w)

                        pbar_val += int(100/(len(Inputs.heights)*len(Inputs.widths)))
                        p_bar.progress(pbar_val, progress_text)
                        
                    if len(energies) > 1:
                        h_trace.append(energies[1] - energies[0])

                    fig.add_trace(go.Scatter(
                        x=x_width,
                        y=trace,
                        mode='lines+markers',
                        name=f"h = {h:.2f}"
                    ))

                height_fig.add_trace(go.Scatter(
                    x = Inputs.heights,
                    y = h_trace,
                    mode= 'lines+markers',
                    name = f"w = {w}"
                ))

                p_bar.empty()

                if Inputs.sweep_param == "Sweep Barrier Height":
                    st.plotly_chart(height_fig)
                else:
                    fig.update_layout(
                        title="(E2 - E1) vs. quantum well width",
                        xaxis_title="Width (Å)",
                        yaxis_title="Energy difference (meV)"
                    )
                    st.plotly_chart(fig)
