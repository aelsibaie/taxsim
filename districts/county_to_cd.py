import os
import numpy as np
import pandas as pd
import copy
from collections import OrderedDict


outputcd = pd.read_csv("OutputCD.csv")
outputcd["County"] = outputcd["County"].str[:-3]
#outputcd = outputcd[outputcd["StateCode"] != 2] remove alaska

county_data = pd.read_csv("data_county.csv")

#outputcd.to_csv("test.csv")


results = []


for state in outputcd["StateCode"].unique():
    state_df = outputcd[outputcd["StateCode"] == state]
    
    county_data_state = county_data[county_data["statefips"] == state]

    for cong_dist in state_df["CongressionalDistrict"].unique():
        cong_dist_df = state_df[state_df["CongressionalDistrict"] == cong_dist]

        # cong_dist is numerical CongressionalDistrict
        # state is numerical StateCode

        counties_in_cd = cong_dist_df["County"].unique()

        counties = []

        for county in counties_in_cd:

            # this is from the OutputCD, it is ONE series
            single_county_data_cd = cong_dist_df[cong_dist_df["County"] == county]
            wt = float(single_county_data_cd["PercentofCD"])

            # this is from the data_county.csv, it is 7 series (agi stubs 2-8)
            single_county_data = county_data_state[county_data_state["county_name"] == county]

            pre_post = []
            for agi_stub in single_county_data["agi_stub"].unique():
                myline = single_county_data[single_county_data["agi_stub"] == agi_stub]
                pre = float(myline["pre"])
                post = float(myline["post"])
                inc_all = float(myline["avg_income_ALL"])
                taxes_paid = float(myline["taxes_paid_ded"])
                pre_post.append((pre, post, inc_all, taxes_paid))

            counties.append((wt, pre_post))

        

        for i in range(0, 7):

            result = OrderedDict()
            
            wts = []
            nums_pre = []
            nums_post = []
            nums_inc = []
            nums_txpaid = []

            for y in range(len(counties)):
                try:
                    wts.append(counties[y][0])
                except IndexError: # match error
                    wts.append(0)

                try:
                    nums_pre.append(counties[y][1][i][0])
                except IndexError: # match error
                    nums_pre.append(0)

                try:
                    nums_post.append(counties[y][1][i][1])
                except IndexError:
                    nums_post.append(0)
                
                try:
                    nums_inc.append(counties[y][1][i][2])
                except IndexError: # match error
                    nums_inc.append(0)

                try:
                    nums_txpaid.append(counties[y][1][i][3])
                except IndexError:
                    nums_txpaid.append(0)
            
            pre = np.average(nums_pre, weights=wts)
            post = np.average(nums_post, weights=wts)
            avg_income_ALL = np.average(nums_inc, weights=wts)
            taxes_paid_ded = np.average(nums_txpaid, weights=wts)

            result["state_fips"] = state
            result["district"] = cong_dist
            result["income"] = i
            result["filing_status"] = 0
            result["child_dep"] = 0
            result["avg_income_ALL"] = round(avg_income_ALL)
            result["taxes_paid_ded"] = round(taxes_paid_ded)
            result["pre-tcja-tax"] = round(pre)
            result["current-law-tax"] = round(post)

            results.append(result)


df = pd.DataFrame(results)
df.to_csv("data.csv", index=False)