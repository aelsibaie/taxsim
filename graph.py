import taxsim
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from collections import OrderedDict

current_law_result_list = []
house_2018_result_list = []

for i in range(1, 10000):
    default_taxpayer = OrderedDict([('filing_status', 0),
                                    ('child_dep', 0),
                                    ('nonchild_dep', 0),
                                    ('ordinary_income1', 0),
                                    ('ordinary_income2', 0),
                                    ('business_income', 0),
                                    ('ss_income', 0),
                                    ('qualified_income', 0),
                                    ('401k_contributions', 0),
                                    ('medical_expenses', 0),
                                    ('sl_income_tax', 0),
                                    ('sl_property_tax', 0),
                                    ('interest_paid', 0),
                                    ('charity_contributions', 0),
                                    ('other_itemized', 0)])
    income = i * 100
    default_taxpayer['ordinary_income1'] = income

    current_law_result = taxsim.calc_federal_taxes(
        default_taxpayer,
        taxsim.current_law_policy
    )
    current_law_result_list.append(current_law_result)

    house_2018_result = taxsim.calc_house_2018_taxes(
        default_taxpayer,
        taxsim.house_2018_policy
    )
    house_2018_result_list.append(house_2018_result)

current_law_df = pd.DataFrame(current_law_result_list)
house_2018_df = pd.DataFrame(house_2018_result_list)

plt.style.use('ggplot')
fig = plt.figure()
ax = plt.axes()
ax.yaxis.set_major_formatter(FuncFormatter('{0:.0%}'.format))
ax.xaxis.set_major_formatter(FuncFormatter('${:,.0f}'.format))
ax.plot(
    current_law_df["gross_income"],
    current_law_df["avg_effective_tax_rate"],
    drawstyle='steps-pre',
    label='Current Law'
)
ax.plot(
    house_2018_df["gross_income"],
    house_2018_df["avg_effective_tax_rate"],
    drawstyle='steps-pre',
    label='House 2018 Proposal'
)
ax.legend(loc='upper left')
ax.set_title(
    'Average Effective Federal Income Tax Rate by Gross Income (Single Filers)'
    )
ax.set_xlabel('Gross Income')
ax.set_ylabel('Average Effective Tax Rate')
fig.set_size_inches(8, 4)
fig.savefig("./graphs/tax_rates.png", dpi=100)
