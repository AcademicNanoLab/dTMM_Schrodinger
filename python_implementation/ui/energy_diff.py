import streamlit as st

class EnergyDifferencePage:
    def render(self):
        st.title("Transition Calculator")
        
        from src.Grid import Grid
        from src.Composition import Composition
        from src.Solvers_FDM import SolverFactory

        from .user_inputs import EnergyDiffInputs
        Inputs = EnergyDiffInputs()
        Inputs.render_energy_diff_inputs()

        ### Calculate
        import src.ConstAndScales
        from src.TransitionCalculator import TransitionCalculator

        if None in (Inputs.solver, Inputs.composition, Inputs.sweep_param):
            st.markdown(":red-badge[**<Calculate> button only appears once all fields are filled.**]")
            return

        if st.button("Calculate"):
            progress_text = "Calculating. Please wait."
            pbar_val = 0
            p_bar = st.progress(pbar_val, text=progress_text)

            ediff_trace = []
            dipole_trace = []
            osc_str_trace = []

            plot_heights = []
            plot_height2 = []

            # K handling: single or list, but always treated as "overlay runs"
            K_list = Inputs.K_values if hasattr(Inputs, "K_values") else [Inputs.K]

            total_steps = len(K_list) * len(Inputs.heights) * len(Inputs.widths)

            for K in K_list:
                for h in Inputs.heights:
                    plot_widths = []

                    for w in Inputs.widths:
                        arr = Inputs.composition.as_array()  # type: ignore
                        arr[1][0] = w
                        arr[0][1] = h
                        arr[-1][1] = h
                    
                        C2 = Composition.from_array(arr)
                        
                        G = Grid(C2, Inputs.dz, Inputs.material)
                        G.set_K(K)

                        solver = SolverFactory.create(
                            G,
                            Inputs.solver,
                            Inputs.nonparabolicity,
                            Inputs.nstmax
                        )
                        energies, wavefunctions = solver.get_wavefunctions()

                        T = TransitionCalculator()
                        ediff, dipoles, osc_str = T.calculate(
                            G.z, energies, wavefunctions, Inputs.i, Inputs.j
                        )

                        if None not in (ediff, dipoles, osc_str):
                            plot_widths.append(w)

                            barrier_height = (
                                src.ConstAndScales.E
                                * Inputs.M.interpolate_parameter(h, Inputs.M.V)
                                / src.ConstAndScales.meV
                            )

                            plot_height2.append(barrier_height)
                            plot_heights.append(h)

                            ediff_trace.append(ediff / src.ConstAndScales.meV)
                            dipole_trace.append(dipoles / src.ConstAndScales.nano)
                            osc_str_trace.append(osc_str / src.ConstAndScales.E)

                        pbar_val += int(100 / total_steps)
                        p_bar.progress(min(pbar_val, 100), text=progress_text)

            from src.Sweep_Visualisation import SweepVisualisation

            match Inputs.sweep_param:
                case "Sweep Well Width":
                    typ = "Well Width"
                    V = SweepVisualisation(
                        ediff_trace,
                        dipole_trace,
                        osc_str_trace,
                        plot_widths,
                        typ,
                        None,
                        K_list
                    )

                case "Sweep Molar Content":
                    typ = "Molar Content"
                    V = SweepVisualisation(
                        ediff_trace,
                        dipole_trace,
                        osc_str_trace,
                        plot_heights,
                        typ,
                        plot_height2
                    )

            st.plotly_chart(V.ediff_plot())
            st.plotly_chart(V.dipoles_plot())
            st.plotly_chart(V.osc_str_plot())

            p_bar.empty()
