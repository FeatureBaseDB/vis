# second attempt
# these condition functions use proper mutually exclusive, collectively exhaustive conditions
# Cx = internal boundary conditions
# Ex = external boundary
# and they correspond between these six, for easy comparison
def array_cond_mutex(M=65536, MA=4096):
    # array
    def I_array(c, r):
        C1 = c <= 2 * r  # array-runs bound
        E2 = c >= r  # left impossible diagonal
        C3 = c <= MA  # array-bitmap bound
        return C1 and E2 and C3
    return I_array


def runs_cond_mutex(M=65536, MA=4096):
    # runs when there is no iarray region (full runs region)
    def I_runs(c, r):
        E4 = r >= 0  # bottom bound
        C5 = r <= MA/2  # runs-bitmap bound
        C1 = c > 2*r  # array-runs-bound
        E6 = c <= M-r+1  # right impossible diagonal
        return C1 and E4 and C5 and E6
    return I_runs


def bitmap_cond_mutex(M=65536, MA=4096):
    # bitmap when there is no iarray region (full bitmap region)
    def I_bitmap(c, r):
        C5 = r > MA/2  # runs-bitmap bound
        C3 = c > MA  # array-runs bound
        E2 = r <= c  # left impossible diagonal
        E6 = c <= M-r+1  # right impossible diagonal
        return E2 and C3 and C5 and E6
    return I_bitmap


# these are the equivalent of the above, but for the iarray case
def iarray_cond_mutex(M=65536, MA=4096):
    # iarray
    def I_iarray(c, r):
        C7 = c >= M-2*r  # iarray-runs bound
        C8 = c >= M-MA  # iarray-bitmap bounds
        E6 = c <= M-r+1  # right impossible diagonal
        return C7 and C8 and E6
    return I_iarray


def runs_cond_mutex_iarray(M=65536, MA=4096):
    # runs with iarray region (reduced runs region)
    def I_runs(c, r):
        E4 = r >= 0  # bottom bound
        C5 = r <= MA/2  # runs-bitmap bound
        C1 = c > 2*r  # array-runs-bound
        # E6 = c <= M-r+1  # right impossible diagonal
        C7 = c < M-2*r  # iarray-runs bound
        return C1 and E4 and C5 and C7
    return I_runs


def bitmap_cond_mutex_iarray(M=65536, MA=4096):
    # bitmap with iarray region (reduced bitmap region)
    def I_bitmap(c, r):
        C5 = r > MA/2  # runs-bitmap bound
        C3 = c > MA  # array-runs bound
        E2 = r <= c  # left impossible diagonal
        E6 = c <= M-r+1  # right impossible diagonal
        C8 = c < M-MA  # iarray-bitmap bound
        return E2 and C3 and C5 and E6 and C8
    return I_bitmap


cond_map = {
    'array': array_cond_mutex,
    'bitmap': bitmap_cond_mutex,
    'runs': runs_cond_mutex,
    'iarray': iarray_cond_mutex,
    'runs_iarray': runs_cond_mutex_iarray,
    'bitmap_iarray': bitmap_cond_mutex_iarray,
}


# first attempt - deprecated
# these condition functions all use non-equality comparisons, which isn't quite right
# shouldn't make a huge difference though
# I_array = indicator function for array region
def array_cond(M=65536, MA=4096):
    # array
    def I_array(c, r):
        return c < 2 * r and c > r and c < MA
    return I_array


def runs_cond(M=65536, MA=4096):
    # runs with iarray region (reduced runs region)
    def I_runs(c, r):
        return r <= MA/2 and c >= 2*r and c <= M-2*r
    return I_runs


def bitmap_cond(M=65536, MA=4096):
    # bitmap with iarray region (reduced runs region)
    def I_bitmap(c, r):
        return r > MA/2 and MA < c < M-MA and r < c < M - r
    return I_bitmap


def iarray_runs_cond(M=65536, MA=4096):
    # the region that is either iarray or runs, depending whether iarrays are allowed
    def I_iarray_runs(c, r):
        return c > M - 2 * r and r < MA/2 and c < M - r
    return I_iarray_runs


def iarray_bitmap_cond(M=65536, MA=4096):
    # the region that is either iarray or bitmap, depending whether iarrays are allowed
    def I_iarray_bitmap(c, r):
        return c > M-MA and r > MA/2 and c < M - r
    return I_iarray_bitmap