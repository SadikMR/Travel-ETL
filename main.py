import argparse
import importlib
import sys
from typing import List, Optional

CRON_PACKAGE = "cron_app.cronjobs"

# Ensure app directories are importable by plain module names used in cron modules
import os
sys.path.insert(0, os.path.join(os.getcwd(), "cron_app"))
sys.path.insert(0, os.path.join(os.getcwd(), "api_app"))
# Ensure cron_app appears before api_app so plain `import config` resolves to cron_app/config.py
cron_path = os.path.join(os.getcwd(), "cron_app")
api_path = os.path.join(os.getcwd(), "api_app")
if sys.path[0] != cron_path:
    if cron_path in sys.path:
        sys.path.remove(cron_path)
    sys.path.insert(0, cron_path)
if api_path in sys.path:
    sys.path.remove(api_path)
sys.path.insert(1, api_path)


def run_cron_by_name(name: str, updated_from: Optional[str], updated_to: Optional[str]) -> None:
    module_name = f"{CRON_PACKAGE}.{name}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        # Fallback to loading by file path when packages are not installed
        from pathlib import Path

        path = Path("cron_app") / "cronjobs" / f"{name}.py"
        if not path.exists():
            print(f"Cron '{name}' not found (tried {module_name} and {path}).")
            return

        spec = importlib.util.spec_from_file_location(f"cron_job_{name}", str(path))
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

    # Preferred: module exposes a run(updated_from, updated_to) function
    if hasattr(module, "run"):
        try:
            module.run(updated_from=updated_from, updated_to=updated_to)
            return
        except TypeError:
            # fall through to class-based runner
            pass

    # Fallback: look for a Cron class (e.g., BookingCron)
    for attr in dir(module):
        if attr.lower().endswith("cron"):
            CronCls = getattr(module, attr)
            try:
                instance = CronCls(updated_from=updated_from, updated_to=updated_to)
                instance.run()
                return
            except TypeError:
                # constructor signature mismatch; try default
                try:
                    instance = CronCls()
                    instance.run()
                    return
                except Exception as e:
                    print(f"Failed to run cron '{name}': {e}")
                    return

    print(f"Cron '{name}' does not provide a runnable entry (no run() or *Cron class).")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run cron jobs by name")
    parser.add_argument("-cron-name", "--cron-name", dest="cron_names", action="append", required=True,
                        help="Name of cron module under cron_app/cronjobs (can be specified multiple times)")
    parser.add_argument("--updated_from", dest="updated_from", help="Updated from date (YYYY-MM-DD)")
    parser.add_argument("--updated_to", dest="updated_to", help="Updated to date (YYYY-MM-DD)")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv or sys.argv[1:])

    # Create the cron_app Flask app and run cron jobs inside its app context
    try:
        cron_pkg = importlib.import_module("cron_app")
        app = cron_pkg.create_app()
    except Exception:
        app = None

    if app is None:
        # No Flask app available; run crons without app context
        for name in args.cron_names:
            print(f"Running cron: {name} (from={args.updated_from} to={args.updated_to})")
            run_cron_by_name(name, args.updated_from, args.updated_to)
        return

    with app.app_context():
        for name in args.cron_names:
            print(f"Running cron: {name} (from={args.updated_from} to={args.updated_to})")
            run_cron_by_name(name, args.updated_from, args.updated_to)


if __name__ == "__main__":
    main()
