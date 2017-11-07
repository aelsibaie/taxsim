from bokeh.charts import Step, show, output_file
import pandas as pd
from collections import OrderedDict
import taxsim


current_law_result_list = []
house_2018_result_list = []

for i in range(1, 1000):
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
    income = i * 1000
    default_taxpayer['ordinary_income1'] = income
    current_law_result = taxsim.calc_federal_taxes(default_taxpayer, taxsim.current_law_policy)
    current_law_result_list.append(current_law_result)
    house_2018_result = taxsim.calc_house_2018_taxes(default_taxpayer, taxsim.house_2018_policy)
    house_2018_result_list.append(house_2018_result)

current_law_df = pd.DataFrame(current_law_result_list)
house_2018_df = pd.DataFrame(house_2018_result_list)

plot = Step(current_law_df, x='gross_income',
            y='avg_effective_tax_rate',
            color='deduction_type',
            title="avg_effective_tax_rate by gross_income",
            xlabel="gross_income",
            ylabel="avg_effective_tax_rate",
            plot_width=800,
            plot_height=400)
output_file("current_law_avg_effective_tax_rates.html")
show(plot)

plot = Step(house_2018_df, x='gross_income',
            y='avg_effective_tax_rate',
            color='deduction_type',
            title="avg_effective_tax_rate by gross_income",
            xlabel="gross_income",
            ylabel="avg_effective_tax_rate",
            plot_width=800,
            plot_height=400)
output_file("house_2018_avg_effective_tax_rates.html")
show(plot)
