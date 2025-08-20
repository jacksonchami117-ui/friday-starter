import os
import subprocess
from datetime import datetime

TASKS_FILE = "TASKS.md"
LOG_FILE = "state/log.txt"

def log(msg: str):
    os.makedirs("state", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} {msg}\n")
    print(msg)

def read_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE) as f:
        return [line.strip() for line in f if line.strip()]

def commit_and_push(msg="AUTO: runner commit"):
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", msg], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    log("Changes committed and pushed.")

def main():
    tasks = read_tasks()
    log("=== FRIDAY Runner Start ===")
    for t in tasks:
        log(f"TASK: {t}")
    commit_and_push()

if __name__ == "__main__":
    main()
