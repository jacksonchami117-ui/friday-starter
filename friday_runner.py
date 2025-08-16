import os
import subprocess
from datetime import datetime

LOG_FILE = "state/log.txt"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def run_command(command):
    log(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        log("STDOUT:\n" + result.stdout)
    if result.stderr:
        log("STDERR:\n" + result.stderr)
    return result.returncode

def main():
    log("=== Friday Runner Started ===")

    # Example: test running Flask app
    log("Testing Flask app...")
    run_command("python app.py & sleep 5 && pkill -f app.py")

    # Commit + push changes
    log("Committing any changes...")
    run_command("git config --global user.name 'Friday AI'")
    run_command("git config --global user.email 'friday@example.com'")
    run_command("git add -A")
    run_command("git commit -m 'AUTO: Friday initial commit' || echo 'No changes to commit'")
    run_command("git push")

    log("=== Friday Runner Finished ===")

if __name__ == "__main__":
    os.makedirs("state", exist_ok=True)
    main()
