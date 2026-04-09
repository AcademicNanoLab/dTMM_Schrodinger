import plotly.graph_objects as go

class SweepVisualisation:
    def __init__(self, ediff_trace, dipoles_trace, osc_str_trace, x_vals, typ ) -> None:
        self.ediff = ediff_trace
        self.dipoles = dipoles_trace
        self.osc_strength = osc_str_trace
        self.x_vals = x_vals
        self.typ = typ

    def single_sweep_plot(self, plot_trace, y_label, title):
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=self.x_vals,
            y=plot_trace,
            mode='lines+markers',
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Height ()" if self.typ == "Barrier Height" else "Width (Å)",
            yaxis_title=y_label
        )
        return fig

    def ediff_plot(self):
        return self.single_sweep_plot(self.ediff, "Energy (meV)", f"Energy difference vs {self.typ}")
    
    def dipoles_plot(self):
        return self.single_sweep_plot(self.dipoles, "Dipole Moment", f"Dipole Moments vs {self.typ}")

    def osc_str_plot(self):
        return self.single_sweep_plot(self.osc_strength, "Oscillator Strength", f"Energy difference vs {self.typ}")
