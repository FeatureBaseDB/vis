import pandas as pd
import matplotlib.pyplot as plt

PLOT = True
PNG = True
mode = 'horizontal'  # direction of bars, text labels
dpi = 600  # 100 -> 640x480 from default figure size
color_map = {  # inspired by HO's mockup
    'AWS': '#fd8705',
    'OCI': '#f20007',
    'Azure': '#2f60ce',
    'GCP': '#4cb944',   # '#6eeb83'
    # 'IBM': '#5f0f40',
}
# https://coolors.co/f20007-2f60ce-fd8705-5f0f40-4cb944
# https://coolors.co/f20007-2f60ce-fd8705-6eeb83-5f0f40

datas = [
    # scale_index: manually select units prefix
    # value_min: for a truncated axis
    # value_field: which field from the CSV to use as bar lengths
    # value_label: axis label for the value
    {
        'file': 'intersection-count.csv',
        'title': 'IntersectionCount Benchmark (CPU Intensive)',
        'value_min': 3,
        'scale_index': 1,
    },
    {
        'file': 'import-concurrent.csv',
        'title': 'ImportRoaringConcurrent Benchmark (CPU and I/O Intensive)',
    },
    {
        'file': 'filewrite.csv',
        'title': 'FileWrite Benchmark (I/O Intensive)',
    },
    {
        'file': '29seg.csv',
        'title': 'Big Segmentation',
    },
    {
        'file': 'raw-query-perf.csv',
        'title': 'Raw Query Performance',
    },
    {
        'file': '29seg-dpmq.csv',
        'title': 'Cost per Megaquery for Segmentation Benchmark',
        'scale_index': 0,
        'value_field': 'dpmq',
        'value_label': '$/Megaquery',
    },
    {
        'file': 'filtered-topn-dpmq.csv',
        'title': 'Cost per Megaquery for Filtered TopN Benchmark',
        'scale_index': 0,
        'value_field': 'dpmq',
        'value_label': '$/Megaquery',
    },
    {
        'file': 'groupby-dpmq.csv',
        'title': 'Cost per Megaquery for GroupBy Benchmark',
        'scale_index': 0,
        'value_field': 'dpmq',
        'value_label': '$/Megaquery',
    },
]

# 'mean' values are already in nanoseconds
units = [
    (1.0, 'n'),
    (1e-3, 'μ'),
    (1e-6, 'm'),
    (1e-9, ''),  # default
]

for data in datas:
    df = pd.read_csv('csv/' + data['file'])

    # handle some special cases
    value_field = 'mean'
    scale, prefix = units[2]
    if 'scale_index' in data:
        scale, prefix = units[data['scale_index']]

    value_label = prefix + 's/operation (mean)'
    if 'value_label' in data:
        value_label = data['value_label']
    value_label += '\n(lower is better)'

    if 'value_field' in data:
        value_field = data['value_field']

    # plot stuff
    bars = {'AWS': ([], []), 'Azure': ([], []), 'OCI': ([], [])}
    names = []
    for n, r in df.iterrows():
        bars[r['cloud']][0].append(n)
        bars[r['cloud']][1].append(scale*r[value_field])
        names.append(r['instance_type'])

    plt.figure()
    plt.title(data['title'])
    if mode == 'vertical':
        for cloud, (x, y) in bars.items():
            plt.bar(x, y, color=color_map[cloud], label=cloud)
        plt.xticks(range(len(df)), names, rotation=90)
        plt.xlabel('Instance Type')
        plt.ylabel(value_label)
        if 'value_min' in data:
            # TODO draw broken lines on truncated axis: https://matplotlib.org/examples/pylab_examples/broken_axis.html
            lims = plt.ylim()
            plt.ylim([data['value_min'], lims[1]])
        ax = plt.gca()
        ax.xaxis.grid(False)
        ax.set_position([0.15, 0.3, 0.75, 0.6])
    elif mode == 'horizontal':
        for cloud, (x, y) in bars.items():
            plt.barh(x, y, color=color_map[cloud], label=cloud)
        plt.yticks(range(len(df)), names)
        plt.ylabel('Instance Type')
        plt.xlabel(value_label)
        if 'value_min' in data:
            # TODO broken lines here too
            lims = plt.xlim()
            plt.xlim([data['value_min'], lims[1]])
        ax = plt.gca()
        ax.yaxis.grid(False)
        ax.set_position([0.3, 0.15, 0.6, 0.75])

    plt.legend()
    img_file = 'png/' + data['file'][:-4] + '-' + mode + '.png'
    if PNG:
        plt.savefig(img_file, dpi=dpi)

if PLOT:
    plt.show()

