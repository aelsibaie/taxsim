from context import *
import copy

policy = taxsim.current_law_policy


def test_zero_tax():
    taxpayer = misc_funcs.create_taxpayer()

    new_policy = copy.deepcopy(policy)
    new_policy['single_brackets'] = [0, 0]
    new_policy['income_tax_rates'] = [0, 0]
    taxes_owed = tax_funcs.fed_ordinary_income_tax(new_policy, taxpayer, 100000)

    assert taxes_owed == 0


def test_2_tax():
    taxpayer = misc_funcs.create_taxpayer()

    rate = 0.1

    new_policy = copy.deepcopy(policy)
    new_policy['single_brackets'] = [0, 100000 + 1]
    new_policy['income_tax_rates'] = [rate, 0.2]
    taxes_owed = tax_funcs.fed_ordinary_income_tax(new_policy, taxpayer, 100000)

    assert taxes_owed == 100000 * rate


def test_tons_of_brackets():
    taxpayer = misc_funcs.create_taxpayer()

    new_policy = copy.deepcopy(policy)
    new_policy['single_brackets'] = [
        0,
        1000,
        2000,
        3000,
        4000,
        5000,
        6000,
        7000,
        8000,
        9000,
        50000,
        75000,
        1000000]
    new_policy['income_tax_rates'] = [
        0.01,
        0.02,
        0.03,
        0.04,
        0.05,
        0.06,
        0.07,
        0.08,
        0.09,
        0.1,
        0.2,
        0.3,
        0.4]
    taxes_owed = tax_funcs.fed_ordinary_income_tax(new_policy, taxpayer, 100000)

    assert taxes_owed == 17050.0  # TODO: confirm by hand


def test_weird_brackets():
    taxpayer = misc_funcs.create_taxpayer()

    new_policy = copy.deepcopy(policy)
    new_policy['single_brackets'] = [0, 50000, 100000]
    new_policy['income_tax_rates'] = [0, 0.1, 0.2]
    taxes_owed = tax_funcs.fed_ordinary_income_tax(new_policy, taxpayer, 200000)

    new_policy2 = copy.deepcopy(policy)
    new_policy2['single_brackets'] = [50000, 50001, 100000]
    new_policy2['income_tax_rates'] = [0.1, 0.1, 0.2]
    taxes_owed2 = tax_funcs.fed_ordinary_income_tax(new_policy2, taxpayer, 200000)

    assert taxes_owed == taxes_owed2
