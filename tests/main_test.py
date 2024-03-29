from context import *
import pytest

policy = taxsim.current_law_policy


def test_main_exit():
    with pytest.raises(SystemExit) as exit_code:
        taxsim.main()
    assert exit_code.type == SystemExit


def test_main_success():
    with pytest.raises(SystemExit) as exit_code:
        taxsim.main()
    assert exit_code.value.code == 0
