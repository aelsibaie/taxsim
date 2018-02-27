"""
This module processes county level data released by the IRS
Latest data files are located here: https://www.irs.gov/statistics/soi-tax-stats-county-data

TODO: This module is INCOMPLETE

"""

import os
import pandas
import logging
from tqdm import tqdm
from collections import OrderedDict
import math

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

    #logging.info("Loading: " + COUNTY_DATA_NOAGI)
    #data_noagi = pandas.read_csv(COUNTY_DATA_NOAGI)
    # TODO: Merge the two datasets before running the calculator

    # drop negative or 0 AGIs
    data_agi = data_agi[data_agi.AGI_STUB != 1]
    data_agi = data_agi[data_agi.N00200 != 0]

    # we only want NY
    data_agi = data_agi[data_agi.STATE == "NY"]

    scale = 1000

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
        
        row_calcs['filing_status'] = 0
        if row_calcs['percent_joint'] > row_calcs['percent_single']:
            row_calcs['filing_status'] = 1
        elif (row_calcs['percent_hoh'] > row_calcs['percent_single']) and (row_calcs['percent_hoh'] > row_calcs['percent_joint']):
            row_calcs['filing_status'] = 2


        #row_calcs['percent_other'] = max(0, 1 - row_calcs['percent_single'] - row_calcs['percent_joint'] - row_calcs['percent_hoh'])
        #row_calcs['percent_elderly'] = div(row.ELDERLY, row.N1)
        
        row_calcs['percent_itemizing'] = div(row.N04470, row.N1)
        if row_calcs['percent_itemizing'] > 0.5:
            row_calcs['itemizing_flag'] = 1
        else:
            row_calcs['itemizing_flag'] = 0

        # CHILDREN
        #row_calcs['number_children'] = div(row.NUMDEP, (row.MARS2 + row.MARS4))  # only divide by filing status' capable of having children
        #row_calcs['rounded_children'] = round(row_calcs['number_children'], 0)

        # household size and new method for children
        row_calcs['household_size'] = round(div(row.N2, row.N1), 0)
        if row_calcs['filing_status'] == 1:
            children = row_calcs['household_size'] - 2
        else:
            children = row_calcs['household_size'] - 1
        row_calcs['children'] = max(0, children)

        # INCOMES
        #row_calcs['taxable_ss_inc'] = div(row.A02500, row.N02500) * scale  # only includes the taxable portion of SS income

        row_calcs['agi'] = div(row.A00100, row.N00200) * scale

        ordinary_income = row.A00200 + row.A00300 + row.A00600

        #row_calcs['wage_inc'] = div(row.A00200, row.N00200) * scale
        #row_calcs['taxable_int_inc'] = div(row.A00300, row.N00300) * scale
        #row_calcs['ordinary_div_inc'] = div(row.A00600, row.N00600) * scale

        qualified_income = row.A00650 + row.A01000

        share_ordinary = div(ordinary_income, (ordinary_income + qualified_income))
        share_qualified = div(qualified_income, (ordinary_income + qualified_income))

        row_calcs['ordinary_income'] = share_ordinary * row_calcs['agi']
        row_calcs['qualified_income'] = share_qualified * row_calcs['agi']


        #row_calcs['qual_div_inc'] = div(row.A00650, row.N00650) * scale
        #row_calcs['cap_gains_inc'] = div(row.A01000, row.N01000) * scale # assuming long term

        #row_calcs['partnership_scorp_inc'] = div(row.A26270, row.N26270) * scale
        #row_calcs['business_professional_inc'] = div(row.A00900, row.N00900) * scale

        # DEDUCTIONS
        row_calcs['total_itemized'] = div(row.A04470, row.N04470) * scale

        income_or_sales = max(row.A18425, row.A18450)
        imputed_itemized_deductions = income_or_sales + row.A18500 + row.A19300 + row.A19700
        percent_income_or_sales_deduction = div(income_or_sales, imputed_itemized_deductions)
        percent_property_deduction = div(row.A18500, imputed_itemized_deductions)
        percent_mort_int_deduction = div(row.A19300, imputed_itemized_deductions)
        percent_charity_deduction = div(row.A19700, imputed_itemized_deductions)

        row_calcs['imputed_income_or_sales_deduction'] = percent_income_or_sales_deduction * row_calcs['total_itemized']
        row_calcs['imputed_property_deduction'] = percent_property_deduction * row_calcs['total_itemized']
        row_calcs['imputed_mort_int_deduction'] = percent_mort_int_deduction * row_calcs['total_itemized']
        row_calcs['imputed_charity_deduction'] = percent_charity_deduction * row_calcs['total_itemized']



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
