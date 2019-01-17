from plotly.offline import plot
import plotly.graph_objs as go

from compute import grid_analytical_log_prob_sampled
from plot import get_bound_traces


def main():
    plot_heatmap_analytical_sampled()


def plot_heatmap_analytical_sampled():
    Nbits, density = 65536, .5
    ArrayMaxSize, RunMaxSize = 4096, 2048
    log_grid, x, y = grid_analytical_log_prob_sampled(Nbits, 64)
    z = log_grid
    title = 'Container space set density (log scale), M=%d' % (Nbits)
    fname = 'figures/heatmap-%d-sampled.html' % Nbits

    # TODO: plot as scatter instead of heatmap?
    data = [go.Heatmap(z=z, x=x, y=y, colorscale='Viridis')]
    data += get_bound_traces(Nbits, ArrayMaxSize)

    # full scale ticks
    xticks = range(0, Nbits+1, Nbits/8)
    yticks = range(0, Nbits/2+1, Nbits/(2*8))

    layout = go.Layout(
        showlegend=False,
        title=title,
        xaxis={'title': 'N (cardinality)', 'tickvals': xticks, 'ticktext': map(str, xticks)},
        yaxis={'title': 'N<sub>R</sub> (runCount)', 'tickvals': yticks, 'ticktext': map(str, yticks), 'scaleanchor': 'x's},
    )
    fig = go.Figure(data=data, layout=layout)
    plot(fig, filename=fname)


main()