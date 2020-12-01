import os
import taxsim.taxsim as taxsim
import taxsim.misc_funcs as misc_funcs
import numpy as np
import pandas as pd
import copy
#from collections import OrderedDict
#import json


def get_diff(taxpayer):
    taxpayer1 = copy.deepcopy(taxpayer)
    taxpayer2 = copy.deepcopy(taxpayer)

    results1 = taxsim.calc_federal_taxes(taxpayer1, taxsim.current_law_policy, False)
    results2 = taxsim.calc_senate_2018_taxes(taxpayer2, taxsim.senate_2018_policy, False)

    return int(round(results1["income_tax_after_credits"])), int(round(results2["income_tax_after_credits"]))

def div(num, den):
    if den != 0:
        return num / den
    else:
        return 0


file_path = os.path.join("data", "county2015", "15incyallagi.csv")

data = pd.read_csv(file_path)

data = data[data["AGI_STUB"] != 1]


for statefips in data["STATEFIPS"].unique():
    state_data = data[data["STATEFIPS"] == statefips]

    for countyfips in state_data["COUNTYFIPS"].unique():
        county_data = state_data[state_data["COUNTYFIPS"] == countyfips]

        for agi_stub in county_data["AGI_STUB"].unique():
            sub_data = county_data[county_data["AGI_STUB"] == agi_stub]

            # demographics
            number_rets = int(sub_data["N1"])
            number_single = int(sub_data["MARS1"])
            number_joint = int(sub_data["MARS2"]) 
            number_hoh = int(sub_data["MARS4"])
            number_itemizers = int(sub_data["N04470"])
            number_dep = int(sub_data["NUMDEP"])
            avg_children = min(3, int(round(div(number_dep, (number_joint + number_hoh)))))

            # ordinary income
            wages = float(div(sub_data["A00200"], number_rets)) * 1000
            taxable_int = float(div(sub_data["A00300"], number_rets)) * 1000
            ord_div = float(div(sub_data["A00600"], number_rets)) * 1000

            # qualified income
            qual_div = float(div(sub_data["A00650"], number_rets)) * 1000
            capgains = float(div(sub_data["A01000"], number_rets)) * 1000
            
            # business income
            bus_inc = float(div(sub_data["A00900"], number_rets)) * 1000
            part_scorp_inc = float(div(sub_data["A26270"], number_rets)) * 1000

            # deductions
            sl_income_sales = float(div(sub_data["A18425"] + sub_data["A18450"], number_itemizers)) * 1000
            sl_prop = float(div(sub_data["A18500"], number_itemizers)) * 1000
            int_paid = float(div(sub_data["A19300"], number_itemizers)) * 1000
            charity = float(div(sub_data["A19700"], number_itemizers)) * 1000


            # construct taxpayers
            single_filing_status = 0
            if avg_children != 0:
                single_filing_status = 2
            
            sng_std_taxpayer = misc_funcs.create_taxpayer()
            sng_std_taxpayer["filing_status"] = single_filing_status
            sng_std_taxpayer["child_dep"] = avg_children
            sng_std_taxpayer["ordinary_income1"] = wages + taxable_int + ord_div
            sng_std_taxpayer["qualified_income"] = qual_div + capgains
            sng_std_taxpayer["business_income"] = bus_inc + part_scorp_inc

            jnt_std_taxpayer = copy.deepcopy(sng_std_taxpayer)
            jnt_std_taxpayer["filing_status"] = 1

            sng_itm_taxpayer = copy.deepcopy(sng_std_taxpayer)
            sng_itm_taxpayer["sl_income_tax"] = sl_income_sales
            sng_itm_taxpayer["sl_property_tax"] = sl_prop
            sng_itm_taxpayer["interest_paid"] = int_paid
            sng_itm_taxpayer["charity_contributions"] = charity

            jnt_itm_taxpayer = copy.deepcopy(sng_itm_taxpayer)
            jnt_itm_taxpayer["filing_status"] = 1

            pre_sng_std, post_sng_std = get_diff(sng_std_taxpayer)
            pre_jnt_std, post_jnt_std = get_diff(jnt_std_taxpayer)
            pre_sng_itm, post_sng_itm = get_diff(sng_itm_taxpayer)
            pre_jnt_itm, post_jnt_itm = get_diff(jnt_itm_taxpayer)

            sng_to_jnt = [number_single + number_hoh, number_joint]
            std_to_itm = [number_rets - number_itemizers, number_itemizers]

            # first weight by filer status
            try:
                pre_itm = np.average([pre_sng_itm, pre_jnt_itm], weights=sng_to_jnt)
                post_itm = np.average([post_sng_itm, post_jnt_itm], weights=sng_to_jnt)
                pre_std = np.average([pre_sng_std, pre_jnt_std], weights=sng_to_jnt)
                post_std = np.average([post_sng_std, post_jnt_std], weights=sng_to_jnt)
            except ZeroDivisionError:
                pre_itm = 0
                post_itm = 0
                pre_std = 0
                post_std = 0