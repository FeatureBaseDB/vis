import pandas as pd
import matplotlib.pyplot as plt
import re

# PLOT, PNG = True, False
# PLOT, PNG = False, True
PLOT, PNG = False, False
screen = 3840, 2160
dpi = 300  # 100 -> 640x480 from default figure size
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

fname = 'csv/allresults-20190201.csv'
df = pd.read_csv(fname)


def truncate(s, maxlen=100):
    if len(s) > maxlen:
        s = s[0:50] + '...' + s[-50:]
    return s


def slugify(s):
    s = s.lower()
    if s.startswith('the '):
        s = s[4:]
    s = re.sub('[ _]', '-', s)
    s = re.sub('[^0-9a-z\-]', '', s)
    return s

ignore_instance_list = ['F16']


def main():
    m = 0
    for title in df['Benchmark'].unique():
        bms = df[df['Benchmark'] == title].sort_values(by=['Mean'])
        # bms = bms[not bms['Instance Type/Shape'].contains('F16')]  # TODO this
        # print(m, title)
        if len(bms['Cloud'].unique()) == 1:
            # print('  skipping single-cloud')
            continue

        # compute scale
        min_val = bms['Mean'].min()
        scale, prefix = units[0]
        if min_val > 1e2:
            scale, prefix = units[1]
        if min_val > 1e5:
            scale, prefix = units[2]
        if min_val > 1e8:
            scale, prefix = units[3]
        value_label = prefix + 's/operation (mean)'

        # group by cloud
        bars = {'AWS': ([], []), 'Azure': ([], []), 'OCI': ([], [])}
        names = []
        k = 0
        for n, r in bms.iterrows():
            instance = r['Instance Type/Shape']

            # TODO do this via pandas outside the loop
            skip = False
            for s in ignore_instance_list:
                if s in instance:
                    skip = True
                    # print('skipping %s in %s' % (s, instance))
            if skip:
                continue

            bars[r['Cloud']][0].append(k)
            bars[r['Cloud']][1].append(scale*r['Mean'])
            name = '%s x %d' % (instance, r['Cluster size'])
            names.append(name)
            k += 1

        # plot
        fig = plt.figure()
        if title.startswith('Benchmark'):
            title.replace('Benchmark', '')
        plt.title(title)
        mang = plt.get_current_fig_manager()
        mang.window.setGeometry(20, 20, screen[0]/3, screen[1]/2)

        for cloud, (x, y) in bars.items():
            plt.barh(x, y, color=color_map[cloud], label=cloud)
        plt.yticks(range(len(bms)), names)
        plt.ylabel('Instance Type')
        plt.xlabel(value_label)
        ax = plt.gca()
        ax.yaxis.grid(False)
        ax.set_position([0.3, 0.15, 0.6, 0.75])
        plt.legend()

        img_file = 'png-all/' + truncate(slugify(title)) + '.png'
        print('    <div class=box><a href="%s"><img src="%s"><p>%s</p></a></div>' % (img_file, img_file, title))
        if PNG:
            plt.savefig(img_file, dpi=dpi)

        if PLOT and m > 126:
            plt.show()
            # debug()

        plt.close(fig)
        m += 1

main()
