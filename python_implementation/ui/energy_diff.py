import streamlit as st
import numpy as np
from ui.fields import *

class EnergyDifferencePage:
    def render(self):
        st.title("Energy Difference Plots")
        from src.Grid import Grid
        from src.Composition import Composition
        from .user_inputs import EnergyDiffInputs
        from src.Solvers_FDM import SolverFactory
        Inputs = EnergyDiffInputs()
        Inputs.render_energy_diff_inputs()

        ### Calculate
        import plotly.graph_objects as go
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

                        C = Composition.from_array(arr)
                        G = Grid(C, Inputs.dz, Inputs.material)
                        G.set_K(Inputs.K)

                        Solver = SolverFactory.create(G, Inputs.solver, Inputs.nonparabolicity, Inputs.nstmax)
                        energies, wavefunctions = Solver.get_wavefunctions()
                        i = 2
                        j = 1

                        T = TransitionCalculator()
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

class TransitionCalculator:
    def __init__(self) -> None:
        import src.ConstAndScales
        self.m_e = src.ConstAndScales.m0
        self.hbar = src.ConstAndScales.HBAR
        self.meV = src.ConstAndScales.meV
    
    def get_energy_diff(self, energies, i, j):
        if len(energies) < max(i, j):
            return None
        else:
            return energies[i-1] - energies[j-1] # FIXME: Needs div by meV.
    
    def get_dipole(self, z, psis, i, j):
        if len(psis) < max(i, j):
            return None

        psi_i = psis[i-1]
        psi_j = psis[j-1]

        dz = z[1] - z[0]

        integ=np.abs(psi_i)*np.abs(psi_i)
        temp=0
        for iz in range(1,len(z)):
            temp+= dz * (integ[iz-1]+integ[iz])/2
        # z_m = z * 1e-10   # Å → m
        integral=0
        integrand = psi_i * z * psi_j
        for iz in range(1,len(z)):
            integral+= dz * (integrand[iz-1]+integrand[iz])/2
        return abs(integral)
    
    def get_oscillator_strength(self, z, energies, psis, i,j):
        e_ij = self.get_energy_diff(energies, i,j)
        if e_ij is None:
            return None
        else:
            d_ij = self.get_dipole(z, psis, i,j)
            if d_ij is None:
                return None
            return (2*self.m_e / self.hbar**2) * e_ij * abs(d_ij)**2
    
    def calculate(self, z, energies, psis, i,j):
        e21 = self.get_energy_diff(energies, i,j)
        d21 = self.get_dipole(z, psis, i,j)
        f21 = self.get_oscillator_strength(z, energies, psis, i,j)
        return e21, d21, f21