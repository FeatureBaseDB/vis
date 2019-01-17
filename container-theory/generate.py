import numpy as np


def test_random():
    x = random_partition(100, 10)
    print(x)


def random_container(N, Nruns, Nbits=8):
    runs = []
    set_lengths = random_partition(N, Nruns, 0, 1)
    clear_lengths = random_partition(2**Nbits - N, Nruns, 1, 0)
    start = last = 0
    for i in range(Nruns):
        start = last + clear_lengths[i]
        last = start + set_lengths[i]
        runs.append([start, last])
    return runs


def random_partition(sum, num, first0=0, last0=0):
    # first0=1 means first element may be 0
    # last0=1 means last element may be 0
    # first0 last0 start end
    # 0      0     1     sum-1
    # 0      1     1     sum
    # 1      0     0     sum-1
    # 1      1     0     sum

    # generate distinct ints in [start, end]
    vals = np.random.permutation(sum - 1 + first0 + last0)[0:num-1]
    if first0 == 0:
        vals += 1

    # append 0 and sum, then sort
    print(vals)
    vals = np.append(vals, [0, sum])
    print(vals)
    vals.sort()
    print(vals)

    print(np.diff(vals))
    # return the diff
    return np.diff(vals)

