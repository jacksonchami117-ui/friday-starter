import os
import subprocess
from datetime import datetime

TASKS_FILE = "TASKS.md"
LOG_FILE = "state/log.txt"

def log(message: str):
    """Write to log file and print to console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs("state", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def run_command(command: str):
    """Run a shell command and log output"""
    log(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        log("STDOUT:\n" + result.stdout)
    if result.stderr:
        log("STDERR:\n" + result.stderr)
    return result.returncode

def read_tasks():
    """Read tasks from TASKS.md"""
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        lines = [line.strip("- ").strip() for line in f.readlines() if line.strip()]
    return lines

def apply_task(task: str):
    """Naive interpreter: handle basic tasks like creating pages"""
    log(f"Applying task: {task}")

    # Example: Add an About page
    if "About page" in task:
        with open("app.py", "a") as f:
            f.write(
                "\n@app.route('/about')\n"
                "def about():\n"
                "    return render_template('about.html')\n"
            )
        os.makedirs("templates", exist_ok=True)
        with open("templates/about.html", "w") as f:
            f.write(
                "<!DOCTYPE html>\n"
                "<html><head><title>About</title></head><body>\n"
                "<h1>About Friday</h1>\n"
                "<p>This is Friday, an autonomous AI agent that edits, commits, and deploys code.</p>\n"
                "</body></html>\n"
            )
        log("Added /about page")

    # Example: Add a Contact page
    if "Contact page" in task:
        with open("app.py", "a") as f:
            f.write(
                "\n@app.route('/contact')\n"
                "def contact():\n"
                "    return render_template('contact.html')\n"
            )
        os.makedirs("templates", exist_ok=True)
        with open("templates/contact.html", "w") as f:
            f.write(
                "<!DOCTYPE html>\n"
                "<html><head><title>Contact</title></head><body>\n"
                "<h1>Contact Us</h1>\n"
                "<form>\n"
                "  Name: <input type='text' name='name'><br>\n"
                "  Email: <input type='email' name='email'><br>\n"
                "  <button type='submit'>Send</button>\n"
                "</form>\n"
                "</body></html>\n"
            )
        log("Added /contact page")

def main():
    log("=== Friday Runner Started ===")
    tasks = read_tasks()
    if not tasks:
        log("No tasks found.")
    else:
        for task in tasks:
            apply_task(task)

    # Commit + push
    run_command("git config --global user.name 'Friday AI'")
    run_command("git config --global user.email 'friday@example.com'")
    run_command("git add -A")
    run_command("git commit -m 'AUTO: Friday applied tasks' || echo 'No changes to commit'")
    run_command("git push")

    log("=== Friday Runner Finished ===")

if __name__ == "__main__":
    main()
