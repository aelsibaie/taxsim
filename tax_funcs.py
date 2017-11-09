import math


def fed_payroll(policy, taxpayer):
    """
    Get Federal payroll tax liabilities.

    Calculates total Federal payroll tax liabilities of both employees
    and employers. Adds any applicable medicare surtax to employees' liability
    if the combined ordinary income exceeds the defined threshold for the
    filing status.

    Args:
        policy (dict): A set of policy parameters, parsed from CSV.
        taxpayer (dict): An example taxpayer household, parsed from CSV.

    Returns:
        dict: Payroll tax values for employee and employer.
    """
    combined_ordinary_income = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2']
    payroll_taxes = {
        "employee": 0,
        "employer": 0
    }

    # Withholding Taxes
    for party in payroll_taxes:
        for income in [taxpayer['ordinary_income1'], taxpayer['ordinary_income2']]:
            social_security = (
                policy['ss_withholding_rate_{party}'.format(party=party)]
                * min(income, policy['ss_wage_base'])
            )
            medicare = (
                policy['medicare_withholding_rate_{party}'.format(party=party)]
                * min(income, policy['medicare_wage_base'])
            )
            payroll_taxes[party] += social_security + medicare

    # Additional Medicare Tax
    filing_status = taxpayer['filing_status']
    medicare_thresholds = policy['additional_medicare_tax_threshold']
    additional_medicare_tax_threshold = medicare_thresholds[filing_status]
    medicare_surtax = 0
    if combined_ordinary_income > additional_medicare_tax_threshold:
        taxable_medicare_surtax = (
            combined_ordinary_income
            - additional_medicare_tax_threshold
        )
        medicare_surtax = taxable_medicare_surtax * policy['additional_medicare_tax_rate']
    payroll_taxes['employee'] += medicare_surtax

    return payroll_taxes


def fed_agi(policy, taxpayer, ordinary_income_after_401k):
    """
    Get Federal AGI.

    Calculates the Federal Adjusted Gross Income, based on IRS Publication 915.

    Args:
        policy (dict): A set of policy parameters, parsed from CSV.
        taxpayer (dict): An example taxpayer household, parsed from CSV.
        ordinary_income_after_401k (float): Combined income, less 401k contributions.

    Returns:
        float: Federal adjusted gross income.
    """
    agi = ordinary_income_after_401k + taxpayer['business_income'] + taxpayer['qualified_income']

    # Social security income may not be fully taxable
    if taxpayer['ss_income'] > 0:
        ss_income = 0
        combined_income = agi + (taxpayer['ss_income'] * 0.5)
        # Publication 915 https://www.irs.gov/pub/irs-pdf/p915.pdf
        line10 = combined_income - policy["taxable_ss_base_threshold"][taxpayer['filing_status']]
        if line10 > 0:
            line11 = (
                policy["taxable_ss_top_threshold"][taxpayer['filing_status']]
                - policy["taxable_ss_base_threshold"][taxpayer['filing_status']]
            )
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
    """
    Get Federal taxable income.

    Takes a taxpayer's info, a given policy, and AGI to calculate taxable income,
    deductions, and exemptions.

    Args:
        policy (dict): A set of policy parameters, parsed from CSV.
        taxpayer (dict): An example taxpayer household, parsed from CSV.
        agi (float): Adjusted gross income of taxpayer household.

    Returns:
        Too many variables.
    """

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
        amt_over_threshold = (
            agi
            - policy["personal_exemption_po_threshold"][taxpayer['filing_status']]
        )
        line6 = math.ceil(amt_over_threshold / policy["personal_exemption_po_amt"])
        line7 = round(line6 * policy["personal_exemption_po_rate"], 3)
        line8 = personal_exemption_amt * line7
        personal_exemption_amt = max(0, personal_exemption_amt - line8)  # aka line9
    else:
        personal_exemption_amt = policy["personal_exemption"] * exemptions_claimed

    # Standard deduction
    standard_deduction = policy["standard_deduction"][taxpayer['filing_status']]
    if taxpayer["ss_income"] > 0:
        standard_deduction = (
            standard_deduction
            + (filers * policy["additional_standard_deduction"][taxpayer['filing_status']])
        )

    # Itemized deductions
    itemized_total = (
        taxpayer["medical_expenses"]
        + taxpayer["sl_income_tax"]
        + taxpayer["sl_property_tax"]
        + taxpayer["interest_paid"]
        + taxpayer["charity_contributions"]
        + taxpayer["other_itemized"]
        )
    # Check for phase out of itemized deductions
    # Itemized Deductions Worksheet—Line 29 https://www.irs.gov/pub/irs-pdf/i1040sca.pdf
    pease_limitation_amt = 0
    line1 = itemized_total
    # line2 could also include investment interest and casualty deductions
    line2 = taxpayer["medical_expenses"]
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


