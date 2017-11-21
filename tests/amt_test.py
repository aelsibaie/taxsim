from context import *


def test_amt():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['qualified_income'] = 1000000
    result = taxsim.calc_federal_taxes(taxpayer, taxsim.current_law_policy)
    assert result['amt'] > 0
