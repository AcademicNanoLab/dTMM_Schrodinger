#
#   Core Visualisation functions using plotly. 
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
            shift = p*Lper
            base = self.G.get_bandstructure_potential() /ConstAndScales.meV - 1e-2*K*Lper*(p-1)
            zz = z[npad:-npad] + shift
            fig.add_trace(go.Scatter(x=zz, y=base[npad:-npad], mode='lines', line=dict(width=4), name="V(z)"))

            for i, Ei in enumerate(self.E):
                wf = 1e3*(np.abs(self.psi[i][npad:-npad])**2) + Ei/ConstAndScales.meV - 1e-2*K*Lper*(p-1)
                tracelegend = f"{Ei/ConstAndScales.meV:.2f} meV"
                fig.add_trace(go.Scatter(x=zz, y=wf, mode='lines', line=dict(width=3), name=tracelegend))
        
        fig.update_layout(
            title = dict(text='Bandstructure Profile', y=0.95, font=dict(size=22)),
            xaxis = dict(title='z [Å]', title_font=dict(size=16) ,tickfont=dict(size=16)),
            yaxis = dict(title='V [meV]', title_font=dict(size=16) ,tickfont=dict(size=16))
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
            if p==0:
                fig.add_trace(go.Scatter(x=zz, y=base[npad:-npad], mode='lines', line=dict(width=4), name="V(z)"))
            else:
                fig.add_trace(go.Scatter(x=zz, y=base[npad:-npad], mode='lines', line=dict(width=4), showlegend=False))

            for i, Ei in enumerate(self.E):
                wf = 1e3*(np.abs(self.psi[i][npad:-npad])**2) + Ei/ConstAndScales.meV - 1e-2*K*Lper*(p-1)
                legendvalue = Ei/ConstAndScales.meV - 1e-2*K*Lper*(p-1)
                fig.add_trace(go.Scatter(x=zz, y=wf, mode='lines', line = dict(width=3), name = f"{legendvalue:.2f} meV" ))
        
        fig.update_layout(
            title = dict(text='Two QCL Periods', y=0.95, font=dict(size=22)),
            xaxis = dict(title='z [Å]', title_font=dict(size=16) ,tickfont=dict(size=16)),
            yaxis = dict(title='V [meV]', title_font=dict(size=16) ,tickfont=dict(size=16))
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
    
    def plot_wavefunction(self):
        fig = go.Figure()
        z = self.G.z / ConstAndScales.ANGSTROM

        wf = self.psi[1].real
        fig.add_trace(go.Scatter(x=z, y=wf, mode='lines'))
        return fig