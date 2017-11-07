import math


def fed_payroll(policy, taxpayer):
    combined_ordinary_income = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2']

    # Withholding Taxes
    employee_payroll_tax = 0
    employer_payroll_tax = 0
    for income in [taxpayer['ordinary_income1'], taxpayer['ordinary_income2']]:
        employee_ss = policy['ss_withholding_rate_employee'] * min(income, policy['ss_wage_base'])
        employer_ss = policy['ss_withholding_rate_employer'] * min(income, policy['ss_wage_base'])
        employee_med = policy['medicare_withholding_rate_employee'] * min(income, policy['medicare_wage_base'])
        employer_med = policy['medicare_withholding_rate_employer'] * min(income, policy['medicare_wage_base'])
        employee_payroll_tax = employee_payroll_tax + employee_ss + employee_med
        employer_payroll_tax = employer_payroll_tax + employer_ss + employer_med

    # Additional Medicare Tax
    medicare_surtax = 0
    if combined_ordinary_income > policy['additional_medicare_tax_threshold'][taxpayer['filing_status']]:
        taxable_medicare_surtax = combined_ordinary_income - policy['additional_medicare_tax_threshold'][taxpayer['filing_status']]
        medicare_surtax = taxable_medicare_surtax * policy['additional_medicare_tax_rate']
    employee_payroll_tax = employee_payroll_tax + medicare_surtax

    return employee_payroll_tax, employer_payroll_tax


def fed_agi(policy, taxpayer, ordinary_income_after_401k):

    agi = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2'] + taxpayer['business_income'] + taxpayer['qualified_income']

    # Social security income may not be fully taxable
    if taxpayer['ss_income'] > 0:
        ss_income = 0
        combined_income = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2'] + taxpayer['business_income'] + (taxpayer['ss_income'] * 0.5) + taxpayer['qualified_income']
        # Publication 915 https://www.irs.gov/pub/irs-pdf/p915.pdf
        line10 = combined_income - policy["taxable_ss_base_threshold"][taxpayer['filing_status']]
        if line10 > 0:
            line11 = policy["taxable_ss_top_threshold"][taxpayer['filing_status']] - policy["taxable_ss_base_threshold"][taxpayer['filing_status']]
            line12 = max(0, line10 - line11)
            line13 = min(line10, line11)
            line14 = line13 * policy["taxable_ss_base_amt"]
            line15 = min(line14, taxpayer['ss_income'] / 2)
            line16 = line12 * policy["taxable_ss_top_amt"]
            line17 = line15 + line16
            line18 = taxpayer['ss_income'] * policy["taxable_ss_top_amt"]
            ss_income = min(line17, line18)  # aka line19
        agi = agi + ss_income

    return agi


def fed_taxable_income(policy, taxpayer, agi):
    taxable_income = agi

    # Personal exemption(s)
    # Publication 501 https://www.irs.gov/pub/irs-pdf/p501.pdf
    personal_exemption_amt = 0
    filers = 1
    if taxpayer["filing_status"] == 1:
        filers = 2
    exemptions_claimed = filers + taxpayer["child_dep"] + taxpayer["nonchild_dep"]
    # Check for phase out of personal exemption
    if agi > policy["personal_exemption_po_threshold"][taxpayer['filing_status']]:
        personal_exemption_amt = policy["personal_exemption"] * exemptions_claimed
        amt_over_threshold = agi - policy["personal_exemption_po_threshold"][taxpayer['filing_status']]
        line6 = math.ceil(amt_over_threshold / policy["personal_exemption_po_amt"])
        line7 = round(line6 * policy["personal_exemption_po_rate"], 3)
        line8 = personal_exemption_amt * line7
        personal_exemption_amt = max(0, personal_exemption_amt - line8)  # aka line9
    else:
        personal_exemption_amt = policy["personal_exemption"] * exemptions_claimed

    # Standard deduction
    standard_deduction = policy["standard_deduction"][taxpayer['filing_status']]
    # TODO: ADD ADDITIONAL STANDARD DEDUCTION FOR ELDERLY

    # Itemized deductions
    itemized_total = taxpayer["medical_expenses"] + \
        taxpayer["sl_income_tax"] + \
        taxpayer["sl_property_tax"] + \
        taxpayer["interest_paid"] + \
        taxpayer["charity_contributions"] + \
        taxpayer["other_itemized"]
    # Check for phase out of itemized deductions
    # Itemized Deductions Worksheet—Line 29 https://www.irs.gov/pub/irs-pdf/i1040sca.pdf
    pease_limitation_amt = 0
    line1 = itemized_total
    line2 = taxpayer["medical_expenses"]  # could also include investment interest and casualty deductions
    if line2 < line1:
        line3 = line1 - line2
        line4 = line3 * policy["itemized_limitation_amt"]
        line5 = agi
        line6 = policy["itemized_limitation_threshold"][taxpayer['filing_status']]
        if line6 < line5:
            line7 = line5 - line6
            line8 = line7 * policy["itemized_limitation_rate"]
            line9 = min(line4, line8)
            pease_limitation_amt = line9  # used in AMT calc
            itemized_total = line1 - line9  # aka line10

    deductions = max(itemized_total, standard_deduction)
    if deductions != standard_deduction:
        deduction_type = "itemized"
    else:
        deduction_type = "standard"
    taxable_income = max(0, taxable_income - personal_exemption_amt - deductions)

    return taxable_income, deduction_type, deductions, personal_exemption_amt, pease_limitation_amt