def house_2018_taxable_income(policy, taxpayer, agi):
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
        amt_over_threshold = (
            agi
            - policy["personal_exemption_po_threshold"][taxpayer['filing_status']]
        )
        line6 = math.ceil(amt_over_threshold / policy["personal_exemption_po_amt"])
        line7 = round(line6 * policy["personal_exemption_po_rate"], 3)
        line8 = personal_exemption_amt * line7
        personal_exemption_amt = max(0, personal_exemption_amt - line8)  # aka line9
    else:
        personal_exemption_amt = policy["personal_exemption"] * exemptions_claimed

    # Standard deduction
    standard_deduction = policy["standard_deduction"][taxpayer['filing_status']]
    # NEW: Eliminate additional standard deduction

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
    # line2 could also include investment interest and casualty deductions
    line2 = taxpayer["medical_expenses"]
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
    # Child Tax Credit Worksheet https://www.irs.gov/pub/irs-pdf/p972.pdf
    # Part 1
    ctc = 0
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
    else:
        line8 = 0

    # Additional Child Tax Credit
    actc_line1 = line8 # ctc
    actc_line2 = taxpayer['ordinary_income1'] + taxpayer['ordinary_income2'] # Earned income
    if actc_line2 > policy['additional_ctc_threshold']:
        actc_line3 = actc_line2 - policy['additional_ctc_threshold']
        actc_line4 = actc_line3 * policy['additional_ctc_rate']
    else:
        actc_line4 = 0 # No qualified ACTC income

    ctc = max(0, actc_line1 - actc_line4)
    actc = min(actc_line1, actc_line4)

    if line1 >= policy['additional_ctc_threshold']:
        if actc_line4 >= actc_line1:
            return ctc, actc
        else:
            print("WARNING: Taxpayer with earned income of $" + str(actc_line2) + " may NOT eligible for the additional child tax credit")
            # TODO: In this instance, the taxpayer might not actually be eligible for the full additional child tax credit"
            # To find the real amount of ACTC, we will need withholding and EITC data
            # This could overestimate the amount of ACTC owed
            return ctc, actc
    else:
        if actc_line4 == 0:
            return ctc, 0
        elif actc_line4 > 0:
            return ctc, actc


def fed_eitc(policy, taxpayer):
    # Publication 596 https://www.irs.gov/pub/irs-pdf/p596.pdf
    income = taxpayer["ordinary_income1"] + taxpayer["ordinary_income2"]  # earned income
    dependentCount = min(taxpayer["child_dep"], 3)
    status = ("married", "single")[taxpayer["filing_status"] != 1]
    EITC_THRESHOLD = policy["eitc_threshold"][dependentCount]
    EITC_MAX = policy["eitc_max"][dependentCount]
    EITC_PHASEOUT = policy["eitc_phaseout_" + status][dependentCount]
    EITC_MAX_INCOME = policy["eitc_max_income_" + status][dependentCount]
    if income < EITC_THRESHOLD:
        return income * (EITC_MAX / EITC_THRESHOLD)
    if income >= EITC_THRESHOLD and income <= EITC_PHASEOUT:
        return EITC_MAX
    if income > EITC_PHASEOUT:
        return max(
            0,
            EITC_MAX + (
                (EITC_PHASEOUT - income)
                * (EITC_MAX / (EITC_MAX_INCOME - EITC_PHASEOUT))
            )
        )


