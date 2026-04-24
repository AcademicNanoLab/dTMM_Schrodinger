import plotly.graph_objects as go

class SweepVisualisation:
    def __init__(self, ediff_trace, dipoles_trace, osc_str_trace, x_vals, typ, x2_vals=None ) -> None:
        self.ediff = ediff_trace
        self.dipoles = dipoles_trace
        self.osc_strength = osc_str_trace
        self.x_vals = x_vals
        self.x2_vals = x2_vals
        self.typ = typ

    def single_sweep_plot(self, plot_trace, y_label, title):
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=self.x_vals,
            y=plot_trace,
            mode='lines+markers',
        ))

        if self.typ == "Molar Content" and self.x2_vals is not None:
            fig.add_trace(go.Scatter(
                x=self.x2_vals,
                y=plot_trace,
                mode='lines+markers',
                xaxis='x2',
            ))
            fig.update_layout(
                xaxis=dict(
                    title="Molar Content (%)",
                    title_font=dict(size=16),
                    tickfont = dict(size=16)),
                xaxis2=dict(
                    title="Conduction Band Offset (meV)",
                    title_font=dict(size=16),
                    tickfont = dict(size=16),
                    overlaying='x',
                    side='top'
                ),
                yaxis = dict(
                    title = y_label,
                    title_font=dict(size=16),
                    tickfont = dict(size=16)
                ),
                title=dict(text=title, y=0.95, font=dict(size=20)),
                margin=dict(t=100),
                showlegend = False
            )
        else:
            fig.update_layout(
                xaxis=dict(
                    title="Width (Å)",
                    title_font=dict(size=16),
                    tickfont = dict(size=16)
                ),
                yaxis = dict(
                    title = y_label,
                    title_font=dict(size=16),
                    tickfont = dict(size=16)
                ),
                title=title,
                showlegend = False
            )
        return fig

    def ediff_plot(self):
        return self.single_sweep_plot(self.ediff, "Energy (meV)", f"Energy difference vs {self.typ}")
    
    def dipoles_plot(self):
        return self.single_sweep_plot(self.dipoles, "Dipole Moment", f"Dipole Moments vs {self.typ}")

    def osc_str_plot(self):
        return self.single_sweep_plot(self.osc_strength, "Oscillator Strength", f"Oscillator Strength vs {self.typ}")
