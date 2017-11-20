import pytest
import os
from taxsim import taxsim, csv_parser, misc_funcs


def test_amt():
    taxpayer = misc_funcs.create_taxpayer()
    taxpayer['qualified_income'] = 1000000
    CURRENT_LAW_FILE = os.path.abspath("./params/current_law_2018.csv")
    current_law_policy = csv_parser.load_policy(CURRENT_LAW_FILE)
    result = taxsim.calc_federal_taxes(taxpayer, current_law_policy)
    assert result['amt'] > 0
