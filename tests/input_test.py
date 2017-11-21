from context import *
import pytest

policy = taxsim.current_law_policy


def test_hoh_but_no_child():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    taxpayer['filing_status'] = 2
    with pytest.raises(ValueError):
        result = taxsim.calc_federal_taxes(taxpayer, policy)


def test_single_with_child():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    taxpayer['filing_status'] = 0
    taxpayer['child_dep'] = 1
    with pytest.raises(ValueError):
        result = taxsim.calc_federal_taxes(taxpayer, policy)
