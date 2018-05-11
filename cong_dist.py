import os
import taxsim.taxsim as taxsim
import taxsim.misc_funcs as misc_funcs
import pandas as pd
import copy
import openpyxl
from collections import OrderedDict


file_path = os.path.join('data', 'ty15_congressional_stats', 'Congressional Data Book Tax Year 2015 Final.xlsx')

wb = openpyxl.load_workbook(file_path)

# delete non-states
non_states = [
    "National",
    "Limitations",
    "Guam",
    "APO FPO",
    "American Samoa",
    "Puerto Rico",
    "Virgin Islands"
]
for sheet_name in non_states:
    del wb[sheet_name]

# convert state names to 2 char abbrev
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}
for ws in wb.worksheets:
    if ws.title in us_state_abbrev.keys():
        ws.title = us_state_abbrev[ws.title]

state_codes = {
    'WA': '53', 'DE': '10', 'DC': '11', 'WI': '55', 'WV': '54', 'HI': '15',
    'FL': '12', 'WY': '56', 'PR': '72', 'NJ': '34', 'NM': '35', 'TX': '48',
    'LA': '22', 'NC': '37', 'ND': '38', 'NE': '31', 'TN': '47', 'NY': '36',
    'PA': '42', 'AK': '02', 'NV': '32', 'NH': '33', 'VA': '51', 'CO': '08',
    'CA': '06', 'AL': '01', 'AR': '05', 'VT': '50', 'IL': '17', 'GA': '13',
    'IN': '18', 'IA': '19', 'MA': '25', 'AZ': '04', 'ID': '16', 'CT': '09',
    'ME': '23', 'MD': '24', 'OK': '40', 'OH': '39', 'UT': '49', 'MO': '29',
    'MN': '27', 'MI': '26', 'RI': '44', 'KS': '20', 'MT': '30', 'MS': '28',
    'SC': '45', 'KY': '21', 'OR': '41', 'SD': '46'
}

dataframes = []
for ws in wb.worksheets:
    data = ws.values
    cols = next(data)[0:]
    df = pd.DataFrame(data, columns=cols)
    df.replace(to_replace="*", value=0, inplace=True)
    df.drop(columns=['Zero and\nLoss'], inplace=True)
    df.rename(columns={"Cong.\nDist.": "district",
                       "$.01 Under\n$10,000": "1",
                       "$10,000 Under\n$20,000": "2",
                       "$20,000 Under\n$30,000": "3",
                       "$30,000 Under\n$50,000": "4",
                       "$50,000 Under\n$75,000": "5",
                       "$75,000 Under\n$100,000": "6",
                       "$100,000 Under\n$150,000": "7",
                       "$150,000 Under\n$200,000": "8",
                       "$200,000 Under\n$500,000": "9",
                       "$500,000 Under\n$1,000,000": "10",
                       "$1,000,000 and\nOver": "11",
                       "Return Item": "return_item",
                       "Total Returns": "total_returns"
                       }, inplace=True)
    # consolidate income brackets
    df['0-30'] = df["1"] + df["2"] + df["3"]
    df['30-75'] = df["4"] + df["5"]
    df['75-150'] = df["6"] + df["7"]
    df['150-500'] = df["8"] + df["9"]
    df['500-inf'] = df["10"] + df["11"]
    # delete old income brackets
    del df["1"], df["2"], df["3"], df["4"], df["5"], df["6"], df["7"], df["8"], df["9"], df["10"], df["11"]
    df['state'] = ws.title
    df['state_fips'] = state_codes[ws.title]

    if df.loc[df['district'] != "Total"].empty == True:
        df.replace(to_replace="Total", value=0, inplace=True)
    else:
        df = df.loc[df['district'] != "Total"]

    dataframes.append(df)

dataframe = pd.concat(dataframes, ignore_index=True)

dataframe.to_csv("cleaned_data.csv")

filing_statuses = [0, 1] # logic later can make this 2 for HoH
number_kids = [0, 1, 2]
incomes = ['0-30', '30-75', '75-150', '150-500', '500-inf']

results = []

