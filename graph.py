import taxsim
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from collections import OrderedDict
from tqdm import tqdm

current_law_result_list = []
house_2018_result_list = []
senate_2018_result_list = []

for i in tqdm(range(1, 10000)):
    STEP = 10
    income = i * STEP
    default_taxpayer = OrderedDict([('filing_status', 1),
                                    ('child_dep', 2),
                                    ('nonchild_dep', 0),
                                    ('ordinary_income1', income * 0.50),
                                    ('ordinary_income2', 0),
                                    ('business_income', income * 0.25),
                                    ('ss_income', 0),
                                    ('qualified_income', income * 0.25),
                                    ('401k_contributions', 0),
                                    ('medical_expenses', 0),
                                    ('sl_income_tax', 0),
                                    ('sl_property_tax', 0),
                                    ('interest_paid', 0),
                                    ('charity_contributions', 0),
                                    ('other_itemized', 0)])
    current_law_result = taxsim.calc_federal_taxes(default_taxpayer, taxsim.current_law_policy)
    current_law_result_list.append(current_law_result)
    house_2018_result = taxsim.calc_house_2018_taxes(default_taxpayer, taxsim.house_2018_policy)
    house_2018_result_list.append(house_2018_result)
    senate_2018_result = taxsim.calc_senate_2018_taxes(default_taxpayer, taxsim.senate_2018_policy)
    senate_2018_result_list.append(senate_2018_result)

current_law_df = pd.DataFrame(current_law_result_list)
house_2018_df = pd.DataFrame(house_2018_result_list)
senate_2018_df = pd.DataFrame(senate_2018_result_list)

# Save CSVs
current_law_df.to_csv('current_law_graph_data.csv')
house_2018_df.to_csv('house_2018_graph_data.csv')
senate_2018_df.to_csv('senate_2018_graph_data.csv')

# Plot figure(s)
plt.style.use('ggplot')
fig = plt.figure()
ax = plt.axes()
ax.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))
ax.xaxis.set_major_formatter(FuncFormatter('${:,.0f}'.format))
ax.plot(current_law_df["gross_income"], current_law_df["avg_effective_tax_rate_wo_payroll"], drawstyle='steps-pre', label='Current Law')
ax.plot(house_2018_df["gross_income"], house_2018_df["avg_effective_tax_rate_wo_payroll"], drawstyle='steps-pre', label='House 2018 Proposal')
ax.plot(senate_2018_df["gross_income"], senate_2018_df["avg_effective_tax_rate_wo_payroll"], drawstyle='steps-pre', label='Senate 2018 Proposal')
ax.legend(loc='upper left')
ax.set_title('Avg Federal Income Tax Rate by Gross Income (business_income)')
ax.set_xlabel('Gross Income')
ax.set_ylabel('Avg Tax Rate (w/o payroll)')
fig.set_size_inches(12, 6)
fig.savefig("tax_rates.png", dpi=100)
