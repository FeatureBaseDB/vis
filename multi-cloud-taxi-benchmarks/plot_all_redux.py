import pandas as pd
import matplotlib.pyplot as plt
import re

# PLOT, PNG = True, False
PLOT, PNG = False, True
# PLOT, PNG = True, True
# PLOT, PNG = False, False

# screen = 3840, 2160  # 4k
screen = 2880, 1800  # macbook

# display settings
dpi = 300  # 100 -> 640x480 from default figure size
figsize = (16, 8)  # inches
fontsize = 20
ax_width = 0.5

color_map = {  # inspired by HO's mockup
    'AWS': '#fd8705',
    'OCI': '#f20007',
    'Azure': '#2f60ce',
    'GCP': '#4cb944',   # '#6eeb83'
    # 'IBM': '#5f0f40',
}


units = [
    (1.0, 'n'),
    (1e-3, 'μ'),
    (1e-6, 'm'),
    (1e-9, ''),  # default
]

specs = [
    {
        'csv_fname': 'csv/raw-performance-all--benchmarks-QueryResult.csv',
        'value_field': 'mean',
        'value_label': '',
        'out_dir': 'redux-perf',
    }, {
        'csv_fname': 'csv/dpmq-all-queries-benchmarks-QueryResult.csv',
        'value_field': 'dpmq',
        'value_label': '$/Megaquery',
        'out_dir': 'redux-dpmq',
    }
]


def slugify(s):
    s = s.lower()
    if s.startswith('the '):
        s = s[4:]
    s = re.sub('[ _]', '-', s)
    s = re.sub('[^0-9a-z\-]', '', s)
    return s


def main(spec):
    df = pd.read_csv(spec['csv_fname'])
    m = 0
    for title in df['benchmark'].unique():
        # sort by value
        bms = df[df['benchmark'] == title].sort_values(by=[spec['value_field']])

        # compute scale
        min_val = bms[spec['value_field']].min()
        scale, prefix = units[0]
        if min_val > 1e2:
            scale, prefix = units[1]
        if min_val > 1e5:
            scale, prefix = units[2]
        if min_val > 1e8:
            scale, prefix = units[3]

        if spec['val_label']:
            # dpmq
            value_label = spec['val_label']
        else:
            # perf
            value_label = prefix + 's/operation (mean)'
        value_label += '\n(lower is better)'

        # group by cloud
        bars = {'AWS': ([], []), 'Azure': ([], []), 'OCI': ([], []), 'GCP': ([], [])}
        names = []
        k = 0
        for n, r in bms.iterrows():
            instance = r['config'].replace('-ubuntu', '')

            bars[r['cloud']][0].append(k)
            bars[r['cloud']][1].append(scale*r[spec['value_field']])
            if title.startswith('Benchmark'):
                # single-fragment, don't care about cluster size
                name = instance
            else:
                name = '%s x %d' % (instance, r['cluster_size'])
            names.append(name)
            k += 1

        # plot
        fig = plt.figure(figsize=figsize)
        if len(title) > 200:
            # replace single long-PQL benchmark name with something descriptive
            title = '29-way Intersect'
        figtitle = title
        if len(title) > 50:
            # split medium-length names onto multiple lines, at comma
            ix = title.index(',', 20)
            figtitle = title[:ix+1] + '\n    ' + title[ix+1:]
        print(title)
        plt.title(figtitle, fontsize=fontsize)

        # place figure at specific location on screen
        # mang = plt.get_current_fig_manager()
        # mang.window.setGeometry(20, 20, screen[0]/2, screen[1]/2)

        for cloud, (x, y) in bars.items():
            plt.barh(x, y, color=color_map[cloud], label=cloud)
        plt.yticks(range(len(bms)), names, fontsize=16, rotation=0)
        plt.ylabel('Cluster Configuration', fontsize=fontsize)
        plt.xlabel(value_label, fontsize=fontsize)
        ax = plt.gca()
        ax.yaxis.grid(False)
        ax.set_position([.9-ax_width, 0.15, ax_width, 0.75])
        plt.legend(fontsize=fontsize)

        img_file = spec['dir_prefix'] + '/' + slugify(title) + '.png'
        # print('    <div class=box><a href="%s"><img src="%s"><p>%s</p></a></div>' % (img_file, img_file, title))
        if PNG:
            plt.savefig(img_file, dpi=dpi, bbox_inches='tight')

        if PLOT:
            plt.show()
            # debug()

        plt.close(fig)
        m += 1
        # break

main(specs[0])
# main(specs[1])
