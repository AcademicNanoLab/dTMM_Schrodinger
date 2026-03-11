import streamlit as st
from ui.fields import *

class EnergyDifferencePage:
    def render(self):
        st.title("Energy Difference Plots")
        st.markdown("### <Calculate> button only appears once all fields are filled.")

        from src.Composition import Composition
        from src.Parameters import InputParameters
        import src.ConstAndScales

        st.text("Base Composition")
        composition = layer_input("Text")    
        material = material_input()
        solver = solver_input()
        nonparabolicity = np_input(solver)

        c1, c2, c3 = st.columns(3)

        with c1:
            nst_max = nst_input()
        with c2:
            dz = dz_input()
        with c3:
            pad = padding_input()
        
        K = st.number_input("K (kV/cm)", 0.0, 5.0, step=0.1, value = 1.9)
        
        ### Calculate
        import plotly.graph_objects as go
        fig = go.Figure()
        graph_type = st.pills("Choose graph type: ", ["Sweep Well Width", "Sweep Barrier Height", "Sweep Both"]) 

        if graph_type:
            heights, widths = get_sweep_ranges(graph_type)
            
            if solver and composition is not None:
                if st.button("Calculate"):
                    progress_text = "Calculating. Please wait."
                    pbar_val = 0
                    p_bar = st.progress(pbar_val, text=progress_text)
                    fig = go.Figure()
                    height_fig = go.Figure()
                    h_trace = []
                    for h in heights:
                        x_width = []
                        trace = []
                        for w in widths:
                            arr = composition.as_array()
                            arr[1][0] = w
                            arr[0][1] = h
                            arr[-1][1] = h
                            # arr = [
                            #     [225, h],
                            #     [w, 0],
                            #     [225, h]
                            # ]

                            C2 = Composition.from_array(arr)
                            IP = InputParameters(C2, material, solver, nonparabolicity, nst_max, dz, pad)
                            
                            from .solver_service import solve_structure
                            _, energies, _ = solve_structure(IP, K)
                            energies_meV = energies / src.ConstAndScales.meV

                            if len(energies) > 1:
                                x_width.append(w)
                                trace.append(energies_meV[1] - energies_meV[0])
                        
                            pbar_val += int(100/(len(heights)*len(widths)))
                            p_bar.progress(pbar_val, progress_text)
                            
                        if len(energies) > 1:
                            h_trace.append(energies_meV[1] - energies_meV[0])

                        fig.add_trace(go.Scatter(
                            x=x_width,
                            y=trace,
                            mode='lines+markers',
                            name=f"h = {h:.2f}"
                        ))

                    height_fig.add_trace(go.Scatter(
                        x = heights,
                        y = h_trace,
                        mode= 'lines+markers',
                        name = f"w = {w}"
                    ))

                    p_bar.empty()

                    if graph_type == "Sweep Barrier Height":
                        st.plotly_chart(height_fig)
                    else:
                        fig.update_layout(
                            title="(E2 - E1) vs. quantum well width",
                            xaxis_title="Width (Å)",
                            yaxis_title="Energy difference (meV)"
                        )
                        st.plotly_chart(fig)