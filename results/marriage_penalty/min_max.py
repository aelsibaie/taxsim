import pandas as pd
import numpy as np

for i in [0, 1, 2]:
    data1 = pd.read_csv("pre-tcja_" + str(i) + "children.csv").as_matrix()
    data2 = pd.read_csv("tcja_" + str(i) + "children.csv").as_matrix()

    print(str(i) + " children")
    print("pre-tcja")
    print(round(data1.max() * 100, 1))
    print(round(data1.min() * 100, 1))
    print("tcja")
    print(round(data2.max() * 100, 1))
    print(round(data2.min() * 100, 1))
    print("")

    #diff = np.subtract(data2, data1)

    #df = pd.DataFrame(diff)

    #df.to_csv("diff_" + str(i) + "children.csv")
