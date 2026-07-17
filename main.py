import argparse
import os
import sys


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run the booking ETL cron")
    parser.add_argument("--cron-name", default="booking", help="Cron job file name")
    parser.add_argument("--updated_from", required=True)
    parser.add_argument("--updated_to", required=True)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])

    if args.cron_name != "booking":
        raise SystemExit("Only the 'booking' cron job is supported")

    sys.path.insert(0, os.path.join(os.getcwd(), "cron_app"))
    sys.path.insert(1, os.path.join(os.getcwd(), "api_app"))

    from cron_app.cronjobs.booking import run

    run(updated_from=args.updated_from, updated_to=args.updated_to)


if __name__ == "__main__":
    main()
