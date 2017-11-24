from context import *
import pytest

policy = taxsim.current_law_policy


def test_git_version():
    git_version = misc_funcs.git_version()
    assert len(git_version) == 40

