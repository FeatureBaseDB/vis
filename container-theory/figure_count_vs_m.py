import pickle
import math

from plotly.offline import plot
import plotly.graph_objs as go

from compute import total_counts_for_m


def main():
    # a, r, t = total_counts_for_m(65536)
    # print(a, r, t)
    # (6651.998924680548, 6651.9989246803443, 19728.301795834672)

    plot_count_vs_m()


def plot_count_vs_m():
    fname = 'data/total_counts_vs_m.pickle'
    with open(fname, 'r') as f:
        data = pickle.load(f)

    c_bitmap = []
    for n in range(len(data['total'])):
        M, a, r, t = data['M'][n], data['array'][n], data['runs'][n], data['total'][n]
        if M <= 512:
            b = math.log10(10 ** t - 10 ** r - 10 ** a)
            c_bitmap.append(b)
        else:
            c_bitmap.append(t)

    x = map(math.log10, data['M'])
    ytick = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
    traces = [
        go.Scatter(x=x, y=map(math.log10, c_bitmap), name='bitmap'),
        go.Scatter(x=x, y=map(math.log10, data['total']), name='total', line={'dash':'dash'}),
        go.Scatter(x=x, y=map(math.log10, data['array']), name='array'),
        go.Scatter(x=x, y=map(math.log10, data['runs']), name='runs', line={'dash':'dash'}),
    ]

    x = map(math.log10, data['M'])
    ytick = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
    layout = go.Layout(
        title='Container type count vs M (log-loglog)',
        xaxis={'title': 'M', 'ticktext': map(str, data['M']), 'tickvals': x},
        yaxis={'title': 'Log Count', 'ticktext': map(str, ytick), 'tickvals': map(math.log10, ytick)},
    )

    fig = go.Figure(data=traces, layout=layout)
    plot(fig, filename='figures/count-vs-m.html')


main()