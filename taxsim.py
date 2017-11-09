from pprint import pprint
from collections import OrderedDict
import csv_parser
import tax_funcs

TAXPAYERS_FILE = "taxpayers.csv"

CURRENT_LAW_FILE = "./params/current_law_2018.csv"
HOUSE_2018_FILE = "./params/house_2018.csv"

CURRENT_LAW_RESULTS = "current_law_results.csv"
HOUSE_2018_RESULTS = "house_2018_results.csv"

taxpayers = csv_parser.load_taxpayers(TAXPAYERS_FILE)
current_law_policy = csv_parser.load_policy(CURRENT_LAW_FILE)
house_2018_policy = csv_parser.load_policy(HOUSE_2018_FILE)


def calc_federal_taxes(taxpayer, policy):
    results = OrderedDict()
    # Gross income
    gross_income = (
        taxpayer['ordinary_income1']
        + taxpayer['ordinary_income2']
        + taxpayer['business_income']
        + taxpayer['ss_income']
        + taxpayer['qualified_income']
    )
    results["gross_income"] = gross_income

    # Payroll taxes
    payroll_taxes = tax_funcs.fed_payroll(policy, taxpayer)
    results["employee_payroll_tax"] = payroll_taxes['employee']
    results["employer_payroll_tax"] = payroll_taxes['employer']

    # Income after tax-deferred retirement contributions
    ordinary_income_after_401k = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2'] - taxpayer['401k_contributions']
    results["ordinary_income_after_401k"] = ordinary_income_after_401k

    # AGI
    agi = tax_funcs.fed_agi(policy, taxpayer, ordinary_income_after_401k)
    results["agi"] = agi

    # Taxable income
    taxable_income, deduction_type, deductions, personal_exemption_amt, pease_limitation_amt = tax_funcs.fed_taxable_income(policy, taxpayer, agi)
    results["taxable_income"] = taxable_income
    results["deduction_type"] = deduction_type
    results["deductions"] = deductions
    results["personal_exemption_amt"] = personal_exemption_amt
    results["pease_limitation_amt"] = pease_limitation_amt

    # Ordinary income tax
    income_tax_before_credits = tax_funcs.fed_ordinary_income_tax(policy, taxpayer, taxable_income)
    results["income_tax_before_credits"] = income_tax_before_credits

    # Qualified income/capital gains
    # TODO: Check for bugs
    qualified_income_tax = tax_funcs.fed_qualified_income(policy, taxpayer, taxable_income, income_tax_before_credits)
    income_tax_before_credits = min(income_tax_before_credits, qualified_income_tax)
    results["qualified_income_tax"] = qualified_income_tax
    results["selected_tax_before_credits"] = income_tax_before_credits # form1040_line44

    # AMT
    amt = tax_funcs.fed_amt(policy, taxpayer, deduction_type, deductions, agi, pease_limitation_amt, income_tax_before_credits)
    results["amt"] = amt

    income_tax_before_credits += amt
    results["income_tax_before_credits_with_amt"] = income_tax_before_credits

    # CTC
    ctc, actc = tax_funcs.fed_ctc(policy, taxpayer, agi)
    results["ctc"] = ctc
    results["actc"] = actc

    # EITC
    eitc = tax_funcs.fed_eitc(policy, taxpayer)
    results["eitc"] = eitc

    # Tax after nonrefundable credits
    income_tax_after_credits = round(max(0, income_tax_before_credits - ctc), 2)
    results["income_tax_after_nonrefundable_credits"] = income_tax_after_credits

    # Tax after ALL credits
    income_tax_after_credits = round(income_tax_before_credits - actc - eitc, 2) # TODO: check if the EITC is fully refundable
    results["income_tax_after_credits"] = income_tax_after_credits

    # Tax burden
    tax_burden = round(income_tax_after_credits + results["employee_payroll_tax"], 2)
    results["tax_burden"] = tax_burden

    # Tax wedge
    tax_wedge = round(
        (
            income_tax_after_credits
            + results["employee_payroll_tax"]
            + results["employer_payroll_tax"]
        ),
        2
    )
    results["tax_wedge"] = tax_wedge

    # Average effective tax rate
    avg_effective_tax_rate = round((tax_burden / gross_income), 4)
    results["avg_effective_tax_rate"] = avg_effective_tax_rate

    # Average effective tax rate without payroll
    avg_effective_tax_rate_wo_payroll = round((income_tax_after_credits / gross_income), 4)
    results["avg_effective_tax_rate_wo_payroll"] = avg_effective_tax_rate_wo_payroll

    return results

