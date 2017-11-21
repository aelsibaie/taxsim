from context import *

policy = taxsim.current_law_policy


def test_personal_exemption_nonchild():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy["personal_exemption_po_threshold"][0]
    taxpayer['nonchild_dep'] = 1
    result1 = taxsim.calc_federal_taxes(taxpayer, policy)

    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['business_income'] = policy["personal_exemption_po_threshold"][0]
    result2 = taxsim.calc_federal_taxes(taxpayer, policy)

    assert result1['personal_exemption_amt'] == (
        result2['personal_exemption_amt'] + policy["personal_exemption"])


def test_personal_exemption_child():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy["personal_exemption_po_threshold"][1]
    taxpayer['child_dep'] = 1
    taxpayer['filing_status'] = 1
    result1 = taxsim.calc_federal_taxes(taxpayer, policy)

    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['business_income'] = policy["personal_exemption_po_threshold"][1]
    taxpayer['filing_status'] = 1
    result2 = taxsim.calc_federal_taxes(taxpayer, policy)

    assert result1['personal_exemption_amt'] == (
        result2['personal_exemption_amt'] + policy["personal_exemption"])


def test_personal_exemption_nonchild_po():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy["personal_exemption_po_threshold"][0] * 2
    taxpayer['nonchild_dep'] = 1
    result1 = taxsim.calc_federal_taxes(taxpayer, policy)

    assert result1['personal_exemption_amt'] == 0


def test_personal_exemption_child_po():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy["personal_exemption_po_threshold"][2] * 2
    taxpayer['child_dep'] = 1
    taxpayer['filing_status'] = 2
    result1 = taxsim.calc_federal_taxes(taxpayer, policy)

    assert result1['personal_exemption_amt'] == 0
