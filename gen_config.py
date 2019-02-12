from taxsim.context import *
import taxsim.taxsim as taxsim
import taxsim.misc_funcs as misc_funcs
import taxsim.csv_parser as csv_parser
from collections import OrderedDict
from datetime import datetime
import copy
import json


meta = []
meta.append({
    "name": "James",
    "filingData": "Single, No Kids",
    "id": "james",
    "tooltip": "This taxpayer takes the standard deduction and had $2,600 of pre-tax 401(k) contributions."
})
meta.append({
    "name": "Jason",
    "filingData": "Single, 2 Kids",
    "id": "jason",
    "tooltip": "This taxpayer takes the standard deduction and had $4,000 of pre-tax 401(k) contributions."
})
meta.append({
    "name": "Amber",
    "filingData": "Single, No Kids",
    "id": "amber",
    "tooltip": "This taxpayer takes the standard deduction and had $5,500 of pre-tax 401(k) contributions."
})
meta.append({
    "name": "Kavya & Nick",
    "filingData": "Married, 2 Kids",
    "id": "kavya",
    "tooltip": "These taxpayers take the standard deduction and had $5,500 of pre-tax 401(k) contributions."
})
meta.append({
    "name": "Sophie & Chad",
    "filingData": "Married, 2 Kids",
    "id": "sophie",
    "tooltip": "These taxpayers claimed about $26,000 worth of itemized deductions and had $20,000 of pre-tax 401(k) contributions."
})
meta.append({
    "name": "Soren & Linea",
    "filingData": "Married, 3 Kids",
    "id": "soren",
    "tooltip": "These taxpayers earned half their income via a pass-through business which qualifies for the new 20-percent deduction and claimed about $30,000 worth of other itemized deductions. They also had $19,000 of pre-tax 401(k) contributions."
})
meta.append({
    "name": "Laura & Seth",
    "filingData": "Married, 2 Kids",
    "id": "laura",
    "tooltip": "These taxpayers claimed about $220,000 worth of itemized deductions and had $18,500 of pre-tax 401(k) contributions."
})
meta.append({
    "name": "Joe & Ethan",
    "filingData": "Married, Retired",
    "id": "joe",
    "tooltip": "This taxpayer takes the standard deduction and had $2,600 of pre-tax 401(k) contributions."
})


tax_calc = taxsim.calc_federal_taxes
policy = taxsim.current_law_policy
policy_2019 = taxsim.current_law_2019_policy

alt_tax_calc = taxsim.calc_senate_2018_taxes
alt_policy = taxsim.senate_2018_policy
alt_policy_2019 = taxsim.senate_2019_policy


taxpayers = csv_parser.load_taxpayers(taxsim.TAXPAYERS_FILE)


profiles = {"profiles": []}


for i in range(len(taxpayers)):

    # Copy taxpayers
    taxpayer1 = copy.deepcopy(taxpayers[i])
    taxpayer2 = copy.deepcopy(taxpayers[i])
    taxpayer3 = copy.deepcopy(taxpayers[i])
    taxpayer4 = copy.deepcopy(taxpayers[i])

    # 2018
    result = tax_calc(taxpayer1, policy)
    alt_result = alt_tax_calc(taxpayer2, alt_policy)

    # 2019
    result_2019 = tax_calc(taxpayer3, policy_2019)
    alt_result_2019 = alt_tax_calc(taxpayer4, alt_policy_2019)

    desc = {"name": meta[i]["name"],
            "filingData": meta[i]["filingData"],
            "id": meta[i]["id"],
            "income": result["gross_income"],
            "tooltip": meta[i]["tooltip"]}

    results = []
    results.append({'plan': {
        'id': 'pre-tcja',
        'name': 'Previous Law',
        'year': 2018},
        'results': result})
    results.append({'plan': {
        'id': 'tcja',
        'name': 'Tax Cuts and Jobs Act',
        'year': 2018},
        'results': alt_result})
    results.append({'plan': {
        'id': 'pre-tcja',
        'name': 'Previous Law',
        'year': 2019},
        'results': result_2019})
    results.append({'plan': {
        'id': 'tcja',
        'name': 'Tax Cuts and Jobs Act',
        'year': 2019},
        'results': alt_result_2019})

    temp_dict = {"description": desc,
                 "taxes": results}

    profiles["profiles"].append(temp_dict)


with open('config.json', 'w') as f:
    json.dump(profiles, f, indent=2)
