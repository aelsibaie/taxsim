from context import *
import pytest

policy = taxsim.current_law_policy


def test_load_taxpayers():
    taxpayers = csv_parser.load_taxpayers('taxpayers.csv')
    assert taxpayers[0]['ordinary_income1'] == 30000