# this is where the magic happens
for state in dataframe.state.unique():
    sub_df = dataframe.loc[dataframe['state'] == state]
    for district in sub_df.district.unique():
        dist_df = sub_df.loc[sub_df['district'] == district]
        # dist_df is each districts data
        for income in incomes:
            # store results in ordered dict
            state = str(dist_df['state'].unique()[0])
            state_fips = int(dist_df['state_fips'].unique())
            district = int(dist_df['district'].unique())
            # number of returns
            ret_count = float(dist_df[dist_df['return_item']=='Return Count'][income])
            try:
                # ordinary income
                wages = float(dist_df[dist_df['return_item']=='Wages Amt.'][income]) / ret_count
                taxable_int = float(dist_df[dist_df['return_item']=='Taxable Interest Amt.'][income]) / ret_count
                # qualified income
                dividends = float(dist_df[dist_df['return_item']=='Taxable Dividend Amt.'][income]) / ret_count
                cap_gains = float(dist_df[dist_df['return_item']=='Capital Gain/Loss Amt.'][income]) / ret_count
                # deductions
                med_exp_ded = float(dist_df[dist_df['return_item']=='Med./Dent. Exp. Amt.'][income]) / ret_count
                sl_ded = float(dist_df[dist_df['return_item']=='State and Loc. Tax Amt.'][income]) / ret_count
                prop_ded = float(dist_df[dist_df['return_item']=='Real Estate Tax Amt.'][income]) / ret_count
                int_ded = float(dist_df[dist_df['return_item']=='Interest Paid Amt.'][income]) / ret_count
                cont_ded = float(dist_df[dist_df['return_item']=='Contribution Amt.'][income]) / ret_count
            except ZeroDivisionError:
                 # set everything to 0 if there are no returns
                wages = 0
                taxable_int = 0
                dividends = 0
                cap_gains = 0
                med_exp_ded = 0
                sl_ded = 0
                prop_ded = 0
                int_ded = 0
                cont_ded = 0

            # create taxpayers
            for CHILDREN in number_kids:
                for FILING_STATUS in filing_statuses:

                    #change for HoH
                    if CHILDREN != 0 and FILING_STATUS == 0:
                        real_FILING_STATUS = 2
                    else:
                        real_FILING_STATUS = FILING_STATUS

                    result = OrderedDict()
                    #result["state"] = state
                    result["state_fips"] = int(state_fips)
                    result["district"] = int(district)
                    result["income"] = income

                    taxpayer = misc_funcs.create_taxpayer()
                    taxpayer["filing_status"] = real_FILING_STATUS
                    taxpayer["child_dep"] = CHILDREN
                    taxpayer["ordinary_income1"] = wages + taxable_int
                    taxpayer["qualified_income"] = dividends + cap_gains
                    taxpayer["medical_expenses"] = med_exp_ded
                    taxpayer["sl_income_tax"] = sl_ded
                    taxpayer["sl_property_tax"] = prop_ded
                    taxpayer["interest_paid"] = int_ded
                    taxpayer["charity_contributions"] = cont_ded



                    result["filing_status"] = int(FILING_STATUS)
                    result["child_dep"] = int(CHILDREN)
                    result["ordinary_income1"] = int(round(wages + taxable_int))
                    result["qualified_income"] = int(round(dividends + cap_gains))
                    result["medical_expenses"] = int(round(med_exp_ded))
                    result["sl_income_tax"] = int(round(sl_ded))
                    result["sl_property_tax"] = int(round(prop_ded))
                    result["interest_paid"] = int(round(int_ded))
                    result["charity_contributions"] = int(round(cont_ded))


                    taxpayer1 = copy.deepcopy(taxpayer)
                    taxpayer2 = copy.deepcopy(taxpayer)

                    results1 = taxsim.calc_federal_taxes(taxpayer1, taxsim.current_law_policy, False)
                    results2 = taxsim.calc_senate_2018_taxes(taxpayer2, taxsim.senate_2018_policy, False)

                    result["pre-tcja-deduction_type"] = results1["deduction_type"]
                    result["current-law-deduction_type"] = results2["deduction_type"]

                    result["pre-tcja-tax"] = int(round(results1["income_tax_after_credits"]))
                    result["current-law-tax"] = int(round(results2["income_tax_after_credits"]))

                    results.append(result)

final_results = pd.DataFrame(results)
final_results.to_csv("final_data.csv", index=False)