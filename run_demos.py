"""Run all four demos in order and report whether each behaved as designed.

Usage:  python run_demos.py
"""
import subprocess
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent / "app"
DEMOS = [
    "demo_1_permissions.py",
    "demo_2_sql_injection.py",
    "demo_3_audit_log.py",
    "demo_4_authentication.py",
]

if __name__ == "__main__":
    failed = []
    for demo in DEMOS:
        code = subprocess.run([sys.executable, demo], cwd=APP).returncode
        if code != 0:
            failed.append(demo)
    print("\n" + "=" * 72)
    if failed:
        print("Some demos did not behave as designed:", ", ".join(failed))
        sys.exit(1)
    print("All demos behaved as designed.")
