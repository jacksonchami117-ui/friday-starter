# Main pipeline tests would go here
# ...existing code...

import glob, zipfile, shutil, datetime, os

def log(msg):
    print(msg)

# ---- Write summary.txt for test-data.zip ----
summary_lines = []

csv_files = glob.glob("state/*.csv")
manifest_files = glob.glob("state/templates/*.json")
video_files = glob.glob("state/outputs/videos/*.mp4")

if csv_files:
    summary_lines.append("CSVs:")
    for f in csv_files:
        summary_lines.append(f"  - {os.path.basename(f)}")
if manifest_files:
    summary_lines.append("Manifests:")
    for f in manifest_files:
        summary_lines.append(f"  - templates/{os.path.basename(f)}")
if video_files:
    summary_lines.append("Videos:")
    for f in video_files:
        summary_lines.append(f"  - videos/{os.path.basename(f)}")

summary_path = "state/summary.txt"
with open(summary_path, "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))

# ---- Zip CSVs, manifests, videos, + summary.txt ----
TEST_DATA_ZIP = "state/test-data.zip"
with zipfile.ZipFile(TEST_DATA_ZIP, "w") as zipf:
    for fpath in csv_files:
        zipf.write(fpath, arcname=os.path.basename(fpath))
    for fpath in manifest_files:
        zipf.write(fpath, arcname=f"templates/{os.path.basename(fpath)}")
    for fpath in video_files:
        zipf.write(fpath, arcname=f"videos/{os.path.basename(fpath)}")
    zipf.write(summary_path, arcname="summary.txt")
log(f"[ZIP] Test data archived at {TEST_DATA_ZIP}")

# ---- Zip logs and traces ----
LOGS_DIR = "state/logs"
LOGS_ZIP = os.path.join(LOGS_DIR, "logs.zip")
with zipfile.ZipFile(LOGS_ZIP, "w") as zipf:
    for fname in ["smoke_test.log", "http_trace.json"]:
        fpath = os.path.join(LOGS_DIR, fname)
        if os.path.exists(fpath):
            zipf.write(fpath, arcname=fname)
log(f"[ZIP] Logs archived at {LOGS_ZIP}")

# ---- Zip failed HTTP responses if any ----
FAILURES_DIR = "state/logs/http_failures"
if os.path.isdir(FAILURES_DIR) and os.listdir(FAILURES_DIR):
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    zip_path = f"{FAILURES_DIR}/failures_{ts}.zip"
    shutil.make_archive(zip_path.replace(".zip", ""), "zip", FAILURES_DIR)
    log(f"[ZIP] Failures archived at {zip_path}")
