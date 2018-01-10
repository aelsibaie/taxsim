from context import *
import taxsim.taxsim as taxsim

policy = taxsim.current_law_policy
alt_policy = taxsim.senate_2018_policy


def get_wt(payroll_period, annual_wage, filing_status, taxpayer_allowances):
    yearly_payroll_periods = {
        'd': 260,
        'w': 52,
        'bw': 26,
        'sm': 24,
        'm': 12,
        'q': 4,
        'sa': 2,
        'a': 1
    }
    rounding_payroll_periods = {
        'd': 1,
        'w': 0,
        'bw': 0,
        'sm': 0,
        'm': 0,
        'q': 0,
        'sa': 0,
        'a': 0
    }
    personal_exemption = policy['personal_exemption']
    standard_deduction = policy['standard_deduction'][filing_status]
    if filing_status == 0:
        brackets = policy['single_brackets']
    elif filing_status == 1:
        brackets = policy['married_brackets']
    # Input validation
    else:
        raise ValueError
    if payroll_period not in yearly_payroll_periods.keys():
        raise ValueError
    payroll_wage = annual_wage / yearly_payroll_periods[payroll_period]    
    if payroll_wage < 0:
        raise ValueError

    allowances = {}
    for key, value in yearly_payroll_periods.items():
        allowances[key] = round(personal_exemption / value, 1)

    # Make our own witholding tables
    intermediary_brackets = []
    for bracket in brackets:
        intermediary_brackets.append(bracket + standard_deduction - personal_exemption)

    withholding_table_row = []
    for int_bracket in intermediary_brackets:
        withholding_table_row.append(round(int_bracket / yearly_payroll_periods[payroll_period],
                                           rounding_payroll_periods[payroll_period]))

    # The Percentage Method, found on:
    # IRS Publication 15 (2017), Page 43
    # https://www.irs.gov/pub/irs-pdf/p15.pdf#en_US_2017_publink1000254685

    # Step 1
    # Multiply one withholding allowance for your payroll period by
    # the number of allowances the employee claims.
    step1 = taxpayer_allowances * allowances[payroll_period]

    # Step 2
    # Subtract that amount from the employee's wages.
    step2 = payroll_wage - step1  # Amount subject to withholding

    # Step 3
    # Determine the amount to withhold from the appropriate table.
    rates = list(reversed(policy['income_tax_rates']))
    withheld_tax = 0
    running_taxable_income = step2
    i = 0
    for threshold in reversed(withholding_table_row):
        if step2 > threshold:
            applicable_taxable_income = running_taxable_income - threshold
            running_taxable_income = running_taxable_income - applicable_taxable_income
            withheld_tax = withheld_tax + (applicable_taxable_income * rates[i])
        i += 1

    return withheld_tax

assert get_wt('w', 24000, 0, 1) == 41.36076923076923
assert get_wt('sm', 650000, 0, 2) == 8671.9312
assert get_wt('bw', 60000, 1, 2) == 210.6238461538461
assert get_wt('m', 320000, 1, 4) == 5993.844
