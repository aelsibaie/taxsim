import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm import tqdm



policies = ["tcja", "currentlaw"]

for policy in tqdm(policies, leave=True):
    for children in tqdm(range(0, 3), leave=False):

        filename = policy + "_" + str(children) + "children"

        data = pd.read_csv(filename + ".csv")

        x = np.logspace(4, 6, num=400, base=10, dtype='int', endpoint=True)

        x = ["$10k", "$20k", "$50k", "$100k", "$200k", "$500k", "$1M"]

        fig = plt.figure()

        ax = plt.axes()
        ax.xaxis.tick_top()
        plt.locator_params(nticks=7)

        ax.set_xticklabels(x)
        ax.set_xlabel('Combined Income')
        ax.set_ylabel('Income Split')

        plt.imshow(data, cmap='seismic', vmin=-0.06, vmax=0.06, interpolation='none', origin='upper')
        plt.colorbar()

        #plt.show()

        plt.savefig(filename + ".png")