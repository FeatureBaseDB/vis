from compute import grid_analytical_exact

Nbits, density = 32, .5
grid, x, y = grid_analytical_exact(Nbits)
z = grid
for r in grid:
    m = ''
    for c in r:
        m += '%4d ' % int(c)
    print(m)
