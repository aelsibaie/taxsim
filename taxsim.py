import csv_parser
import tax_funcs
from collections import OrderedDict

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
    gross_income = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2'] + taxpayer['business_income'] + taxpayer['ss_income'] + taxpayer['qualified_income']
    print("gross_income", gross_income)
    results["gross_income"] = gross_income

    # Payroll taxes
    employee_payroll_tax, employer_payroll_tax = tax_funcs.fed_payroll(policy, taxpayer)
    print("employee_payroll_tax", employee_payroll_tax)
    print("employer_payroll_tax", employer_payroll_tax)
    results["employee_payroll_tax"] = employee_payroll_tax
    results["employer_payroll_tax"] = employer_payroll_tax

    # Income after tax-deferred retirement contributions
    ordinary_income_after_401k = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2'] - taxpayer['401k_contributions']
    print("ordinary_income_after_401k", ordinary_income_after_401k)
    results["ordinary_income_after_401k"] = ordinary_income_after_401k

    # AGI
    agi = tax_funcs.fed_agi(policy, taxpayer, ordinary_income_after_401k)
    print("agi", agi)
    results["agi"] = agi

    # Taxable income
    taxable_income, deduction_type, deductions, personal_exemption_amt, pease_limitation_amt = tax_funcs.fed_taxable_income(policy, taxpayer, agi)
    print("taxable_income", taxable_income)
    print("deduction_type", deduction_type)
    print("deductions", deductions)
    print("personal_exemption_amt", personal_exemption_amt)
    print("pease_limitation_amt", pease_limitation_amt)
    results["taxable_income"] = taxable_income
    results["deduction_type"] = deduction_type
    results["deductions"] = deductions
    results["personal_exemption_amt"] = personal_exemption_amt
    results["pease_limitation_amt"] = pease_limitation_amt

    # Ordinary income tax
    income_tax_before_credits = tax_funcs.fed_ordinary_income_tax(policy, taxpayer, taxable_income)
    print("income_tax_before_credits", income_tax_before_credits)
    results["income_tax_before_credits"] = income_tax_before_credits

    # Qualified income/capital gains
    # TODO: Check for bugs
    qualified_income_tax = tax_funcs.fed_qualified_income(policy, taxpayer, taxable_income, income_tax_before_credits)
    print("qualified_income_tax", qualified_income_tax)
    income_tax_before_credits = min(income_tax_before_credits, qualified_income_tax)
    print("income_tax_before_credits", income_tax_before_credits)
    results["qualified_income_tax"] = qualified_income_tax
    results["income_tax_before_credits"] = income_tax_before_credits

    # AMT
    amt = tax_funcs.fed_amt(policy, taxpayer, deduction_type, deductions, agi, pease_limitation_amt)
    print("amt", amt)
    results["amt"] = amt

    # CTC
    ctc = tax_funcs.fed_ctc(policy, taxpayer, agi)
    print("ctc", ctc)
    results["ctc"] = ctc

    # EITC
    eitc = tax_funcs.fed_eitc(policy, taxpayer)
    print("eitc", eitc)
    results["eitc"] = eitc

    # Tax after credits
    income_tax_after_credits = income_tax_before_credits - ctc - eitc
    print("income_tax_after_credits", income_tax_after_credits)
    results["income_tax_after_credits"] = income_tax_after_credits

    # AMT check
    # TODO: Check this workaround so the AMT wont block refundable credits
    if income_tax_after_credits >= 0:
        federal_income_tax = max(amt, income_tax_after_credits)
    else:
        federal_income_tax = income_tax_after_credits

    # Federal income tax
    federal_income_tax = round(federal_income_tax, 2)
    print("federal_income_tax", federal_income_tax)
    results["federal_income_tax"] = federal_income_tax

    # Tax burden
    tax_burden = round(federal_income_tax + employee_payroll_tax, 2)
    print("tax_burden", tax_burden)
    results["tax_burden"] = tax_burden

    # Average effective tax rate
    avg_effective_tax_rate = round((tax_burden / gross_income) * 100, 2)
    print("avg_effective_tax_rate", avg_effective_tax_rate)
    results["avg_effective_tax_rate"] = avg_effective_tax_rate

    # Tax wedge
    tax_wedge = round(federal_income_tax + employee_payroll_tax + employer_payroll_tax, 2)
    print("tax_wedge", tax_wedge)
    results["tax_wedge"] = tax_wedge

    return results


