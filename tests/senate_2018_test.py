from context import *

policy = taxsim.current_law_policy

def test_senate_ordinary_income():
    taxpayer = misc_funcs.create_taxpayer()
    
    taxpayer['ordinary_income1'] = 100000
    
    result_currentlaw = taxsim.calc_federal_taxes(taxpayer, policy)
    result_senate2018 = taxsim.calc_senate_2018_taxes(taxpayer, taxsim.senate_2018_policy)
    
    assert result_currentlaw['tax_burden'] > result_senate2018["tax_burden"]

def test_senate_std_deduction():
    taxpayer = misc_funcs.create_taxpayer()
    
    taxpayer['ordinary_income1'] = 100000
    
    result_currentlaw = taxsim.calc_federal_taxes(taxpayer, policy)
    result_senate2018 = taxsim.calc_senate_2018_taxes(taxpayer, taxsim.senate_2018_policy)
    
    assert result_currentlaw['deductions'] < result_senate2018["deductions"]

def test_senate_personal_exemption_elimination():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = taxsim.senate_2018_policy['personal_exemption_po_threshold'][0] / 2
    result_senate2018 = taxsim.calc_senate_2018_taxes(taxpayer, taxsim.senate_2018_policy)
    
    assert result_senate2018["personal_exemption_amt"] == 0

def test_senate_personal_exemption_elimination2():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy['personal_exemption_po_threshold'][0] / 2
    result_senate2018 = taxsim.calc_senate_2018_taxes(taxpayer, taxsim.senate_2018_policy)
    
    assert result_senate2018["personal_exemption_amt"] == 0

def test_senate_pease_elimination():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy['itemized_limitation_threshold'][0] * 2
    taxpayer['charity_contributions'] = policy['standard_deduction'][0] * 2
    result_senate2018 = taxsim.calc_senate_2018_taxes(taxpayer, taxsim.senate_2018_policy)
    
    assert result_senate2018["pease_limitation_amt"] == 0

def test_senate_pease_elimination():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['ordinary_income1'] = policy['itemized_limitation_threshold'][0] * 2
    taxpayer['charity_contributions'] = policy['standard_deduction'][0] * 2
    result_senate2018 = taxsim.calc_senate_2018_taxes(taxpayer, taxsim.senate_2018_policy)
    
    assert result_senate2018["pease_limitation_amt"] == 0

def test_senate_ctc_larger():
    taxpayer = misc_funcs.create_taxpayer()
    
    taxpayer['ordinary_income1'] = 50000
    taxpayer['filing_status'] = 2
    taxpayer['child_dep'] = 1
    
    result_currentlaw = taxsim.calc_federal_taxes(taxpayer, policy)
    result_senate2018 = taxsim.calc_senate_2018_taxes(taxpayer, taxsim.senate_2018_policy)
    
    assert result_currentlaw['actc'] < result_senate2018["actc"]
