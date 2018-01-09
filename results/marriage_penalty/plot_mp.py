import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm import tqdm



policies = ["tcja", "currentlaw"]

for policy in tqdm(policies, leave=True):
    for children in tqdm(range(0, 3), leave=False):


        filename = policy + "_" + str(children) + "children"

        data = pd.read_csv(filename + ".csv")

        fig = plt.figure()
        ax = plt.axes()
        # ax.xaxis.tick_top()
        # ax.xaxis.set_label_position('top')

        ax.set_xlabel('Combined Income')
        ax.set_ylabel('Income Split')

        plt.imshow(data, cmap='seismic', vmin=-0.06, vmax=0.06, interpolation='none', origin='upper')
        plt.colorbar()

        plt.title(policy + ", " + str(children) + " children")

        plt.savefig(filename + ".png", dpi=100, format='png')
        #plt.savefig(filename + ".svg", dpi=100, format='svg')

# plt.show()
