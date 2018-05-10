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
    df['0-30'] = df["1"] + df["2"] + df["3"]
    del df["1"], df["2"], df["3"]
    df['30-75'] = df["4"] + df["5"]
    del df["4"], df["5"]
    df['75-150'] = df["6"] + df["7"]
    del df["6"], df["7"]
    df['150-500'] = df["8"] + df["9"]
    del df["8"], df["9"]
    df['500-inf'] = df["10"] + df["11"]
    del df["10"], df["11"]
    df['state'] = ws.title
    df['state_fips'] = state_codes[ws.title]


    dataframes.append(df)

dataframe = pd.concat(dataframes, ignore_index=True)

dataframe.to_csv("test.csv")