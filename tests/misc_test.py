from context import *
import pytest

policy = taxsim.current_law_policy


def test_git_version():
    git_version = misc_funcs.git_version()
    assert len(git_version) == 40

def test_load_taxpayers():
    taxpayers = csv_parser.load_taxpayers('taxpayers.csv')
    assert taxpayers[0]['ordinary_income1'] == 30000
