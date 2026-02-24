from nuv.cli import main


def test_no_command_returns_1() -> None:
    assert main([]) == 1
