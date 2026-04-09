import plotly.graph_objects as go

class SweepVisualisation:
    def __init__(self, plot_trace, x_vals, x_label:str, y_label:str, title:str) -> None:
        self.plot_trace = plot_trace
        self.x_vals = x_vals
        self.x_label = x_label
        self.y_label = y_label
        self.title = title

    def single_sweep_plot(self):
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=self.x_vals,
            y=self.plot_trace,
            mode='lines+markers',
        ))

        fig.update_layout(
            title=self.title,
            xaxis_title=self.x_label,
            yaxis_title=self.y_label
        )
        return fig