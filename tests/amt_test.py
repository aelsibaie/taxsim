from context import *


def test_amt():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['qualified_income'] = taxsim.current_law_policy["single_brackets"][-1]
    result = taxsim.calc_federal_taxes(taxpayer, taxsim.current_law_policy)
    assert result['amt'] > 0