def fed_amt(policy, taxpayer, deduction_type, deductions, agi, pease_limitation_amt, income_tax_before_credits):
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
        # TODO: check this logic before use
        line5 = taxpayer["other_itemized"]
        if agi < policy["itemized_limitation_threshold"][taxpayer['filing_status']]:
            line6 = 0
        else:
            # TODO: Check this behavior, it reverses the pease limitation
            line6 = -pease_limitation_amt
        amt_income = line1 + line2 + line3 + line5 + line6
        # only charity and mortgage allowed
    else:
        line1 = agi
        amt_income = line1

    # Step 2: Calculate AMT Exemption
    amt_exemption = policy["amt_exemption"][taxpayer['filing_status']]
    amt_exemption_po_threshold = policy["amt_exemption_po_threshold"][taxpayer['filing_status']]
    if amt_income > amt_exemption_po_threshold:
        # Exemption Worksheet
        # https://www.irs.gov/pub/irs-pdf/i6251.pdf#en_US_2016_publink64277pd0e1980
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

    # Step 3: Calculate AMT
    # After this if statement, amt is equivalent to line 31 and 33 of form 6251
    if amt_taxable_income < policy["amt_rate_threshold"]:
        amt = amt_taxable_income * policy["amt_rates"][0]  # 26% rate
    else:
        rate_diff = (
            (policy["amt_rate_threshold"] * policy["amt_rates"][1])
            - (policy["amt_rate_threshold"] * policy["amt_rates"][0])
        )
        amt = amt_taxable_income * policy["amt_rates"][1] - rate_diff  # 28% rate

    line34 = income_tax_before_credits
    amt = max(0, amt - line34) # aka line35

    return amt


def fed_qualified_income(policy, taxpayer, taxable_income, income_tax_before_credits):
    # Qualified Dividends and Capital Gain Tax Worksheet—Line 44, Form 1040
    # https://apps.irs.gov/app/vita/content/globalmedia/capital_gain_tax_worksheet_1040i.pdf
    cap_gains_tax = 0
    line1 = taxable_income
    line2 = taxpayer["qualified_income"]
    line3 = 0  # Enter the amount from Form 1040, line 13.
    line4 = line3 + line2
    line5 = 0  # investment interest expense deduction
    line6 = max(0, line4 - line5)
    line7 = max(0, line1 - line6)  # taxable_income - qualified_income
    line8 = policy["cap_gains_lower_threshold"][taxpayer['filing_status']]
    line9 = min(line1, line8)
    line10 = min(line7, line9)
    line11 = line9 - line10  # this amount is taxed at 0%
    line12 = min(line1, line6)
    line13 = line11
    line14 = line12 - line13
    line15 = policy["cap_gains_upper_threshold"][taxpayer['filing_status']]
    line16 = min(line15, line1)
    line17 = line7 + line11
    line18 = max(0, line16 - line17)
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


def house_2018_qualified_income(policy, taxpayer, taxable_income, income_tax_before_credits, po_amount):
    # Qualified Dividends and Capital Gain Tax Worksheet—Line 44, Form 1040
    # https://apps.irs.gov/app/vita/content/globalmedia/capital_gain_tax_worksheet_1040i.pdf
    cap_gains_tax = 0
    line1 = taxable_income
    line2 = taxpayer["qualified_income"]
    line3 = 0  # Enter the amount from Form 1040, line 13.
    line4 = line3 + line2
    line5 = 0  # investment interest expense deduction
    line6 = max(0, line4 - line5)
    line7 = max(0, line1 - line6)  # taxable_income - qualified_income
    line8 = policy["cap_gains_lower_threshold"][taxpayer['filing_status']]
    line9 = min(line1, line8)
    line10 = min(line7, line9)
    line11 = line9 - line10  # this amount is taxed at 0%
    line12 = min(line1, line6)
    line13 = line11
    line14 = line12 - line13
    line15 = policy["cap_gains_upper_threshold"][taxpayer['filing_status']]
    line16 = min(line15, line1)
    line17 = line7 + line11
    line18 = line16 - line17
    line18 = max(0, line16 - line17)
    line19 = min(line14, line18)
    line20 = line19 * policy["cap_gains_lower_rate"]
    line21 = line11 + line19
    line22 = line12 - line21
    line23 = line22 * policy["cap_gains_upper_rate"]
    line24 = fed_ordinary_income_tax(
        policy,
        taxpayer,
        line7 - taxpayer["business_income"]
    ) + (taxpayer["business_income"] * 0.25) + po_amount  # tax on line7
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
