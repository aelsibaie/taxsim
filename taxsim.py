import csv_parser
import tax_funcs

CURRENT_LAW_FILE = "./params/current_law_2018.csv"
TAXPAYERS_FILE = "taxpayers.csv"

policy = csv_parser.load_policy(CURRENT_LAW_FILE)
taxpayers = csv_parser.load_taxpayers(TAXPAYERS_FILE)


def calc_federal_taxes(taxpayer):
    # Gross income
    gross_income = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2'] + taxpayer['business_income'] + taxpayer['ss_income'] + taxpayer['qualified_income']
    print("gross_income", gross_income)

    # Payroll taxes
    employee_payroll_tax, employer_payroll_tax = tax_funcs.fed_payroll(policy, taxpayer)
    print("employee_payroll_tax", employee_payroll_tax)
    print("employer_payroll_tax", employer_payroll_tax)

    # Income after tax-deferred retirement contributions
    ordinary_income_after_401k = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2'] - taxpayer['401k_contributions']
    print("ordinary_income_after_401k", ordinary_income_after_401k)

    # AGI
    agi = tax_funcs.fed_agi(policy, taxpayer, ordinary_income_after_401k)
    print("agi", agi)

    # Taxable income
    taxable_income, deduction_type, deductions, personal_exemption_amt, pease_limitation_amt = tax_funcs.fed_taxable_income(policy, taxpayer, agi)
    print("taxable_income", taxable_income)
    print("deduction_type", deduction_type)
    print("deductions", deductions)
    print("personal_exemption_amt", personal_exemption_amt)
    print("pease_limitation_amt", pease_limitation_amt)

    # Ordinary income tax
    income_tax_before_credits = tax_funcs.fed_ordinary_income_tax(policy, taxpayer, taxable_income)
    print("income_tax_before_credits", income_tax_before_credits)

    # TODO: Add qualified income/capital gains taxes
    
    # AMT
    amt = tax_funcs.fed_amt(policy, taxpayer, deduction_type, deductions, agi, pease_limitation_amt)
    print("amt", amt)

    # CTC
    ctc = tax_funcs.fed_ctc(policy, taxpayer, agi)
    print("ctc", ctc)

    # EITC
    eitc = tax_funcs.fed_eitc(policy, taxpayer)
    print("eitc", eitc)

    # Tax after credits
    income_tax_after_credits = income_tax_before_credits - ctc - eitc
    print("income_tax_after_credits", income_tax_after_credits)

    # AMT check
    # TODO: Check this workaround so the AMT wont block refundable credits
    if income_tax_after_credits >= 0:
        federal_income_tax = max(amt, income_tax_after_credits)
    else:
        federal_income_tax = income_tax_after_credits
    print("federal_income_tax", federal_income_tax)

    # Tax burden
    tax_burden = federal_income_tax + employee_payroll_tax
    print("tax_burden", tax_burden)

    # Tax wedge
    tax_wedge = federal_income_tax + employee_payroll_tax + employer_payroll_tax
    print("tax_wedge", tax_wedge)

    print("")


for taxpayer in taxpayers:
    calc_federal_taxes(taxpayer)
