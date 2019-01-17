Python source for creating figures used in the Pilosa "Universe map" blog post.

# contents

## directories
- data/ - pickle files used to create figures without recomputing
- figures/ - html output from plotly

## modules
- definitions.py - basic math
- conditions.py - simple functions for identifying grid pixels with regions
- plot.py - plot helper functions
- compute.py - core computation stuff
- generate.py - port of the random container generation code from pilosa
- logfloat.py - attempt at encapsulating the "logarithmic representation"

## figure plotters
- figure_heatmap_bruteforce.py - attempt 1, enumerate all sets and count
- figure_heatmap_stochastic.py - attempt 2, monte carlo simulation
- figure_heatmap_stochastic_large.py - attempt 2b, monte carlo on too big of a space
- figure_heatmap_analytical.py - final version for M=65536
- figure_count_vs_n.py
- figure_count_vs_m.py

other files are miscellaneous exploration