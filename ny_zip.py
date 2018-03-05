import os
import taxsim.taxsim as taxsim
import taxsim.misc_funcs as misc_funcs
import pandas as pd
import copy
from collections import OrderedDict

file_path1 = os.path.join('data', 'ny_zip', '75-100.csv')
file_path2 = os.path.join('data', 'ny_zip', '100-200.csv')

df1 = pd.read_csv(file_path1)
df2 = pd.read_csv(file_path2)

'''
    Married-Joint, Two Dependents Under 17
    Married-Joint, One Dependent Under 17
    Married-Joint, No Dependents
    Single, No Dependents
'''

datasets = [df1, df2]

dataset_num = 0

for dataset in datasets:

    dataset_num += 1

    for FILING_STATUS in [0, 1]:  # single or married

        if FILING_STATUS == 1:
            max_kids = 2
        else:
            max_kids = 0

        for NUMBER_KIDS in range(max_kids + 1):


            all_results = []

            for input_taxpayer in dataset.itertuples():
                row_results = OrderedDict()

                taxpayer = misc_funcs.create_taxpayer()
                taxpayer["filing_status"] = FILING_STATUS
                taxpayer["child_dep"] = NUMBER_KIDS
                taxpayer["ordinary_income1"] = input_taxpayer.AGI
                taxpayer["sl_income_tax"] = input_taxpayer.SLIncomeTax
                taxpayer["sl_property_tax"] = input_taxpayer.PropertyTax
                taxpayer["interest_paid"] = input_taxpayer.MortgageInterest
                taxpayer["charity_contributions"] = input_taxpayer.Contributions

                taxpayer1 = copy.deepcopy(taxpayer)
                taxpayer2 = copy.deepcopy(taxpayer)

                results1 = taxsim.calc_federal_taxes(taxpayer1, taxsim.current_law_policy, False)
                results2 = taxsim.calc_senate_2018_taxes(taxpayer2, taxsim.senate_2018_policy, False)

                row_results["zip"] = input_taxpayer.Zip
                row_results["Filers"] = input_taxpayer.Filers
                row_results["Itemizers"] = input_taxpayer.Itemizers
                row_results["AGI"] = input_taxpayer.AGI
                row_results["pre-tcja-tax"] = results1["income_tax_after_credits"]
                row_results["current-law-tax"] = results2["income_tax_after_credits"]

                all_results.append(row_results)

            result_df = pd.DataFrame(all_results)

            if FILING_STATUS == 1:
                FILING_STATUS_STR = "MARRIED"
            else:
                FILING_STATUS_STR = "SINGLE"

            if dataset_num == 1:
                DATASET_STR = "75-100"
            else:
                DATASET_STR = "100-200"

            filename = "filingstatus" + str(FILING_STATUS_STR) + "_children" + str(NUMBER_KIDS) + "_dataset" + str(DATASET_STR) + ".csv"  # lol
            filepath = os.path.join('results', 'ny_zip', filename)

            result_df.to_csv(filepath)