"""
This module processes county level data released by the IRS
Latest data files are located here: https://www.irs.gov/statistics/soi-tax-stats-county-data
"""

import os
import pandas
import logging
from tqdm import tqdm
from collections import OrderedDict

from . import taxsim
from . import misc_funcs

COUNTY_DATA_AGI = '15incyallagi.csv'
COUNTY_DATA_NOAGI = '15incyallnoagi.csv'

COUNTY_DATA_AGI = os.path.join('data', 'county2015', COUNTY_DATA_AGI)
COUNTY_DATA_NOAGI = os.path.join('data', 'county2015', COUNTY_DATA_NOAGI)


def process_county_data():
    """Process county level data using the tax calculator"""
    logging.info("Loading: " + COUNTY_DATA_AGI)
    data_agi = pandas.read_csv(COUNTY_DATA_AGI)

    logging.info("Loading: " + COUNTY_DATA_NOAGI)
    data_noagi = pandas.read_csv(COUNTY_DATA_NOAGI)

    # TODO: Merge the two datasets before running the calculator

    rows = []
    for row in tqdm(data_agi.itertuples()):
        row_calcs = OrderedDict()

        row_calcs['STATEFIPS'] = row.STATEFIPS
        row_calcs['STATE'] = row.STATE
        row_calcs['COUNTYFIPS'] = row.COUNTYFIPS
        row_calcs['COUNTYNAME'] = row.COUNTYNAME
        row_calcs['AGI_STUB'] = row.AGI_STUB

        '''
        Some notes on the variables in the 'row' object
            - All variables begining with 'N' represent the number of returns for a given attribute.
            - All variables begining with 'A' represent an amount of dollars for a given attribute.
            - For all the files, the money amounts are reported in thousands of dollars.
            - More info can be found in the doc file named 15incydocguide.doc
        '''

        # PROPORTIONS OF FILING STATUSES
        row_calcs['percent_single'] = div(row.MARS1, row.N1)
        row_calcs['percent_joint'] = div(row.MARS2, row.N1)
        row_calcs['percent_hoh'] = div(row.MARS4, row.N1)
        # percent_other may include filers who are married but filing separately
        # TODO: write test
        row_calcs['percent_other'] = max(0, 1 - row_calcs['percent_single'] - row_calcs['percent_joint'] - row_calcs['percent_hoh'])
        row_calcs['percent_elderly'] = div(row.ELDERLY, row.N1)
        row_calcs['percent_itemizing'] = div(row.N04470, row.N1)

        # CHILDREN
        row_calcs['number_children'] = div(row.NUMDEP, (row.MARS2 + row.MARS4))  # only divide by filing status' capable of having children
        row_calcs['rounded_children'] = round(row_calcs['number_children'], 0)

        # INCOMES
        row_calcs['taxable_ss_inc'] = div(row.A02500, row.N02500)  # only includes the taxable portion of SS income

        row_calcs['wage_inc'] = div(row.A00200, row.N00200)

        row_calcs['ordinary_div_inc'] = div(row.A00600, row.N00600)
        row_calcs['qual_div_inc'] = div(row.A00650, row.N00650)
        row_calcs['cap_gains_inc'] = div(row.A01000, row.N01000)  # unsure if long term cap gains

        row_calcs['partnership_scorp_inc'] = div(row.A26270, row.N26270)
        row_calcs['business_professional_inc'] = div(row.A00900, row.N00900)

        # DEDUCTIONS
        row_calcs['total_itemized'] = div(row.A04470, row.N04470)

        row_calcs['state_local_income'] = div(row.A18425, row.N04470)
        row_calcs['state_local_sales'] = div(row.A18450, row.N04470)
        # Pick either sales or income tax deduction
        row_calcs['state_local_sales_or_inc'] = max(
            row_calcs['state_local_sales'],
            row_calcs['state_local_income'])
        row_calcs['state_local_prop'] = div(row.A18500, row.N04470)

        calculated_taxes_paid = row_calcs['state_local_prop'] + row_calcs['state_local_sales_or_inc']
        ratio_inc_sales = div(row_calcs['state_local_sales_or_inc'], calculated_taxes_paid)
        ratio_prop = div(row_calcs['state_local_prop'], calculated_taxes_paid)
        
        row_calcs['taxes_paid_total'] = div(row.A18300, row.N04470)  # TODO: write test

        row_calcs['state_local_sales_or_inc'] = ratio_inc_sales * row_calcs['taxes_paid_total']
        row_calcs['state_local_prop'] = ratio_prop * row_calcs['taxes_paid_total']

        row_calcs['mort_int'] = div(row.A19300, row.N04470)

        row_calcs['charity_cont'] = div(row.A19700, row.N04470)
  



        # Append final results to list
        rows.append(row_calcs)

    return rows


def div(numerator, denominator):
    """Automatically handle division by 0 by setting the result equal to 0"""
    try:
        result = numerator / denominator
    except ZeroDivisionError:
        result = 0
    return result
