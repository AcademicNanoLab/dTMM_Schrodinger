import streamlit as st
import numpy as np
from ui.fields import *

class EnergyDifferencePage:
    def render(self):
        st.title("Energy Difference Plots")

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
        sweep_param = st.pills("Choose sweep parameter: ", ["Sweep Well Width", "Sweep Barrier Height", "Sweep Both"])
        plot_diff = st.pills("Choose plot value: ", ["Energy Difference", "Dipole matrix element", "Oscillator Strength"])

        if sweep_param is None or plot_diff is None:
            st.markdown(":red-badge[**<Calculate> button only appears once all fields are filled.**]")
        else:
            heights, widths = get_sweep_ranges(sweep_param)
            
            if solver is None or composition is None:
                st.markdown(":red-badge[**<Calculate> button only appears once all fields are filled.**]")
            else:
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
                            arr = composition.as_array() # type: ignore
                            arr[1][0] = w
                            arr[0][1] = h
                            arr[-1][1] = h

                            C2 = Composition.from_array(arr)
                            IP = InputParameters(C2, material, solver, nonparabolicity, nst_max, dz, pad)
                            
                            from .solver_service import solve_structure
                            G, energies, wavefunctions = solve_structure(IP, K)
                            print("@£@£@£@£@£@£@£@£",len(energies))
                            if len(energies) < 2:
                                continue

                            T = TransitionCalculator()
                            if plot_diff == "Energy Difference":
                                trace.append(T.get_E21(energies))
                            elif plot_diff == "Dipole matrix element":
                                tmp = T.get_d21(G.z, wavefunctions)
                                if tmp is not None:
                                    trace.append(tmp /10e-9)
                            elif plot_diff == "Oscillator Strength":
                                trace.append(T.get_f21(G.z, energies, wavefunctions))
                            x_width.append(w)

                            pbar_val += int(100/(len(heights)*len(widths)))
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
                        x = heights,
                        y = h_trace,
                        mode= 'lines+markers',
                        name = f"w = {w}"
                    ))

                    p_bar.empty()

                    if sweep_param == "Sweep Barrier Height":
                        st.plotly_chart(height_fig)
                    else:
                        fig.update_layout(
                            title="(E2 - E1) vs. quantum well width",
                            xaxis_title="Width (Å)",
                            yaxis_title="Energy difference (meV)"
                        )
                        st.plotly_chart(fig)

class TransitionCalculator:
    def __init__(self) -> None:
        import src.ConstAndScales
        self.m_e = src.ConstAndScales.m0
        self.hbar = src.ConstAndScales.HBAR
        self.meV = src.ConstAndScales.meV
    
    def get_E21(self, energies):
        if len(energies) < 2:
            return None
        else:
            return energies[1] - energies[0] # FIXME: Needs div by meV.
    
    def get_d21(self, z, psis):
        if len(psis) < 2:
            return None

        psi1 = psis[0]
        psi2 = psis[2]

        # z_m = z * 1e-10   # Å → m
        dz = z[1] - z[0]
        integral=0
        integrand = psi1 * z * psi2
        for i in range(1,len(z)):
            integral+= dz * (integrand[i-1]+integrand[i])/2
        # print("new")
        return abs(integral)
    
    def get_f21(self, z, energies, psis):
        e21 = self.get_E21(energies)
        if e21 is None:
            return None
        else:
            d21 = self.get_d21(z, psis)
            if d21 is None:
                return None
            return (2*self.m_e / self.hbar**2) * e21 * abs(d21)**2
    
    def calculate(self, z, energies, psis):
        e21 = self.get_E21(energies)
        d21 = self.get_d21(z, psis)
        f21 = self.get_f21(z, energies, psis)
        return e21, d21, f21