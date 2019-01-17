import math
import numpy as np
from scipy.misc import comb


def max_array_size(M):
    """Compute the minimum possible value for ArrayMaxSize,
    in terms of M, the number of bits in the bitmap"""
    # - each element of the array requires ceil(log2(M)) bits
    # - the bitmap uses M bits
    # - when N * ceil(log2(M)) > M, array is too big
    # max_array_size is when N > M/ceil(log2(M))
    return int(np.floor(M/np.ceil(np.log2(M))))


def F(card, runs, M):
    """Compute the total number of bitmaps with M bits,
    cardinality card, runCount runs. 
    Returns exact result as long type

    # https://math.stackexchange.com/questions/2391769/what-is-the-number-of-binary-strings-of-length-n-with-exactly-r-runs-of-ones-wi
    """
    if card == 0 and runs == 0:
        return 1

    if card == 0 or runs == 0:
        return 0

    if runs > card:
        return 0

    if runs > M-card+1:
        return 0

    return comb(card-1, runs-1, exact=True) * comb(M-card+1, runs, exact=True)


def logProbabilityF(card, runs, nbits):
    # compute log probability:
    # log(F/2**Nbits)
    # log(F) - Nbits*log(2)
    x = F(card, runs, nbits)
    if x == 0:
        return np.NAN
    return math.log10(x) - nbits * np.log10(2)


# logsum is a cache for logcomb
logs = np.log10(range(1, 65536+1))
logs = np.insert(logs, 0, 0)
logsum = np.cumsum(logs)      # log(factorial(n)) = logsum[n]


def logcomb(n, k):
    """Compute binomial coefficient in logarithmic domain"""
    return logsum[n] - logsum[k] - logsum[n-k]


def logF(card, runs, M):
    """Compute the total number of bitmaps with M bits,
    and cardinality card, runCount runs. 
    Returns approximate result as log10 exponent."""
    if card == 0 and runs == 0:
        return 0

    if card == 0 or runs == 0:
        return -np.inf

    if runs > card:
        return -np.inf

    if runs > M-card+1:
        return -np.inf

    return logcomb(card-1, runs-1) + logcomb(M-card+1, runs)


def logF_nocheck(card, runs, M):
    return logcomb(card-1, runs-1) + logcomb(M-card+1, runs)


min_digit_dif = 13            # if log(y/x) > min_digit_dif, then y >> x, and x+y = y


def large_log_sum(x, y):
    # computes log10(10**x + 10**y), for very large values of x, y
    # if y >> x, then x+y is approximately y
    # if x and y are comparable:
    # 
    # rewrite log10(10**x + 10**y) as y + log10(1 + 10 ** (x-y))
    # only one exponentiation, no long
    #
    # min_digit_dif determines how many digits are preserved. 2 or 3 would be enough,
    # but there isn't really a drawback of using more, as long as it fits in a float
    if x == -np.inf and y == -np.inf:
        return -np.inf

    if x > y:
        x, y = y, x

    if y - x > min_digit_dif:
        return y
    else:
        return y + math.log10(1 + 10 ** (x-y))

    """ 
    # log10(10**x + 10**y)  # overflows
    # log10(10**long(x) + 10**long(y))  # casts a float to int and loses up to an order of magnitude of precision
    # so, we split the exponent into long and float parts. but this requires 4 exponentiations

        d = 10
        xi = math.floor(x)  # integer part of x
        xf = x - xi         # fractional part of x
        yi = math.floor(y)
        yf = y - yi
        return math.log10(10 ** long(xi-d) * long(10 ** (xf+d)) + 10 ** long(yi-d) * long(10 ** (yf+d)))
    """


def large_log_sum_vec(x):
    s = x[0]
    for z in x[1:]:
        s = large_log_sum(s, z)
    return s


def large_log_sum_array(x):
    y = np.zeros((x.shape[1],))
    for n in range(x.shape[1]):
        y[n] = large_log_sum_vec(x[:, n])
    return y