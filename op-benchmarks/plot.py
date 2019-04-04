import re
import numpy as np
import matplotlib.pyplot as plt


names = ['difference', 'intersect', 'intersection-count', 'union', 'xor']


def read_opgrid():
    data = {}
    for name in names:
        data[name] = read_grid_file(name + '.txt')
    return data


def read_grid_file(fname):
    with open(fname) as f:
        lines = f.read().strip().split('\n')

    grid = []
    ylabels = []
    for line in lines:
        if '.' in line:
            parts = str(re.sub(' +', ' ', line.strip())).split(' ')
            ylabels.append(parts[0])
            grid.append([float(x) for x in parts[1:]])
        else:
            xlabels = str(re.sub(' +', ' ', line.strip())).split(' ')

    return {
        'xlabels': xlabels,
        'ylabels': ylabels,
        'grid': grid,
    }


def plot_grid(ax, data):
    cax = ax.imshow(np.log10(data['grid']))

    ax.plot([4.5, 4.5], [-0.5, 15.5], 'w-')
    ax.plot([9.5, 9.5], [-0.5, 15.5], 'w-')
    ax.plot([10.5, 10.5], [-0.5, 15.5], 'w-')
    ax.plot([11.5, 11.5], [-0.5, 15.5], 'w-')
    ax.plot([-0.5, 15.5], [4.5, 4.5], 'w-')
    ax.plot([-0.5, 15.5], [9.5, 9.5], 'w-')
    ax.plot([-0.5, 15.5], [10.5, 10.5], 'w-')
    ax.plot([-0.5, 15.5], [11.5, 11.5], 'w-')

    plt.xticks(np.arange(0, len(data['xlabels'])), data['xlabels'], rotation='vertical')
    plt.yticks(np.arange(0, len(data['ylabels'])), data['ylabels'])
    ax.grid(False)

    cbar = plt.colorbar(cax, ticks=[1, 2, 3, 4, 5])
    cbar.ax.set_yticklabels(['1 ns', '10 ns', '100 ns', '1 μs', '10 μs'])


def pnorm(A, p=2):
    return np.sum(np.sum(np.abs(A))) ** (1/p)


data = read_opgrid()
for name in names:
    fig, ax = plt.subplots()
    plot_grid(ax, data[name])

    A = np.array(data[name]['grid'])
    Asym = (A + A.T)/2
    Aanti = (A - A.T)/2

    norm = pnorm
    sym_ratio1 = (norm(Asym) - norm(Aanti)) / (norm(Asym) + norm(Aanti))
    sym_ratio2 = (norm(Asym) - norm(Aanti)) / norm(A)
    print(sym_ratio1, sym_ratio2)

    plt.title('%s (symmetry ratio %4.2f)' % (name, sym_ratio2))
    ax.set_position([0.2, 0.3, 0.5, 0.5])
    plt.savefig('%s.png' % name, bbox_inches='tight')


plt.show()
