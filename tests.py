from taxsim import current_law_policy, calc_federal_taxes
from misc_funcs import create_taxpayer

def babies_first_test():
    taxpayer = create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    result = calc_federal_taxes(taxpayer, current_law_policy)
    assert result['amt'] > 0