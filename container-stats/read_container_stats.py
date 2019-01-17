import subprocess
import string
import os
import pickle
from plotly.offline import plot
import plotly.graph_objs as go
from panda import debug


def main():
    data, title = get_taxi_data(), 'Taxi'
    # data, title = get_ssb_data(), 'SSB'  # I don't think I have this data anymore; requires SSB demo to be up
    plot_card_run_data(data, title)


def get_ssb_data():
    # output:
    # data = {
    #   'frame0': {
    #      'view0': [(N_0, NR_0), (N_1, NR_1), ...],
    #      'view1': ...,
    #   },
    #   'frame1': ...,
    # }
    data_path = 'container-stats'

    data = {}
    for root, dirs, files in os.walk(data_path):
        if root == data_path:
            continue
        parts = root.split('/')
        index_frame = parts[1]
        data[index_frame] = {'standard': []}
        print(root, len(dirs), len(files))
        for file in files:
            with open(root + '/' + file) as f:
                raw = f.read()
            file_data = read_inspect_output_v2(raw)
            card_runs = [(d['N'], d['RUNS']) for d in file_data]
            data[index_frame]['standard'] += card_runs

    return data


def get_taxi_data():
    # inspect_file('/Users/abernstein/.pilosa/taxi/pickup_grid_id/views/standard/fragments/11')
    fname = 'taxi-distribution.pickle'
    if os.path.exists(fname):
        print('loading data from pickle')
        with open(fname, 'r') as f:
            data = pickle.load(f)
    else:
        print('reading container stats from fragment files')
        data = get_card_run_data_for_index('taxi', '*', ['standard'])
        with open(fname, 'w') as f:
            pickle.dump(data, f)

    return data


def plot_card_run_data(data, title):
    # input:
    # groups of lists of (cardinality, runCount) pairs, structured like this:
    # data = {
    #   'frame0': {
    #      'view0': [(N_0, NR_0), (N_1, NR_1), ...],
    #      'view1': ...,
    #   },
    #   'frame1': ...,
    # }
    traces = []
    for k, v in data.items():
        print('%7s %s' % (len(v['standard']), k))
        xy = v['standard']
        xy = set(xy)
        traces.append({
            'x': [x[0] for x in xy],
            'y': [x[1] for x in xy],
            'name': k,
            'mode': 'markers',
        })

    line = {'color': 'rgb(0,255,0)'}

    M, MA, MR = 65536, 4096, 2048
    annotations = [
        go.Scatter(x=[0, M/2], y=[0, M/2], line=line, name='impossible-left'),
        go.Scatter(x=[M/2, M], y=[M/2, 0], line=line, name='impossible-right'),
        go.Scatter(x=[0, MA], y=[0, MR], line=line, name='array-run'),
        go.Scatter(x=[MA, MA], y=[MR, MA], line=line, name='array-bitmap'),
        # go.Scatter(x=[MA, M-MR], y=[MR, MR], line=line, name='run-bitmap (no iarray)'),
        go.Scatter(x=[M-MA, M-MA], y=[MR, MA], line=line, name='iarray-bitmap'),
        go.Scatter(x=[MA, M-MA], y=[MR, MR], line=line, name='run-bitmap'),
        go.Scatter(x=[M, M-MA], y=[0, MR], line=line, name='iarray-run'),
    ]
    traces += annotations

    layout = go.Layout(
        title='%s frame container distribution' % title,
        xaxis={'title': 'Cardinality'},
        yaxis={'title': 'runCount'},
    )

    fig = {'data': traces, 'layout': layout}
    plot(fig, filename='container-distribution.html')
    debug()

def read_inspect_output_v1(raw):
    # separating this function is useful because you can
    # transfer the `inspect` output rather than the entire file
    headers = True
    parsers = [int, int, str, int, int, int, str]
    data = []
    for line in raw.strip().split('\n'):
        if line.startswith('INDEX'):
            header_line = map(string.strip, line.split('\t'))
            headers = False
            continue

        if not headers:
            strs = map(string.strip, line.split('\t'))
            datum = {}
            for n in range(len(header_line)):
                datum[header_line[n]] = parsers[n](strs[n])

            data.append(datum)

        import ipdb; ipdb.set_trace()

    return data


def read_inspect_output_v2(raw):
    headers = True
    parsers = [int, str, int, int, int, str]
    data = []
    for line in raw.strip().split('\n'):
        if line.startswith('KEY'):
            header_line = map(string.strip, line.split('\t'))
            headers = False
            continue

        if not headers:
            strs = map(string.strip, line.split('\t'))
            datum = {}
            for n in range(len(header_line)):
                datum[header_line[n]] = parsers[n](strs[n])

            data.append(datum)

    return data


def inspect_file(fname):
    cmd = 'pilosa inspect %s' % fname
    print(cmd)
    out = subprocess.check_output(cmd, shell=True)
    return read_inspect_output(out)


def get_card_run_data_for_index(index, frames, views):
    # inputs:
    # - index
    # - list of frames (or '*' for all)
    # - list of views
    #
    # output
    # groups of lists of (cardinality, runCount) pairs, structured like this:
    # data = {
    #   'frame0': {
    #      'view0': [(N_0, NR_0), (N_1, NR_1), ...],
    #      'view1': ...,
    #   },
    #   'frame1': ...,
    # }
    pilosa_path = os.getenv('HOME') + '/.pilosa'
    index_path = pilosa_path + '/' + index

    data = {}
    for frame in os.listdir(index_path):
        frame_path = index_path + '/' + frame
        if not os.path.isdir(frame_path):
            print(' not dir')
            continue

        if frames != '*' and frame not in frames:
            print(' not in list')
            continue

        data[frame] = {}
        for view in views:
            fragment_path = frame_path + '/views/' + view + '/fragments'
            data[frame][view] = []
            for file in os.listdir(fragment_path):
                if 'cache' in file:
                    continue
                file_path = fragment_path + '/' + file
                datum = inspect_file(file_path)
                card_runs = [(d['N'], d['RUNS']) for d in datum]
                data[frame][view] += card_runs

    return data


if __name__ == '__main__':
    main()
