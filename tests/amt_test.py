import pytest

from taxsim import current_law_policy, calc_federal_taxes
from misc_funcs import create_taxpayer


def test_amt():
    taxpayer = create_taxpayer()
    taxpayer['qualified_income'] = 1000000
    result = calc_federal_taxes(taxpayer, current_law_policy)
    assert result['amt'] > 0
