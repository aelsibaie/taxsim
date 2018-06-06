import os
import taxsim.taxsim as taxsim
import taxsim.misc_funcs as misc_funcs
import numpy as np
import pandas as pd
import copy
from collections import OrderedDict


def get_diff(taxpayer):
    taxpayer1 = copy.deepcopy(taxpayer)
    taxpayer2 = copy.deepcopy(taxpayer)

    taxpayer2["qualified_income"] = taxpayer2["qualified_income"] * 1.049236641 # from Kyle

    results1 = taxsim.calc_federal_taxes(taxpayer1, taxsim.current_law_policy, False)
    results2 = taxsim.calc_senate_2018_taxes(taxpayer2, taxsim.senate_2018_policy, False)

    return int(round(results1["gross_income"] - results1["tax_burden"])), int(round(results2["gross_income"] - results2["tax_burden"]))

def div(num, den):
    if den != 0:
        return num / den
    else:
        return 0


file_path = os.path.join("data", "county2015", "15incyallagi.csv")

data = pd.read_csv(file_path)

# drop negative or 0 dollar taxpayers
data = data[data["AGI_STUB"] != 1]

# drop state aggregates
data = data[data["COUNTYFIPS"] != 0]

results = []


for statefips in data["STATEFIPS"].unique():
    state_data = data[data["STATEFIPS"] == statefips]

    for countyfips in state_data["COUNTYFIPS"].unique():
        county_data = state_data[state_data["COUNTYFIPS"] == countyfips]

        for agi_stub in county_data["AGI_STUB"].unique():
            sub_data = county_data[county_data["AGI_STUB"] == agi_stub]

            # misc
            state_name = str(sub_data.iloc[0]["STATE"])
            county_name = str(sub_data.iloc[0]["COUNTYNAME"])


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


            # set to share of AGI
            agi = float(div(sub_data["A00100"], number_rets)) * 1000
            our_total = wages + taxable_int + ord_div + qual_div + capgains + bus_inc + part_scorp_inc
            wages_shr = div(wages, our_total)
            taxable_int_shr = div(taxable_int, our_total)
            ord_div_shr = div(ord_div, our_total)
            qual_div_shr = div(qual_div, our_total)
            capgains_shr = div(capgains, our_total)
            bus_inc_shr = div(bus_inc, our_total)
            part_scorp_inc_shr = div(part_scorp_inc, our_total)

            # ordinary income
            wages = wages_shr * agi
            taxable_int = taxable_int_shr * agi
            ord_div = ord_div_shr * agi

            # qualified income
            qual_div = qual_div_shr * agi
            capgains = capgains_shr * agi
            
            # business income
            bus_inc = bus_inc_shr * agi
            part_scorp_inc = part_scorp_inc_shr * agi



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
            sng_itm_taxpayer["sl_income_tax"] = sl_income_sales * 0.5
            sng_itm_taxpayer["sl_property_tax"] = sl_prop * 0.5
            sng_itm_taxpayer["interest_paid"] = int_paid * 0.5
            sng_itm_taxpayer["charity_contributions"] = charity * 0.5

            jnt_itm_taxpayer = copy.deepcopy(sng_itm_taxpayer)
            jnt_itm_taxpayer["filing_status"] = 1
            jnt_itm_taxpayer["sl_income_tax"] = sl_income_sales
            jnt_itm_taxpayer["sl_property_tax"] = sl_prop
            jnt_itm_taxpayer["interest_paid"] = int_paid
            jnt_itm_taxpayer["charity_contributions"] = charity

            pre_sng_std, post_sng_std = get_diff(sng_std_taxpayer)
            pre_jnt_std, post_jnt_std = get_diff(jnt_std_taxpayer)
            pre_sng_itm, post_sng_itm = get_diff(sng_itm_taxpayer)
            pre_jnt_itm, post_jnt_itm = get_diff(jnt_itm_taxpayer)

            # weights

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
            
            # next weight by itemization status
            try:
                pre = np.average([pre_std, pre_itm], weights=std_to_itm)
                post = np.average([post_std, post_itm], weights=std_to_itm)
            except ZeroDivisionError:
                pre = 0
                post  = 0


            result = OrderedDict()
            result["state_name"] = state_name
            result["statefips"] = statefips
            result["county_name"] = county_name
            result["countyfips"] = countyfips
            result["agi_stub"] = agi_stub
            result["child_dep"] = avg_children
            result["avg_income_ALL"] = int(round(wages + taxable_int + ord_div + qual_div + capgains + bus_inc + part_scorp_inc))
            result["taxes_paid_ded"] = sl_income_sales + sl_prop
            result["pre"] = pre
            result["post"] = post

            results.append(result)

df = pd.DataFrame(results)
df.to_csv("data_county.csv", index=False)