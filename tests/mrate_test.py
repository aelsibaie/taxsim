from context import *
import copy

policy = taxsim.current_law_policy


def test_marginal_income_tax_rate():
    taxpayer = misc_funcs.create_taxpayer()

    taxpayer['ordinary_income1'] = 100000

    results = taxsim.calc_federal_taxes(taxpayer, policy)

    assert results['marginal_income_tax_rate'] > 0.0001


def test_marginal_business_income_tax_rate():
    taxpayer = misc_funcs.create_taxpayer()

    taxpayer['business_income'] = 100000

    results = taxsim.calc_federal_taxes(taxpayer, policy)

    assert results['marginal_business_income_tax_rate'] > 0.0001


def test_marginal_income_tax_rate0():
    taxpayer = misc_funcs.create_taxpayer()

    taxpayer['ordinary_income1'] = 0

    results = taxsim.calc_federal_taxes(taxpayer, policy)

    assert results['marginal_income_tax_rate'] < 0.0001


def test_marginal_business_income_tax_rate0():
    # this edge case doesn't make sense any more after sched se was included
    taxpayer = misc_funcs.create_taxpayer()

    taxpayer['business_income'] = 0

    results = taxsim.calc_federal_taxes(taxpayer, policy)

    assert results['marginal_business_income_tax_rate'] > 0.0001
