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
        z = self.G.z / ConstAndScales.ANGSTROM
        V = self.G.get_bandstructure_potential() / ConstAndScales.meV
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=z, y=V, mode='lines', line=dict(width=3)))
        
        for i, Ei in enumerate(self.E):
            wf = 1e3*(np.abs(self.psi[i]**2)+ Ei/ConstAndScales.meV)
            fig.add_trace(go.Scatter(x=z, y=wf, mode='lines'))
        
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
        fig = go.Figure(go.Scatter(x=list(range(len(y))), y=y, mode='markers+lines'))
        fig.update_layout(
            title = 'Bound state energies',
            xaxis_title = '#',
            yaxis_title = 'E [meV]'
        )

        return fig

    def plot_energy_diff_thz(self):
        f = np.diff(self.E/ConstAndScales.meV)/4.1356
        labels = [11*i+10 if i<10 else 101*i+100 for i in range(1, len(self.E))]
        fig = go.Figure(go.Scatter(x=list(range(len(f))), y=f, mode='markers+lines'))
        fig.update_xaxes(tickvals=list(range(len(f))), ticktext=[str(l) for l in labels])
        fig.update_layout(
            title='Energy differences',
            xaxis_title='fi',
            yaxis_title='f [THz]'
        )
        return fig