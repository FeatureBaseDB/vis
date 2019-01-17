from collections import Counter
import pickle
import time
import numpy as np

from definitions import F, logF, logProbabilityF, max_array_size, large_log_sum
from conditions import *

## helpers
def countruns(x):
    padded = np.insert(x, 0, 0)  # pad left side with 0
    ups = np.diff(padded+0) == 1
    return np.count_nonzero(ups)


## computation functions for simple line plots
def total_counts_vs_m():
    M_vec = [2 ** e for e in range(3, 16+1)]
    c_array, c_runs, c_total = [], [], []
    for M in M_vec:
        print(M)
        a, r, t = total_counts_for_m(M)
        c_array.append(a)
        c_runs.append(r)
        c_total.append(t)

    data = {
        'M': M_vec,
        'array': c_array,
        'runs': c_runs,
        'total': c_total,
    }

    fname = 'data/total_counts_vs_m.pickle'
    with open(fname, 'w') as f:
        pickle.dump(data, f)


def total_counts_for_m(M):
	# compute total count of all sets in certain regions, for given value of M
	# returns (in log domain):
	# - s_array: total count of all array sets
	# - s_runs: total count of all RLE sets
	# - s_total: total count of all sets

    MA = max_array_size(M)

    def f_array(M, MA, card):
        return range(card/2, card+1)
    c_array = range(0, MA+1)
    s_array = sum_F_smart(M, MA, c_array, f_array, array_cond_mutex(M, MA))

    def f_runs(M, MA, card):
        return range(1, min(MA/2+1, card/2))
    c_runs = range(0, M+1)
    s_runs = sum_F_smart(M, MA, c_runs, f_runs, runs_cond_mutex(M, MA))

    return s_array, s_runs, M * np.log10(2)


## computation functions for heatmaps (analytical)

# sum_F_smart is the latest version of the grid computation
# functions, and should be faster than grid_analytical_*
def sum_F_smart(M, MA, card_vec, runs_vec_func, cond):
	# compute sum of all values of F over an arbitrary region.
	# M and MA are constants.
	# grid is computed for every value in card_vec.
	# runs_vec_func computes a new vector of runs values to be used for each value of card.
	# this allows computing over an arbitrary window.
	# cond is another arbitrary window function - these functions are more confidently verified than the
	# runs_vec_func functions.
    s = -np.inf
    for card in card_vec:
        print(card)
        runs_vec = runs_vec_func(M, MA, card)
        for runs in runs_vec:
            if cond(card, runs):
                v = logF(card, runs, M)
                s = large_log_sum(v, s)

    return s


def grid_analytical_logF_conditional(M, card_vec, runs_vec, width, cond, debug=True):
    # previously known as sum_logF_for_condition
    if debug:
        print('summing for %s' % cond.__name__)
    t0 = time.time()
    z = np.ones((len(runs_vec), len(card_vec)))*-np.inf
    for n, card in enumerate(card_vec):
        if debug:
            # print('x = %d (%d/%d)' % (card, n, len(card_vec)))
            pass
        for m, runs in enumerate(runs_vec):
            z[m, n] = sum_logF_over_rectangle_conditional(M, [card, card+width], [runs, runs+width], cond)
            # print(n, m, z[m, n])
            if m > 0 and z[m, n] == 0 and z[m-1, n] > 0:
                # passed out of region, stop counting
                break

    if debug:
        print('%f sec' % (time.time() - t0))
    return z


def sum_logF_over_rectangle_conditional(M, card_range, runs_range, cond):
    # when summing a bunch of numbers with widely varying magnitude,
    # only need to sum the top few for an accurate result.
    t0 = time.time()
    s = -np.inf
    for card in range(card_range[0], card_range[1]):
        for runs in range(runs_range[0], runs_range[1]):
            if runs > card or runs > M-card+1:
                # impossible region, should never compute this
                break
            if cond(card, runs):
                # v = logF_nocheck(card, runs, M)
                v = logF(card, runs, M)
                # print(card, runs, v)
                s = large_log_sum(s, v)

    # print('10^%d sets in %sx%s (%f sec)' % (s, card_range, runs_range, time.time()-t0))
    dt = time.time() - t0
    return s


def grid_analytical_integral(M, cell_size):
    # naively compute downsampled grid by summing over evenly spaced rectangular regions
    grid = np.zeros((M/(2*cell_size)+1, M/cell_size+1))
    # cvec and rvec represent lower-left corner of cell
    cvec = range(0, M+1, cell_size)
    rvec = range(0, M/2+1, cell_size)
    for x, card in enumerate(cvec):
        for y, runs in enumerate(rvec):
            grid[y, x] = sum_F_over_rectangle(M, [card, card+cell_size], [runs, runs+cell_size])
    # print(grid)
    return grid, cvec, rvec


