import plotly.graph_objects as go

class SweepVisualisation:
    def __init__(
        self,
        ediff_trace,
        dipoles_trace,
        osc_str_trace,
        x_vals,
        typ,
        x2_vals=None,
        k_values=None
    ):
        self.ediff = ediff_trace
        self.dipoles = dipoles_trace
        self.osc_strength = osc_str_trace
        self.x_vals = x_vals
        self.x2_vals = x2_vals
        self.typ = typ
        self.k_values = k_values or []

    def _make_fig(self, traces, y_label, title):
        fig = go.Figure()

        # ensure K labels exist
        if len(self.k_values) != len(traces):
            self.k_values = [f"K={i}" for i in range(len(traces))]

        for i, y in enumerate(traces):
            fig.add_trace(go.Scatter(
                x=self.x_vals,
                y=y,
                mode='lines+markers',
                name=str(self.k_values[i])
            ))

        # layout
        if self.typ == "Molar Content" and self.x2_vals is not None:
            fig.update_layout(
                xaxis=dict(
                    title="Molar Content [%]",
                    title_font=dict(size=16),
                    tickfont=dict(size=16)
                ),
                xaxis2=dict(
                    title="Conduction Band Offset [meV]",
                    overlaying='x',
                    side='top',
                    title_font=dict(size=16),
                    tickfont=dict(size=16)
                ),
                yaxis=dict(
                    title=y_label,
                    title_font=dict(size=16),
                    tickfont=dict(size=16)
                ),
                title=dict(text=title, y=0.95, font=dict(size=20)),
                margin=dict(t=100),
                showlegend=True
            )
        else:
            fig.update_layout(
                xaxis=dict(
                    title="Width [Å]",
                    title_font=dict(size=16),
                    tickfont=dict(size=16)
                ),
                yaxis=dict(
                    title=y_label,
                    title_font=dict(size=16),
                    tickfont=dict(size=16)
                ),
                title=title,
                showlegend=True
            )

        return fig

    def ediff_plot(self):
        return self._make_fig(
            self.ediff,
            "Energy [meV]",
            f"Energy difference vs {self.typ}"
        )

    def dipoles_plot(self):
        return self._make_fig(
            self.dipoles,
            "Dipole Moment [e nm]",
            f"Dipole Moments vs {self.typ}"
        )

    def osc_str_plot(self):
        return self._make_fig(
            self.osc_strength,
            "Oscillator Strength",
            f"Oscillator Strength vs {self.typ}"
        )
