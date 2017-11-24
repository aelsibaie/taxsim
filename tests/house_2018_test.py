from context import *

policy = taxsim.current_law_policy


def test_house_ordinary_income():
    taxpayer = misc_funcs.create_taxpayer()

    taxpayer['ordinary_income1'] = 100000

    result_currentlaw = taxsim.calc_federal_taxes(taxpayer, policy)
    result_house2018 = taxsim.calc_house_2018_taxes(taxpayer, taxsim.house_2018_policy)

    assert result_currentlaw['tax_burden'] > result_house2018["tax_burden"]


def test_house_std_deduction():
    taxpayer = misc_funcs.create_taxpayer()

    taxpayer['ordinary_income1'] = 100000

    result_currentlaw = taxsim.calc_federal_taxes(taxpayer, policy)
    result_house2018 = taxsim.calc_house_2018_taxes(taxpayer, taxsim.house_2018_policy)

    assert result_currentlaw['deductions'] < result_house2018["deductions"]


def test_house_personal_exemption_elimination():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = taxsim.house_2018_policy['personal_exemption_po_threshold'][0] / 2
    result_house2018 = taxsim.calc_house_2018_taxes(taxpayer, taxsim.house_2018_policy)

    assert result_house2018["personal_exemption_amt"] == 0


def test_house_personal_exemption_elimination2():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy['personal_exemption_po_threshold'][0] / 2
    result_house2018 = taxsim.calc_house_2018_taxes(taxpayer, taxsim.house_2018_policy)

    assert result_house2018["personal_exemption_amt"] == 0


def test_house_pease_elimination():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy['itemized_limitation_threshold'][0] * 2
    taxpayer['charity_contributions'] = policy['standard_deduction'][0] * 2
    result_house2018 = taxsim.calc_house_2018_taxes(taxpayer, taxsim.house_2018_policy)

    assert result_house2018["pease_limitation_amt"] == 0


def test_house_pease_elimination():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy['itemized_limitation_threshold'][0] * 2
    taxpayer['charity_contributions'] = policy['standard_deduction'][0] * 2
    result_house2018 = taxsim.calc_house_2018_taxes(taxpayer, taxsim.house_2018_policy)

    assert result_house2018["pease_limitation_amt"] == 0


def test_house_ctc_larger():
    taxpayer = misc_funcs.create_taxpayer()

    taxpayer['ordinary_income1'] = 50000
    taxpayer['filing_status'] = 2
    taxpayer['child_dep'] = 1

    result_currentlaw = taxsim.calc_federal_taxes(taxpayer, policy)
    result_house2018 = taxsim.calc_house_2018_taxes(taxpayer, taxsim.house_2018_policy)

    assert result_currentlaw['actc'] < result_house2018["actc"]


def test_house_business_income():
    taxpayer = misc_funcs.create_taxpayer()

    taxpayer['business_income'] = 100000

    result_currentlaw = taxsim.calc_federal_taxes(taxpayer, policy)
    result_house2018 = taxsim.calc_house_2018_taxes(taxpayer, taxsim.house_2018_policy)

    assert result_currentlaw['tax_burden'] > result_house2018["tax_burden"]
