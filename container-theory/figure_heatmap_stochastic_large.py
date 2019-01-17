import numpy as np
from plotly.offline import plot
import plotly.graph_objs as go

from plot import get_bound_traces
from compute import grid_stochastic_large


def main():
    plot_grid_stochastic_large()


def plot_grid_stochastic_large():
    Nbits, Niter, density = 65536, 100000, .5
    ArrayMaxSize, RunMaxSize = 4096, 2048
    grid, x, y = grid_stochastic_large(Nbits, Niter, density)
    
    # log_grid = np.log10(grid * (2**Nbits/Niter))
    # log_grid = Nbits * np.log10(2) - np.log10(Niter) + np.log10(grid)    
    log_grid = Nbits * np.log10(2) - np.log10(Niter) + np.log10(grid)
    z = log_grid
    title = 'Container space set density, M=%d, %d iterations (log scale)' % (Nbits, Niter)
    fname = 'figures/heatmap-%d-stochastic.html' % Nbits

    data = [go.Heatmap(z=z, x=x, y=y, colorscale='Viridis')]
    data += get_bound_traces(Nbits, ArrayMaxSize)

    # full scale ticks
    #xticks = range(0, Nbits+1, Nbits/8)
    #yticks = range(0, Nbits/2+1, Nbits/(2*8))

    # zoom ticks
    xticks = range(2**15-2**9, 2**15+2**9+1, 2**10/8)
    yticks = range(2**14-2**8, 2**14+2**8+1, 2**9/8)
    layout = go.Layout(
        showlegend=False,
        title=title,
        xaxis={'title': 'N (cardinality)', 'tickvals': xticks, 'ticktext': map(str, xticks)},
        yaxis={'title': 'N<sub>R</sub> (runCount)', 'tickvals': yticks, 'ticktext': map(str, yticks), 'scaleanchor': 'x'},
    )
    fig = go.Figure(data=data, layout=layout)
    plot(fig, filename=fname)


main()