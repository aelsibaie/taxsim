from context import *

policy = taxsim.current_law_policy
policy2 = taxsim.senate_2018_policy


def test_pease_limiting():
    # Test that Pease is kicking in when the filer has 2x the itemized_limitation_threshold
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy["itemized_limitation_threshold"][0] * 2
    taxpayer['sl_income_tax'] = policy["standard_deduction"][0] * 2
    result = taxsim.calc_federal_taxes(taxpayer, policy)
    assert result['pease_limitation_amt'] > 0


def test_pease_only_itemized():
    # Test that Pease doesn't kick in if the filer is taking the standard deduction
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy["itemized_limitation_threshold"][0] * 2
    result = taxsim.calc_federal_taxes(taxpayer, policy)
    assert result['pease_limitation_amt'] == 0


def test_pease_threshold():
    # Test the edge case right before Pease should kick in
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy["itemized_limitation_threshold"][0]
    taxpayer['sl_income_tax'] = policy["standard_deduction"][0] * 2
    result = taxsim.calc_federal_taxes(taxpayer, policy)
    assert result['pease_limitation_amt'] == 0


def test_pease_threshold_safe():
    # Test a case plenty before Pease should kick in
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy["itemized_limitation_threshold"][0] / 2
    taxpayer['sl_income_tax'] = policy["standard_deduction"][0] * 2
    result = taxsim.calc_federal_taxes(taxpayer, policy)
    assert result['pease_limitation_amt'] == 0


def test_limit_charity_deduction1():
    # Test a case plenty before Pease should kick in
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    taxpayer['charity_contributions'] = (policy["charitable_cont_limit"] * 100000) - 1
    result = taxsim.calc_federal_taxes(taxpayer, policy)

    taxpayer2 = misc_funcs.create_taxpayer()
    taxpayer2['ordinary_income1'] = 100000
    taxpayer2['charity_contributions'] = (policy["charitable_cont_limit"] * 100000)
    result2 = taxsim.calc_federal_taxes(taxpayer2, policy)

    assert result['taxable_income'] > result2['taxable_income']


def test_limit_charity_deduction2():
    # Test a case plenty before Pease should kick in
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    taxpayer['charity_contributions'] = (policy["charitable_cont_limit"] * 100000) + 1
    result = taxsim.calc_federal_taxes(taxpayer, policy)

    taxpayer2 = misc_funcs.create_taxpayer()
    taxpayer2['ordinary_income1'] = 100000
    taxpayer2['charity_contributions'] = (policy["charitable_cont_limit"] * 100000)
    result2 = taxsim.calc_federal_taxes(taxpayer2, policy)

    assert result['taxable_income'] == result2['taxable_income']


def test_limit_charity_deduction3():
    # Test a case plenty before Pease should kick in
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    taxpayer['charity_contributions'] = (policy2["charitable_cont_limit"] * 100000) - 1
    result = taxsim.calc_senate_2018_taxes(taxpayer, policy2)

    taxpayer2 = misc_funcs.create_taxpayer()
    taxpayer2['ordinary_income1'] = 100000
    taxpayer2['charity_contributions'] = (policy2["charitable_cont_limit"] * 100000)
    result2 = taxsim.calc_senate_2018_taxes(taxpayer2, policy2)

    assert result['taxable_income'] > result2['taxable_income']


def test_limit_charity_deduction4():
    # Test a case plenty before Pease should kick in
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    taxpayer['charity_contributions'] = (policy2["charitable_cont_limit"] * 100000) + 1
    result = taxsim.calc_senate_2018_taxes(taxpayer, policy2)

    taxpayer2 = misc_funcs.create_taxpayer()
    taxpayer2['ordinary_income1'] = 100000
    taxpayer2['charity_contributions'] = (policy2["charitable_cont_limit"] * 100000)
    result2 = taxsim.calc_senate_2018_taxes(taxpayer2, policy2)

    assert result['taxable_income'] == result2['taxable_income']


def test_limit_mort_int_ded1():
    # Test a case plenty before Pease should kick in
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    taxpayer['interest_paid'] = (policy["mortgage_interest_cap"] * taxsim.ASSUMED_MORTGAGE_RATE) - 1
    result = taxsim.calc_federal_taxes(taxpayer, policy)

    taxpayer2 = misc_funcs.create_taxpayer()
    taxpayer2['ordinary_income1'] = 100000
    taxpayer2['interest_paid'] = (policy["mortgage_interest_cap"] * taxsim.ASSUMED_MORTGAGE_RATE)
    result2 = taxsim.calc_federal_taxes(taxpayer2, policy)

    assert result['taxable_income'] > result2['taxable_income']


def test_limit_mort_int_ded2():
    # Test a case plenty before Pease should kick in
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    taxpayer['interest_paid'] = (policy["mortgage_interest_cap"] * taxsim.ASSUMED_MORTGAGE_RATE) + 1
    result = taxsim.calc_federal_taxes(taxpayer, policy)

    taxpayer2 = misc_funcs.create_taxpayer()
    taxpayer2['ordinary_income1'] = 100000
    taxpayer2['interest_paid'] = (policy["mortgage_interest_cap"] * taxsim.ASSUMED_MORTGAGE_RATE)
    result2 = taxsim.calc_federal_taxes(taxpayer2, policy)

    assert result['taxable_income'] == result2['taxable_income']


def test_limit_mort_int_ded3():
    # Test a case plenty before Pease should kick in
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    taxpayer['interest_paid'] = (policy2["mortgage_interest_cap"] * taxsim.ASSUMED_MORTGAGE_RATE) - 1
    result = taxsim.calc_senate_2018_taxes(taxpayer, policy2)

    taxpayer2 = misc_funcs.create_taxpayer()
    taxpayer2['ordinary_income1'] = 100000
    taxpayer2['interest_paid'] = (policy2["mortgage_interest_cap"] * taxsim.ASSUMED_MORTGAGE_RATE)
    result2 = taxsim.calc_senate_2018_taxes(taxpayer2, policy2)

    assert result['taxable_income'] > result2['taxable_income']


def test_limit_mort_int_ded4():
    # Test a case plenty before Pease should kick in
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    taxpayer['interest_paid'] = (policy2["mortgage_interest_cap"] * taxsim.ASSUMED_MORTGAGE_RATE) - 1
    result = taxsim.calc_senate_2018_taxes(taxpayer, policy2)

    taxpayer2 = misc_funcs.create_taxpayer()
    taxpayer2['ordinary_income1'] = 100000
    taxpayer2['interest_paid'] = (policy2["mortgage_interest_cap"] * taxsim.ASSUMED_MORTGAGE_RATE)
    result2 = taxsim.calc_senate_2018_taxes(taxpayer2, policy2)

    assert result['taxable_income'] > result2['taxable_income']
