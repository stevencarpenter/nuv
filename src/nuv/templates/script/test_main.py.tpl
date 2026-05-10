from main import main


def test_main_returns_zero() -> None:
    assert main([]) == 0


def test_main_rejects_unknown_option() -> None:
    assert main(["--bogus"]) == 2
