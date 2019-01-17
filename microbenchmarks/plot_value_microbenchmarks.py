import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('value-benchmarks-2019-01.csv')


x1, y1 = [], []
x2, y2 = [], []
for n, r in df.iterrows():
    name = '%s-%s-%s' % (r['func'], r['depth'], r['sparsity'])
    if r['sparsity'] == 1:
        x1.append(name)
        y1.append(r['ns'])
    else:
        x2.append(name)
        y2.append(r['ns'])


plt.barh(x1, y1, label='dense')
plt.barh(x2, y2, label='sparse')
ax = plt.gca()
ax.set_xscale("log")
plt.legend()
plt.show()