def sum_F_over_rectangle(M, card_range, runs_range):
    # naively sum exact F values over rectangular region
    s = 0
    for card in range(card_range[0], card_range[1]):
        for runs in range(runs_range[0], runs_range[1]):
            v = F(card, runs, M)
            s += v
            # print('%d added for (%d, %d) - (%s, %s)' % (v, card, runs, card_range, runs_range))
    return s


def grid_analytical_log_prob_sampled(Nbits, width):
	# compute samples of the grid for a given Nbits. 
	# samples are spaced 'width' pixels apart
    grid = np.ones((width/2+1, width+1)) * -np.inf
    cvec = range(1, Nbits+1, Nbits/width)
    rvec = range(1, Nbits/2+1, Nbits/width)
    for x, cardinality in enumerate(cvec):
        print(cardinality)
        for y, runcount in enumerate(rvec):
            grid[y, x] = logProbabilityF(cardinality, runcount, Nbits)

    return grid, cvec, rvec


def grid_analytical_log_sampled(M, width):
    grid = np.zeros((width/2, width))
    cvec = range(0, M, M/width)
    rvec = range(0, M/2, M/width)
    for x, cardinality in enumerate(cvec):
        print(cardinality)
        for y, runcount in enumerate(rvec):
            grid[y, x] = logF(cardinality, runcount, M)

    return grid, cvec, rvec


def grid_analytical_exact(Nbits):
	# compute full grid for Nbits. will be slow for Nbits > 2^10 or so
    grid = np.zeros((Nbits/2, Nbits))
    cvec = range(1, Nbits+1)
    rvec = range(1, Nbits/2+1)
    for cardinality in cvec:
        for runcount in rvec:
            grid[runcount-1, cardinality-1] = F(cardinality, runcount, Nbits)

    return grid, cvec, rvec


## computation functions for heatmaps (stochastic, brute-force)

def grid_stochastic_large(Nbits, Niter, density=None, Nset=None):
    # for roaring-sized Nbits, can't use a grid
    # also return the x, y axis vectors
    result = Counter()
    n_min, n_max = np.inf, -np.inf
    nr_min, nr_max = np.inf, -np.inf
    for k in range(Niter):
        if density:
            bits = np.random.random(size=(Nbits,)) <= density
        elif Nset:
            # TODO use random permutation to set exactly Nset bits
            # this will show an actual marginal distribution - a 1d slice for N=Nset
            pass
        n = np.count_nonzero(bits)
        nr = countruns(bits)
        n_min = min(n_min, n)
        n_max = max(n_max, n)
        nr_min = min(nr_min, nr)
        nr_max = max(nr_max, nr)

        result[(nr, n)] += 1

    n_vec = np.arange(n_min, n_max+1)
    nr_vec = np.arange(nr_min, nr_max+1)

    grid = np.zeros((len(nr_vec), len(n_vec)))
    for (nr, n), count in result.items():
        grid[nr-nr_min, n-n_min] = count
    return grid, n_vec, nr_vec


def grid_stochastic(Nbits, Niter, density):
    # for moderately large Nbits, we have to sample
    # also return the x, y axis vectors
    grid = np.zeros((Nbits/2+1, Nbits+1))
    for k in range(Niter):
        bits = np.random.random(size=(Nbits,)) <= density
        n = np.count_nonzero(bits)
        nr = countruns(bits)
        grid[nr, n] += 1

    return grid, range(0, Nbits+1), range(0, Nbits/2+1)


def grid_deterministic(Nbits=8, debug=False):
    # for small enough Nbits, we can check every possible set
    # also return the x, y axis vectors
    grid = np.zeros((Nbits/2+1, Nbits+1))
    vals = range(2**Nbits)
    for i in vals:
        bitstr = format(i, '08b')
        bits = np.array([1 if b == '1' else 0 for b in bitstr])
        n = sum(bits)
        nr = countruns(bits)
        grid[nr, n] += 1
        if debug:
            print('%3d %s %2d %d' % (i, bitstr, n, nr, array_encode(bits), rl_encode(bits)))

    return grid, range(0, Nbits+1), range(0, Nbits/2+1)


def array_encode(bits, bpe=3):
    a_vec = np.where(bits)
    encoded = []
    for a in a_vec:
        encoded.append(format(a, '03b'))
    return ' '.join(encoded)


def rl_encode(bits, bpe=3):
    pass