def calc_house_2018_taxes(taxpayer, policy):
    # NEW: Itemized deduction limitations
    taxpayer["sl_property_tax"] = min(10000, taxpayer["sl_property_tax"])
    taxpayer["sl_income_tax"] = 0
    taxpayer["medical_expenses"] = 0

    results = OrderedDict()
    # Gross income
    gross_income = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2'] + taxpayer['business_income'] + taxpayer['ss_income'] + taxpayer['qualified_income']
    results["gross_income"] = gross_income

    # Payroll taxes
    payroll_taxes = tax_funcs.fed_payroll(policy, taxpayer)
    results["employee_payroll_tax"] = payroll_taxes['employee']
    results["employer_payroll_tax"] = payroll_taxes['employer']

    # Income after tax-deferred retirement contributions
    ordinary_income_after_401k = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2'] - taxpayer['401k_contributions']
    results["ordinary_income_after_401k"] = ordinary_income_after_401k

    # AGI
    agi = tax_funcs.fed_agi(policy, taxpayer, ordinary_income_after_401k)
    results["agi"] = agi

    # Taxable income
    taxable_income, deduction_type, deductions, personal_exemption_amt, pease_limitation_amt = tax_funcs.fed_taxable_income(policy, taxpayer, agi)
    taxable_income, deduction_type, deductions, personal_exemption_amt, pease_limitation_amt = tax_funcs.house_2018_taxable_income(policy, taxpayer, agi)
    results["taxable_income"] = taxable_income
    results["deduction_type"] = deduction_type
    results["deductions"] = deductions
    results["personal_exemption_amt"] = personal_exemption_amt
    results["pease_limitation_amt"] = pease_limitation_amt

    # Ordinary income tax
    income_tax_before_credits = tax_funcs.fed_ordinary_income_tax(policy, taxpayer, taxable_income - taxpayer["business_income"]) + (taxpayer["business_income"] * 0.25)

    # NEW: Phaseout of benefit of the 12-percent bracket
    po_amount = 0
    lower_rate_po_threshold = [1000000, 1200000, 1000000]  # Hardcoded policy
    if agi > lower_rate_po_threshold[taxpayer["filing_status"]]:
        brackets = tax_funcs.get_brackets(taxpayer, policy)
        benefit = policy["income_tax_rates"][-1] * brackets[2] - policy["income_tax_rates"][0] * brackets[2]
        po_amount = min(benefit, 0.06 * (agi - lower_rate_po_threshold[taxpayer["filing_status"]]))  # Hardcoded policy
    income_tax_before_credits = income_tax_before_credits + po_amount
    results["income_tax_before_credits"] = income_tax_before_credits

    # Qualified income/capital gains
    # NEW: new house_2018_qualified_income function
    qualified_income_tax = tax_funcs.house_2018_qualified_income(policy, taxpayer, taxable_income, income_tax_before_credits, po_amount)
    income_tax_before_credits = min(income_tax_before_credits, qualified_income_tax)
    results["qualified_income_tax"] = qualified_income_tax
    results["selected_tax_before_credits"] = income_tax_before_credits # form1040_line44 

    # AMT
    amt = tax_funcs.fed_amt(policy, taxpayer, deduction_type, deductions, agi, pease_limitation_amt, income_tax_before_credits)
    results["amt"] = amt

    income_tax_before_credits += amt 
    results["income_tax_before_credits_with_amt"] = income_tax_before_credits 

    # CTC
    ctc, actc = tax_funcs.fed_ctc(policy, taxpayer, agi) 
    results["ctc"] = ctc
    results["actc"] = actc 

    # EITC
    eitc = tax_funcs.fed_eitc(policy, taxpayer)
    results["eitc"] = eitc

    # NEW: Personal credit
    num_taxpayers = 1
    if taxpayer["filing_status"] == 1:  # married
        num_taxpayers = 2
    personal_credit = (num_taxpayers) * 300
    results["personal_credit"] = personal_credit

    # Tax after nonrefundable credits
    income_tax_after_credits = round(max(0, income_tax_before_credits - ctc - personal_credit), 2)
    results["income_tax_after_nonrefundable_credits"] = income_tax_after_credits

    # Tax after ALL credits
    income_tax_after_credits = round(income_tax_before_credits - actc - eitc, 2) # TODO: check if the EITC is fully refundable
    results["income_tax_after_credits"] = income_tax_after_credits

    # Tax burden
    tax_burden = round(income_tax_after_credits + results["employee_payroll_tax"], 2)

    results["tax_burden"] = tax_burden

    # Tax wedge
    tax_wedge = round(
        (
            income_tax_after_credits
            + results["employee_payroll_tax"]
            + results["employer_payroll_tax"]
        ),
        2
    )
    results["tax_wedge"] = tax_wedge

    # Average effective tax rate
    avg_effective_tax_rate = round((tax_burden / gross_income), 4)
    results["avg_effective_tax_rate"] = avg_effective_tax_rate

    # Average effective tax rate without payroll
    avg_effective_tax_rate_wo_payroll = round((income_tax_after_credits / gross_income), 4)
    results["avg_effective_tax_rate_wo_payroll"] = avg_effective_tax_rate_wo_payroll

    return results

if __name__ == '__main__':
    current_law_results = []
    house_2018_results = []
    for i in range(len(taxpayers)):
        filer = taxpayers[i]
        print("\n" + "Current law - filer #" + str(i + 1))
        current_law_result = calc_federal_taxes(filer, current_law_policy)
        current_law_results.append(current_law_result)
        pprint(current_law_result)
        print("\n" + "House 2018 - filer #" + str(i + 1))
        house_2018_result = calc_house_2018_taxes(filer, house_2018_policy)
        house_2018_results.append(house_2018_result)
        pprint(house_2018_result)

    csv_parser.write_results(current_law_results, CURRENT_LAW_RESULTS)
    csv_parser.write_results(house_2018_results, HOUSE_2018_RESULTS)
