from context import *

policy = taxsim.current_law_policy


def test_sched_se():
    # ensure business_income is treated better under ordinary tax code
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    result1 = taxsim.calc_federal_taxes(taxpayer, policy)

    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['business_income'] = 100000
    result2 = taxsim.calc_federal_taxes(taxpayer, policy)

    assert result1['tax_wedge'] > result2['tax_wedge']


def test_qualified_income():
    # ensure qualified_income is taxed at a lower rate than ordinary_income1
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 100000
    result1 = taxsim.calc_federal_taxes(taxpayer, policy)

    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['qualified_income'] = 100000
    result2 = taxsim.calc_federal_taxes(taxpayer, policy)

    assert result1['income_tax_after_credits'] > result2['income_tax_after_credits']


def test_ss_income1():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 50000
    result1 = taxsim.calc_federal_taxes(taxpayer, policy)

    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ss_income'] = 50000
    result2 = taxsim.calc_federal_taxes(taxpayer, policy)

    assert result1['taxable_income'] > result2['taxable_income']


def test_ss_income2():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 50000
    result1 = taxsim.calc_federal_taxes(taxpayer, policy)

    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ss_income'] = 50000
    result2 = taxsim.calc_federal_taxes(taxpayer, policy)

    assert result1['income_tax_after_credits'] > result2['income_tax_after_credits']


def test_401k_contributions():
    # ensure 401k_contributions reduce AGI
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 50000
    taxpayer['401k_contributions'] = 10000
    result1 = taxsim.calc_federal_taxes(taxpayer, policy)

    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 50000
    result2 = taxsim.calc_federal_taxes(taxpayer, policy)

    assert result1['agi'] < result2['agi']


def test_0_income():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = 0
    result = taxsim.calc_federal_taxes(taxpayer, policy)

    assert result['avg_effective_tax_rate'] == 0


def test_additional_standard_deduction():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ss_income'] = policy['taxable_ss_base_threshold'][0]
    result = taxsim.calc_federal_taxes(taxpayer, policy)

    assert result['deductions'] > policy['standard_deduction'][0]
