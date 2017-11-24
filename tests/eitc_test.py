from context import *

policy = taxsim.current_law_policy

def test_eitc_phase_in():
    # before max credit
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy["eitc_threshold"][0] / 2
    result = taxsim.calc_federal_taxes(taxpayer, policy)
    assert result['eitc'] < policy["eitc_max"][0]



def test_eitc_threshold():
    # edge case
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy["eitc_threshold"][0]
    result = taxsim.calc_federal_taxes(taxpayer, policy)
    assert result['eitc'] == policy["eitc_max"][0]


def test_eitc_phaseing_out1():
    # mid point in phase out, check if eitc is less than max
    taxpayer = misc_funcs.create_taxpayer()
    midpoint = (policy['eitc_max_income_single'][0] - policy["eitc_phaseout_single"][0]) / 2
    taxpayer['ordinary_income1'] = policy["eitc_phaseout_single"][0] + midpoint
    result = taxsim.calc_federal_taxes(taxpayer, policy)
    assert result['eitc'] < policy["eitc_max"][0]

def test_eitc_phaseing_out2():
    # mid point in phase out, check if eitc is not 0
    taxpayer = misc_funcs.create_taxpayer()
    midpoint = (policy['eitc_max_income_single'][0] - policy["eitc_phaseout_single"][0]) / 2
    taxpayer['ordinary_income1'] = policy["eitc_phaseout_single"][0] + midpoint
    result = taxsim.calc_federal_taxes(taxpayer, policy)
    assert result['eitc'] != 0

def test_eitc_phased_out1():
    # edge case
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy['eitc_max_income_single'][0]
    result = taxsim.calc_federal_taxes(taxpayer, policy)
    assert result['eitc'] == 0

def test_eitc_phased_out2():
    # well above edge case
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy['eitc_max_income_single'][0] * 2
    result = taxsim.calc_federal_taxes(taxpayer, policy)
    assert result['eitc'] == 0