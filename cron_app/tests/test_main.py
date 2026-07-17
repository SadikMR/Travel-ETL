from main import parse_args


def test_parse_args_reads_dates() -> None:
    args = parse_args(["--updated_from", "2026-07-12", "--updated_to", "2026-07-13"])

    assert args.updated_from == "2026-07-12"
    assert args.updated_to == "2026-07-13"
