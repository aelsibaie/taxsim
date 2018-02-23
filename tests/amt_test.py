from context import *


def test_amt():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['qualified_income'] = taxsim.current_law_policy["single_brackets"][-1]
    result = taxsim.calc_federal_taxes(taxpayer, taxsim.current_law_policy)
    assert result['amt'] > 0


def test_amt_salt():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 300000
    taxpayer['sl_income_tax'] = 25000
    taxpayer['sl_property_tax'] = 25000
    result = taxsim.calc_federal_taxes(taxpayer, taxsim.current_law_policy)
    assert result['amt'] > 0


def test_no_amt():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 300000
    result = taxsim.calc_federal_taxes(taxpayer, taxsim.current_law_policy)
    assert result['amt'] == 0


def test_qualified_amt_greater_than_ord():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 300000
    taxpayer['sl_income_tax'] = 25000
    taxpayer['sl_property_tax'] = 25000
    result = taxsim.calc_federal_taxes(taxpayer, taxsim.current_law_policy)

    taxpayer2 = misc_funcs.create_taxpayer()
    taxpayer2['qualified_income'] = 300000
    taxpayer2['sl_income_tax'] = 25000
    taxpayer2['sl_property_tax'] = 25000
    result2 = taxsim.calc_federal_taxes(taxpayer2, taxsim.current_law_policy)

    assert result['amt'] > result2['amt']


def test_qualified_amt_greater_than_ord():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['qualified_income'] = 1000000000000000  # this represents the concept "as income approaches infinity"
    result = taxsim.calc_federal_taxes(taxpayer, taxsim.current_law_policy)

    assert result['avg_effective_tax_rate_wo_payroll'] < taxsim.current_law_policy['amt_rates'][-1]
