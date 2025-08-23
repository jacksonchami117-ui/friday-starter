import sys
import os

# Preflight checks for FRIDAY deployment
# This script should be run before Gunicorn starts

def check_python_version():
    if sys.version_info < (3, 11):
        print(f"ERROR: Python 3.11+ required, found {sys.version}")
        sys.exit(1)

def check_env_vars():
    required = ["SECRET_KEY"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        print(f"ERROR: Missing required env vars: {missing}")
        sys.exit(1)

def main():
    check_python_version()
    check_env_vars()
    print("Preflight checks passed.")

if __name__ == "__main__":
    main()