def fed_ordinary_income_tax(policy, taxpayer, taxable_income):
    brackets = get_brackets(taxpayer, policy)
    rates = list(reversed(policy["income_tax_rates"]))
    ordinary_income_tax = 0
    running_taxable_income = taxable_income
    i = 0
    for threshold in reversed(brackets):
        if taxable_income > threshold:
            applicable_taxable_income = running_taxable_income - threshold
            running_taxable_income = running_taxable_income - applicable_taxable_income
            ordinary_income_tax = ordinary_income_tax + (applicable_taxable_income * rates[i])
        i += 1

    return round(ordinary_income_tax, 2)


def fed_ctc(policy, taxpayer, agi):
    ctc = 0
    # TODO: Is there a phase in of the CTC?
    # Child Tax Credit Worksheet https://www.irs.gov/pub/irs-pdf/p972.pdf
    line1 = taxpayer["child_dep"] * policy["ctc_credit"]
    line4 = agi
    line5 = policy["ctc_po_threshold"][taxpayer['filing_status']]
    if line4 > line5:
        line6 = math.ceil((line4 - line5) / 1000) * 1000
    else:
        line6 = 0
    line7 = line6 * policy["ctc_po_rate"]
    if line1 > line7:
        line8 = line1 - line7
        ctc = line8
    else:
        ctc = 0
    return ctc


def fed_eitc(policy, taxpayer):
    eitc = 0
    # Publication 596 https://www.irs.gov/pub/irs-pdf/p596.pdf
    # TODO: TEST EITC. THIS IS JUST A DIRECT R TRANSLATION.
    income = taxpayer["ordinary_income1"] + taxpayer["ordinary_income2"]  # earned income
    c = min(taxpayer["child_dep"], 3)
    if taxpayer["filing_status"] != 1:
        if income < policy["eitc_threshold"][c]:
            eitc = income * (policy["eitc_max"][c] / policy["eitc_threshold"][c])
        elif (income >= policy["eitc_threshold"][c]) and (income <= policy["eitc_phaseout_single"][c]):
            eitc = policy["eitc_max"][c]
        elif (income > policy["eitc_phaseout_single"][c]):
            eitc = max(0, policy["eitc_max"][c] + ((policy["eitc_phaseout_single"][c] - income) * (policy["eitc_max"][c] / (policy["eitc_max_income_single"][c] - policy["eitc_phaseout_single"][c]))))
    else:
        if income < policy["eitc_threshold"][c]:
            eitc = income * (policy["eitc_max"][c] / policy["eitc_threshold"][c])
        elif (income >= policy["eitc_threshold"][c]) and (income <= policy["eitc_phaseout_married"][c]):
            eitc = policy["eitc_max"][c]
        elif (income > policy["eitc_phaseout_married"][c]):
            eitc = max(0, policy["eitc_max"][c] + ((policy["eitc_phaseout_married"][c] - income) * (policy["eitc_max"][c] / (policy["eitc_max_income_married"][c] - policy["eitc_phaseout_married"][c]))))
    return eitc


