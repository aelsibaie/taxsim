from . import taxsim
from . import misc_funcs

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from tqdm import tqdm


def gen_datasets():
    print("Generating datasets")
    policies = [
        (taxsim.calc_senate_2018_taxes, taxsim.senate_2018_policy, "tcja"),
        (taxsim.calc_federal_taxes, taxsim.current_law_policy, "pre-tcja")
    ]
    for tax_calc_function, policy_object, name in tqdm(policies):
        for CHILDREN in tqdm(range(0, 3), leave=False):

            PERCENTAGE_PRECISION = 4
            INCOME_UPPER_BOUND = 6
            INCOME_LOWER_BOUND = 4
            DATASET_SIZE = 400  # aka the resolution (default 400)

            list_of_columns = []
            # This loop is for horizontal rows
            for total_income in tqdm(np.logspace(INCOME_LOWER_BOUND, INCOME_UPPER_BOUND, num=DATASET_SIZE, base=10, dtype='int', endpoint=True), leave=False):
                total_income = float(total_income)
                column = []

                # This loop is for vertical columns
                for i in range(0, DATASET_SIZE):

                    # Split incomes
                    ratio = (i / (DATASET_SIZE - 1)) / 2  # Ratios range from 0.0 to 0.5
                    income1 = total_income * (1 - ratio)
                    income2 = total_income * ratio
                    assert math.isclose(income1 + income2, total_income)  # Helpful, but optional

                    # Create married taxpayer
                    married_taxpayer = misc_funcs.create_taxpayer()
                    married_taxpayer['filing_status'] = 1
                    married_taxpayer['child_dep'] = CHILDREN
                    married_taxpayer['ordinary_income1'] = income1
                    married_taxpayer['ordinary_income2'] = income2
                    married_results = tax_calc_function(married_taxpayer, policy_object, mrate=False)

                    married_tax_burden = married_results['tax_burden']

                    # Create single taxpayers
                    if CHILDREN == 0:
                        single_taxpayer1_nokids = misc_funcs.create_taxpayer()
                        single_taxpayer1_nokids['filing_status'] = 0
                        single_taxpayer1_nokids['ordinary_income1'] = income1
                        single_result1 = tax_calc_function(single_taxpayer1_nokids, policy_object, mrate=False)

                        single_taxpayer2_nokids = misc_funcs.create_taxpayer()
                        single_taxpayer2_nokids['filing_status'] = 0
                        single_taxpayer2_nokids['ordinary_income1'] = income2
                        single_result2 = tax_calc_function(single_taxpayer2_nokids, policy_object, mrate=False)

                        unmarried_tax_burden = single_result1['tax_burden'] + single_result2['tax_burden']
                    # Separate logic if taxpayers have kids
                    else:
                        # Option A (Child with 1st taxpayer)
                        single_taxpayer1 = misc_funcs.create_taxpayer()
                        single_taxpayer1['filing_status'] = 2
                        single_taxpayer1['ordinary_income1'] = income1
                        single_taxpayer1['child_dep'] = CHILDREN
                        single_result1 = tax_calc_function(single_taxpayer1, policy_object, mrate=False)

                        single_taxpayer2 = misc_funcs.create_taxpayer()
                        single_taxpayer2['filing_status'] = 0
                        single_taxpayer2['ordinary_income1'] = income2
                        single_result2 = tax_calc_function(single_taxpayer2, policy_object, mrate=False)

                        option_a = single_result1['tax_burden'] + single_result2['tax_burden']

                        # Option B (Child with 2nd taxpayer)
                        single_taxpayer3 = misc_funcs.create_taxpayer()
                        single_taxpayer3['filing_status'] = 0
                        single_taxpayer3['ordinary_income1'] = income1
                        single_result3 = tax_calc_function(single_taxpayer3, policy_object, mrate=False)

                        single_taxpayer4 = misc_funcs.create_taxpayer()
                        single_taxpayer4['filing_status'] = 2
                        single_taxpayer4['ordinary_income1'] = income2
                        single_taxpayer4['child_dep'] = CHILDREN
                        single_result4 = tax_calc_function(single_taxpayer4, policy_object, mrate=False)

                        option_b = single_result3['tax_burden'] + single_result4['tax_burden']

                        if CHILDREN == 2:
                            # Option C (Children split evenly)
                            single_taxpayer5 = misc_funcs.create_taxpayer()
                            single_taxpayer5['filing_status'] = 2
                            single_taxpayer5['ordinary_income1'] = income1
                            single_taxpayer5['child_dep'] = 1
                            single_result5 = tax_calc_function(single_taxpayer5, policy_object, mrate=False)

                            single_taxpayer6 = misc_funcs.create_taxpayer()
                            single_taxpayer6['filing_status'] = 2
                            single_taxpayer6['ordinary_income1'] = income2
                            single_taxpayer6['child_dep'] = 1
                            single_result6 = tax_calc_function(single_taxpayer6, policy_object, mrate=False)

                            option_c = single_result5['tax_burden'] + single_result6['tax_burden']
                        else:
                            option_c = option_b

                        # Pick the better option
                        unmarried_tax_burden = min(option_a, option_b, option_c)

                    penalty = married_tax_burden - unmarried_tax_burden
                    penalty_percent = penalty / total_income

                    penalty_percent = round(penalty_percent, PERCENTAGE_PRECISION)

                    column.append(penalty_percent)

                list_of_columns.append(column)

            df = pd.DataFrame(list_of_columns)
            df = df.transpose()
            df.to_csv("results/marriage_penalty/" + name + "_" + str(CHILDREN) + "children.csv", index=False, header=False)


def plot_datasets():
    print("Plotting datasets")
    policy_names = ["tcja", "pre-tcja", "diff"]

    for policy in tqdm(policy_names):
        for children in tqdm(range(0, 3), leave=False):

            filename = "results/marriage_penalty/" + policy + "_" + str(children) + "children"

            data = pd.read_csv(filename + ".csv")

            fig = plt.figure()
            ax = plt.axes()
            ax.grid(False)
            # ax.xaxis.tick_top()
            # ax.xaxis.set_label_position('top')

            ax.set_xlabel('Combined Income')
            ax.set_ylabel('Income Split')

            plt.imshow(data, cmap='seismic', vmin=-0.12, vmax=0.12, origin='upper')
            plt.colorbar()

            plt.title(policy + ", " + str(children) + " children")

            #fig.set_size_inches(18.5, 10.5)
            #plt.savefig(filename + ".png", format='png')
            plt.savefig(filename + ".svg", format='svg')
