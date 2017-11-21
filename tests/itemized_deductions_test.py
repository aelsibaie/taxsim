from context import *

policy = taxsim.current_law_policy


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