def fed_amt(policy, taxpayer, deduction_type, deductions, agi, pease_limitation_amt):
    amt = 0
    # Form 6251 https://www.irs.gov/pub/irs-pdf/f6251.pdf
    # Instructions https://www.irs.gov/pub/irs-pdf/i6251.pdf

    # Step 1: Define AMT income
    amt_income = 0
    if deduction_type == "itemized":
        line1 = agi - deductions  # also line41 on form 1040
        if taxpayer["ss_income"] > 0:
            line2 = taxpayer["medical_expenses"]
        else:
            line2 = 0
        line3 = taxpayer["sl_income_tax"] + taxpayer["sl_property_tax"]
        line5 = taxpayer["other_itemized"]  # TODO: check this logic before use
        if agi < policy["itemized_limitation_threshold"][taxpayer['filing_status']]:
            line6 = 0
        else:
            line6 = -pease_limitation_amt  # TODO: Check this behavior, it reverses the pease limitation
        amt_income = line1 + line2 + line3 + line5 + line6
        # only charity and mortgage allowed
    else:
        line1 = agi
        amt_income = line1

    # Step 2: Calculate AMT
    amt_exemption = policy["amt_exemption"][taxpayer['filing_status']]
    amt_exemption_po_threshold = policy["amt_exemption_po_threshold"][taxpayer['filing_status']]
    if amt_income > amt_exemption_po_threshold:
        # Exemption Worksheet https://www.irs.gov/pub/irs-pdf/i6251.pdf#en_US_2016_publink64277pd0e1980
        ws_line1 = amt_exemption
        ws_line2 = amt_income
        ws_line3 = amt_exemption_po_threshold
        ws_line4 = ws_line2 - ws_line3
        ws_line5 = ws_line4 * policy["amt_exemption_po_rate"]
        ws_line6 = max(0, ws_line1 - ws_line5)
        line29 = ws_line6
    else:
        line29 = amt_exemption
    amt_taxable_income = max(0, amt_income - line29)
    if amt_taxable_income < policy["amt_rate_threshold"]:
        amt = amt_taxable_income * policy["amt_rates"][0]  # 26% rate
    else:
        rate_diff = (policy["amt_rate_threshold"] * policy["amt_rates"][1]) - (policy["amt_rate_threshold"] * policy["amt_rates"][0])
        amt = amt_taxable_income * policy["amt_rates"][1] - rate_diff  # 28% rate

    return amt


def fed_qualified_income(policy, taxpayer, taxable_income, income_tax_before_credits):
    cap_gains_tax = 0
    line1 = taxable_income
    line2 = taxpayer["qualified_income"]
    line3 = 0  # Enter the amount from Form 1040, line 13.
    line4 = line3 + line2
    line5 = 0  # investment interest expense deduction
    line6 = line4 - line5
    line7 = line1 - line6  # taxable_income - qualified_income
    line8 = policy["cap_gains_lower_threshold"][taxpayer['filing_status']]
    line9 = min(line1, line8)
    line10 = min(line7, line9)
    line11 = line9 - line10  # this amount is taxed at 0%
    line12 = min(line1, line6)
    line14 = line12 - line11
    line15 = policy["cap_gains_upper_threshold"][taxpayer['filing_status']]
    line16 = min(line15, line1)
    line17 = line7 + line11
    line18 = line16 - line17
    line19 = min(line14, line18)
    line20 = line19 * policy["cap_gains_lower_rate"]
    line21 = line11 + line19
    line22 = line12 - line21
    line23 = line22 * policy["cap_gains_upper_rate"]
    line24 = fed_ordinary_income_tax(policy, taxpayer, line7)  # tax on line7
    line25 = line20 + line23 + line24
    line26 = income_tax_before_credits  # tax on line1
    cap_gains_tax = min(line25, line26)

    return cap_gains_tax


def get_brackets(taxpayer, policy):
    if taxpayer['filing_status'] == 0:
        brackets = policy["single_brackets"]
    elif taxpayer['filing_status'] == 1:
        brackets = policy["married_brackets"]
    else:
        brackets = policy["hoh_brackets"]

    return brackets
