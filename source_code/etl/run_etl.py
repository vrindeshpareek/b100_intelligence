import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = {
    1: "etl/01_extract_from_mysql.py",
    2: "etl/02_clean_and_transform.py",
    3: "etl/03_load_to_warehouse.py",
    4: "etl/04_ml_scoring.py",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--steps", nargs="+", type=int, choices=STEPS.keys(), default=[1, 2, 3, 4]
    )
    parser.add_argument(
        "--drop", action="store_true", help="Drop warehouse tables before step 3"
    )
    args = parser.parse_args()

    for step in args.steps:
        cmd = [sys.executable, str(ROOT / STEPS[step])]
        if step == 3 and args.drop:
            cmd.append("--drop-first")
        print(f"\nRunning step {step}: {STEPS[step]}")
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode:
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