def calc_house_2018_taxes(taxpayer, policy):
    # NEW: Itemized deduction limitations
    taxpayer["sl_property_tax"] = max(10000, taxpayer["sl_property_tax"])
    taxpayer["sl_income_tax"] = 0

    results = OrderedDict()
    # Gross income
    gross_income = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2'] + taxpayer['business_income'] + taxpayer['ss_income'] + taxpayer['qualified_income']
    print("gross_income", gross_income)
    results["gross_income"] = gross_income

    # Payroll taxes
    employee_payroll_tax, employer_payroll_tax = tax_funcs.fed_payroll(policy, taxpayer)
    print("employee_payroll_tax", employee_payroll_tax)
    print("employer_payroll_tax", employer_payroll_tax)
    results["employee_payroll_tax"] = employee_payroll_tax
    results["employer_payroll_tax"] = employer_payroll_tax

    # Income after tax-deferred retirement contributions
    ordinary_income_after_401k = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2'] - taxpayer['401k_contributions']
    print("ordinary_income_after_401k", ordinary_income_after_401k)
    results["ordinary_income_after_401k"] = ordinary_income_after_401k

    # AGI
    agi = tax_funcs.fed_agi(policy, taxpayer, ordinary_income_after_401k)
    print("agi", agi)
    results["agi"] = agi

    # Taxable income
    taxable_income, deduction_type, deductions, personal_exemption_amt, pease_limitation_amt = tax_funcs.fed_taxable_income(policy, taxpayer, agi)
    print("taxable_income", taxable_income)
    print("deduction_type", deduction_type)
    print("deductions", deductions)
    print("personal_exemption_amt", personal_exemption_amt)
    print("pease_limitation_amt", pease_limitation_amt)
    results["taxable_income"] = taxable_income
    results["deduction_type"] = deduction_type
    results["deductions"] = deductions
    results["personal_exemption_amt"] = personal_exemption_amt
    results["pease_limitation_amt"] = pease_limitation_amt

    # Ordinary income tax
    income_tax_before_credits = tax_funcs.fed_ordinary_income_tax(policy, taxpayer, taxable_income - taxpayer["business_income"]) + (taxpayer["business_income"] * 0.25)
    print("debug: income_tax_before_credits and 12% po", income_tax_before_credits)

    # NEW: Phaseout of benefit of the 12-percent bracket
    po_amount = 0
    lower_rate_po_threshold = [1000000, 1200000, 1000000]  # Hardcoded policy
    if agi > lower_rate_po_threshold[taxpayer["filing_status"]]:
        brackets = tax_funcs.get_brackets(taxpayer, policy)
        benefit = policy["income_tax_rates"][-1] * brackets[2] - policy["income_tax_rates"][0] * brackets[2]
        po_amount = min(benefit, 0.06 * (agi - lower_rate_po_threshold[taxpayer["filing_status"]]))  # Hardcoded policy
    income_tax_before_credits = income_tax_before_credits + po_amount
    print("income_tax_before_credits", income_tax_before_credits)
    results["income_tax_before_credits"] = income_tax_before_credits

    # Qualified income/capital gains
    # TODO: Check for bugs
    # NEW: new house_2018_qualified_income function
    qualified_income_tax = tax_funcs.house_2018_qualified_income(policy, taxpayer, taxable_income, income_tax_before_credits, po_amount)
    print("qualified_income_tax", qualified_income_tax)
    income_tax_before_credits = min(income_tax_before_credits, qualified_income_tax)
    print("income_tax_before_credits", income_tax_before_credits)
    results["qualified_income_tax"] = qualified_income_tax
    results["income_tax_before_credits"] = income_tax_before_credits

    # AMT
    amt = tax_funcs.fed_amt(policy, taxpayer, deduction_type, deductions, agi, pease_limitation_amt)
    print("amt", amt)
    results["amt"] = amt

    # CTC
    ctc = tax_funcs.fed_ctc(policy, taxpayer, agi)
    print("ctc", ctc)
    results["ctc"] = ctc

    # EITC
    eitc = tax_funcs.fed_eitc(policy, taxpayer)
    print("eitc", eitc)
    results["eitc"] = eitc

    # NEW: Personal credit
    num_taxpayers = 1
    if taxpayer["filing_status"] == 1:  # married
        num_taxpayers = 2
    personal_credit = (num_taxpayers) * 300

    # NEW: Nonrefundable credits
    income_tax_before_credits = max(0, income_tax_before_credits - personal_credit)

    # Tax after credits
    income_tax_after_credits = income_tax_before_credits - ctc - eitc  # TODO: check refundable portion of CTC
    print("income_tax_after_credits", income_tax_after_credits)
    results["income_tax_after_credits"] = income_tax_after_credits

    # AMT check
    # TODO: Check this workaround so the AMT wont block refundable credits
    if income_tax_after_credits >= 0:
        federal_income_tax = max(amt, income_tax_after_credits)
    else:
        federal_income_tax = income_tax_after_credits

    # Federal income tax
    federal_income_tax = round(federal_income_tax, 2)
    print("federal_income_tax", federal_income_tax)
    results["federal_income_tax"] = federal_income_tax

    # Tax burden
    tax_burden = round(federal_income_tax + employee_payroll_tax, 2)
    print("tax_burden", tax_burden)
    results["tax_burden"] = tax_burden

    # Average effective tax rate
    avg_effective_tax_rate = round((tax_burden / gross_income) * 100, 2)
    print("avg_effective_tax_rate", avg_effective_tax_rate)
    results["avg_effective_tax_rate"] = avg_effective_tax_rate

    # Tax wedge
    tax_wedge = round(federal_income_tax + employee_payroll_tax + employer_payroll_tax, 2)
    print("tax_wedge", tax_wedge)
    results["tax_wedge"] = tax_wedge

    return results


current_law_results = []
house_2018_results = []
for filer in taxpayers:
    print("\n" + "Starting current law calculator")
    current_law_results.append(calc_federal_taxes(filer, current_law_policy))
    print("\n" + "Starting house 2018 calculator")
    house_2018_results.append(calc_house_2018_taxes(filer, house_2018_policy))

csv_parser.write_results(current_law_results, CURRENT_LAW_RESULTS)
csv_parser.write_results(house_2018_results, HOUSE_2018_RESULTS)
