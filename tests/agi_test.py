from context import *

policy = taxsim.current_law_policy


def test_ss_income_agi():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy["taxable_ss_base_threshold"][0]
    taxpayer['ss_income'] = policy["taxable_ss_base_threshold"][0] * 2
    result = taxsim.calc_federal_taxes(taxpayer, policy)
    assert result['agi'] < result["gross_income"]


def test_ss_income_phasein2():
    # TODO: confirm this
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ss_income'] = policy["taxable_ss_base_amt"]
    result = taxsim.calc_federal_taxes(taxpayer, policy)
    assert result['agi'] < result["gross_income"]
