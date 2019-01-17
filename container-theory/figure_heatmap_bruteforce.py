from plotly.offline import plot
import plotly.graph_objs as go

from compute import grid_deterministic


def main():
    plot_grid_deterministic()



def plot_grid_deterministic():
    Nbits, Niter = 8, 256
    #Nbits, Niter = 16, 65536
    grid, x, y = grid_deterministic(Nbits, debug=True)
    for r in grid:
        m = ''
        for c in r:
            m += '%4d ' % int(c)
        print(m)
    z = grid
    title = 'Container space set density (linear scale), M=%d' % (Nbits)
    fname = 'figures/heatmap-%d.html' % Nbits

    data = [go.Heatmap(z=z, x=x, y=y, colorscale='Viridis')]

    layout = go.Layout(
        showlegend=False,
        title=title,
        xaxis={'title': 'N (cardinality)'},
        yaxis={'title': 'N<sub>R</sub> (runCount)', 'scaleanchor': 'x'},
    )
    fig = go.Figure(data=data, layout=layout)
    plot(fig, filename=fname)


main()