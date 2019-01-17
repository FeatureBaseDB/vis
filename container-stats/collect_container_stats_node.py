import subprocess
import os
import random

"""
/<index>/views/<frame>/fragments/<fragmentID>
/<index>/views/<frame>/fragments/<fragmentID>.cache
<index>-<frame>/standard-fragment-<fragmentID>.txt

/<index>/views/field_<field>/fragments/<fragmentID>
/<index>/views/field_<field>/fragments/<fragmentID>.cache
<index>-<frame>/field-<field>-<fragmentID>.txt
"""

index = 'ssb'
sample_rate = 0.1

data_dir = os.getenv('HOME') + '/pilosa'
index_dir = data_dir + '/' + index
output_dir = os.getenv('HOME') + '/container-stats'
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

print(index_dir)


for root, dirs, files in os.walk(index_dir):
    if 'fragments' in root:
        # print('%s - %d dirs, %d files' % (root, len(dirs), len(files)))
        parts = root.replace(index_dir+'/', '').split('/')
        subdir = '%s-%s' % (index, parts[0])

        if '/views/standard' in root:
            # /home/ubuntu/pilosa/ssb/s_region/views/standard/fragment
            ftype = 'standard'
            fname_prefix = '%s/standard' % (subdir)

        if '/views/field_' in root:
            # /home/ubuntu/pilosa/ssb/lo_profit/views/field_lo_profit/fragments
            ftype = 'bsi'
            fname_prefix = '%s/%s' % (subdir, parts[2])

        print('  %s: %s - %d files' % (ftype, fname_prefix, len(files)))
        if not os.path.exists(output_dir + '/' + subdir):
            os.mkdir(output_dir + '/' + subdir)

        for file in files:

            if 'cache' in file:
                continue
            if random.random() > sample_rate:
                continue

            fin = '%s/%s' % (root, file)
            fout = '%s/%s-%s.txt' % (output_dir, fname_prefix, file)
            cmd = 'pilosa inspect %s > %s' % (fin, fout)
            print(cmd)
            subprocess.check_output(cmd, shell=True)
