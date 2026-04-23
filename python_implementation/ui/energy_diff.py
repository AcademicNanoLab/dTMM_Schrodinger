import streamlit as st

class EnergyDifferencePage:
    def render(self):
        st.title("Energy Difference Plots")
        
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
        else:
            if st.button("Calculate"):
                progress_text = "Calculating. Please wait."
                pbar_val = 0
                p_bar = st.progress(pbar_val, text=progress_text)

                ediff_trace = []
                dipole_trace = []
                osc_str_trace = []

                plot_heights = []
                plot_height2 = []
                for h in Inputs.heights:
                    plot_widths = []
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

                        # Calculate Energy difference, dipile moment and oscillator strength between the energy levels.
                        T = TransitionCalculator()
                        ediff, dipoles, osc_str = T.calculate(G.z, energies, wavefunctions, Inputs.i, Inputs.j)

                        if None not in (ediff, dipoles, osc_str):
                            plot_widths.append(w)
                            barrier_height = src.ConstAndScales.E *Inputs.M.interpolate_parameter(h, Inputs.M.V) / src.ConstAndScales.meV # type: ignore
                            plot_height2.append(barrier_height)
                            plot_heights.append(h)

                            ediff_trace.append(ediff / src.ConstAndScales.meV) # type: ignore ediff is not None
                            dipole_trace.append(dipoles / src.ConstAndScales.nano) # type: ignore dipoles is not None
                            osc_str_trace.append(osc_str / src.ConstAndScales.E) # type: ignore osc_str is not None
                        
                        pbar_val += int(100/(len(Inputs.heights)*len(Inputs.widths)))
                        p_bar.progress(pbar_val, progress_text)

                # Plot graphs
                from src.Sweep_Visualisation import SweepVisualisation

                match Inputs.sweep_param:
                    case "Sweep Well Width":
                        typ = "Well Width"
                        V = SweepVisualisation(ediff_trace, dipole_trace, osc_str_trace, plot_widths, typ)
                    
                    case "Sweep Barrier Height": # TODO: add second x axis with 
                        typ = "Barrier Height"
                        V = SweepVisualisation(ediff_trace, dipole_trace, osc_str_trace, plot_height2, typ)

                st.plotly_chart(V.ediff_plot())
                st.plotly_chart(V.dipoles_plot())
                st.plotly_chart(V.osc_str_plot())

                p_bar.empty()

