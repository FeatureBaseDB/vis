import pickle
import math
import time
import numpy as np

from plotly.offline import plot
import plotly.graph_objs as go

from compute import grid_analytical_logF_conditional, sum_F_smart
from definitions import large_log_sum_array
from conditions import cond_map


def main():
    # compute_count_vs_n(65536, 64)
    plot_count_vs_n(65536, mode='count', regions='iarray')
    #plot_count_vs_n(65536, mode='freq', regions='iarray')
    #plot_count_vs_n(65536, mode='count', regions='array')
    #plot_count_vs_n(65536, mode='freq', regions='array')
    

def counts_to_freqs(data):
    data['array']['array'] -= data['max']
    data['array']['bitmap'] -= data['max']
    data['array']['runs'] -= data['max']
    # data['iarray']['array'] -= data['max']  # this is the same object as array-array...
    data['iarray']['iarray'] -= data['max']
    data['iarray']['runs_iarray'] -= data['max']
    data['iarray']['bitmap_iarray'] -= data['max']


def plot_count_vs_n(M, mode='count', regions='array'):
    fname = 'data/count-vs-n-%s.pickle' % (M)
    with open(fname, 'r') as f:
        data = pickle.load(f)

    title = 'Container type count vs cardinality (log scale)'
    ytitle = 'Log count'
    if mode == 'freq':
        title = 'Container type frequency vs cardinality (log scale)'
        ytitle = 'Log probability'
        counts_to_freqs(data)

    traces = []
    c_vec = data['c']

    keys = data[regions].keys()
    # sort the keys for consistent trace order
    for k in sorted(keys):
        traces.append({'x': c_vec, 'y': data[regions][k], 'name': k})

    # full view
    xticks = range(0, M+1, M/8)

    # zoom view
    # xticks = range(0, M/8+1, M/64)

    layout = go.Layout(
        title=title,
        xaxis={'title': 'N (cardinality)', 'tickvals': xticks, 'ticktext': map(str, xticks)},
        yaxis={'title': ytitle},
    )
    fig = go.Figure(data=traces, layout=layout)

    plot(fig, filename='figures/count-vs-n.html')


def compute_count_vs_n(M=65536, step=64):
    MA, MR = 4096, 2048

    c_vec = np.arange(0, M+1, step)

    # add some extra values to check for sharper curve definition
    # these values are just left/right of the cardinality bounds
    b0 = [1, 2, 4, 65532, 65534, 65535]
    b1 = [4095, 4096, 4097]
    b2 = [61439, 61440, 61441]
    b3 = [63487, 63488, 63489]
    b4 = range(62976, 63488, 32)
    c_vec = np.hstack((c_vec, b0, b1, b2, b3, b4))
    c_vec.sort()

    # z_array = np.zeros(c_vec.shape)  # cond_map avoids having to repeat a line like this 6 times
    z = {}
    for ctype in cond_map:
        z[ctype] = np.zeros(c_vec.shape)

    def f_all(M, MA, card):
        return range(0, M/2+1)

    t0 = time.time()
    for n, c in enumerate(c_vec):
        print('%d/%d, %d (%f sec)' % (n, len(c_vec)+1, c, time.time() - t0))
        # z_array[n] = sum_F_smart(M, MA, [c], f_all, array_cond_mutex(M, MA))
        for ctype, cond in cond_map.items():
            z[ctype][n] = sum_F_smart(M, MA, [c], f_all, cond(M, MA))

    fname = 'data/count-vs-n-%s.pickle' % (M)
    data = {
        'c': c_vec,
        'max': np.max(np.vstack((z['array'], z['bitmap'], z['runs'])), axis=0),
        'array': {
            'array': z['array'],
            'runs': z['runs'],
            'bitmap': z['bitmap'],
        },
        'iarray': {
            'array': z['array'],
            'iarray': z['iarray'],
            'runs_iarray': z['runs_iarray'],
            'bitmap_iarray': z['bitmap_iarray'],
        },
    }
    with open(fname, 'w') as f:
        pickle.dump(data, f)


main()