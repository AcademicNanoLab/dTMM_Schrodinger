#
#
# Visualization object that plots outputs of SchrodingerNonparabolic solver
#
#

import numpy as np
import plotly.graph_objects as go

from src import ConstAndScales

class Visualisation:
    def __init__(self, grid, energies, psi):
        self.G = grid
        self.E = energies       # (nstates,)
        self.psi = psi          # (nstates, nz)

    def plot_V_wf(self):
        padding = 0
        K = self.G.get_K()
        z = self.G.z / ConstAndScales.ANGSTROM
        Lper = z[-1] - padding
        dz = self.G.get_dz() / ConstAndScales.ANGSTROM
        npad = int(padding/dz/2) +1
        fig = go.Figure()

        for p in range(1):
            shift = (p-1)*Lper
            base = self.G.get_bandstructure_potential() /ConstAndScales.meV - 1e-2*K*Lper*(p-1)
            zz = z[npad:-npad] + shift
            fig.add_trace(go.Scatter(x=zz, y=base[npad:-npad], mode='lines', line=dict(width=3)))

            for i, Ei in enumerate(self.E):
                wf = 1e3*(np.abs(self.psi[i][npad:-npad])**2) + Ei/ConstAndScales.meV - 1e-2*K*Lper*(p-1)
                fig.add_trace(go.Scatter(x=zz, y=wf, mode='lines'))
        
        fig.update_layout(
            title = 'Bandstructure Profile',
            xaxis_title = 'z [Å]',
            yaxis_title = 'V [meV]'
        )
    
        return fig
    
    def plot_QCL(self, K=0.0, padding=0, is_gif=False, axis=None):
        z = self.G.z / ConstAndScales.ANGSTROM
        Lper = z[-1] - padding
        dz = self.G.get_dz() / ConstAndScales.ANGSTROM
        npad = int(padding/dz/2) +1
        fig = go.Figure()

        for p in range(2):
            shift = (p-1)*Lper
            base = self.G.get_bandstructure_potential() /ConstAndScales.meV - 1e-2*K*Lper*(p-1)
            zz = z[npad:-npad] + shift
            fig.add_trace(go.Scatter(x=zz, y=base[npad:-npad], mode='lines', line=dict(width=3)))

            for i, Ei in enumerate(self.E):
                wf = 1e3*(np.abs(self.psi[i][npad:-npad])**2) + Ei/ConstAndScales.meV - 1e-2*K*Lper*(p-1)
                fig.add_trace(go.Scatter(x=zz, y=wf, mode='lines'))
        
        fig.update_layout(
            title = f'K = {K}' if is_gif else 'Two QCL Periods',
            xaxis_title = 'z [Å]', 
            yaxis_title = 'V [meV]'
        )

        if axis:
            fig.update_xaxes(range=[axis[0], axis[1]])
            fig.update_yaxes(range=[axis[2], axis[3]])
        
        return fig

    def plot_energies(self):
        y = self.E / ConstAndScales.meV
        fig = go.Figure()
        for i, yi in enumerate(y):
            # marker
            fig.add_trace(go.Scatter(x=[i], y=[yi], mode='markers', marker=dict(symbol="circle-open", size=18, color='blue')))
            # dashed line to x-axis
            fig.add_trace(go.Scatter(x=[i, i], y=[0, yi], mode='lines', line=dict(dash='dash', color='blue')))
        
        fig.update_layout(
            title='Bound state energies',
            xaxis_title='#',
            yaxis_title='E [meV]',
            showlegend = False
        )
        return fig


    def plot_energy_diff_thz(self):
        f = np.diff(self.E / ConstAndScales.meV) / 4.1356
        labels = [11*i+10 if i<10 else 101*i+100 for i in range(1, len(self.E))]
        fig = go.Figure()
        for i, fi in enumerate(f):
            # marker
            fig.add_trace(go.Scatter(x=[i], y=[fi], mode='markers', marker=dict(symbol="circle-open", size=18, color='red')))
            # dashed line to x-axis
            fig.add_trace(go.Scatter(x=[i, i], y=[0, fi], mode='lines', line=dict(dash='dash', color='red')))
        
        fig.update_xaxes(tickvals=list(range(len(f))), ticktext=[str(l) for l in labels])
        fig.update_layout(
            title='Energy differences',
            xaxis_title='fi',
            yaxis_title='f [THz]', 
            showlegend = False
        )
        return fig