from context import *


def test_ctc():
    # ensure CTC is working
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = taxsim.current_law_policy["ctc_po_threshold"][1]
    taxpayer['child_dep'] = 1
    taxpayer['filing_status'] = 1
    result1 = taxsim.calc_federal_taxes(taxpayer, taxsim.current_law_policy)

    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = taxsim.current_law_policy["ctc_po_threshold"][1]
    taxpayer['child_dep'] = 0
    taxpayer['filing_status'] = 1
    result2 = taxsim.calc_federal_taxes(taxpayer, taxsim.current_law_policy)

    ctc_benefit = result2["income_tax_after_credits"] - result1["income_tax_after_credits"]

    # this also captures some of the personal exemption, thus > and not ==
    assert ctc_benefit > taxsim.current_law_policy["ctc_credit"]


def test_ctc_po():
    taxpayer = misc_funcs.create_taxpayer()
    # at 2x the ctc_po_threshold, the CTC should be fully phased out
    taxpayer['ordinary_income1'] = taxsim.current_law_policy["ctc_po_threshold"][1] * 2
    taxpayer['child_dep'] = 1
    taxpayer['filing_status'] = 1
    result = taxsim.calc_federal_taxes(taxpayer, taxsim.current_law_policy)
    assert result["ctc"] == 0 and result["actc"] == 0
