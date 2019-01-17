def get_bound_traces(M=65536, MA=4096, mode='iarray', color='rgb(255,0,0)', normalized=False):
    # compute endpoints that define lines that separate container regions
    # M, MA are max cardinality and max array size
    # mode is default 'iarray' in which case all four regions are computed, or '' for the basic three.
    # color is the line color, defaults to red
    # normalized is a boolean which should only be True if M=1.0, for normalized plots
    ofs = 1.0
    if normalized:
        ofs = 0.0

    MR = MA/2
    M1 = M+ofs
    MA1 = MA+ofs
    line = {'color': color}
    traces = [
        {'x': [0, M1/2], 'y': [0, M1/2], 'line': line, 'mode': 'lines'},  # left impossible diagonal
        {'x': [M1/2, M1], 'y': [M1/2, 0], 'line': line, 'mode': 'lines'},  # right impossible diagonal
        {'x': [0, MA], 'y': [0, MR], 'line': line, 'mode': 'lines'},  # array-run
        {'x': [MA, MA], 'y': [MR, MA], 'line': line, 'mode': 'lines'},  # array-bitmap
    ]

    if mode == 'iarray':
        traces += [
            {'x': [M-MA, M-MA], 'y': [MR, MA1], 'line': line, 'mode': 'lines'},  # iarray-bitmap (iarray)
            {'x': [MA, M-MA], 'y': [MR, MR], 'line': line, 'mode': 'lines'},  # run-bitmap (iarray)
            {'x': [M, M-MA], 'y': [0, MR], 'line': line, 'mode': 'lines'},  # iarray-run (iarray)
        ]

    else:
        traces += [
            {'x': [MA, M-MR], 'y': [MR, MR], 'line': line, 'mode': 'lines'},  # run-bitmap (no iarray)
        ]

    return traces