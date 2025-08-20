import os, json, shutil
from datetime import datetime
from pathlib import Path
from typing import Dict
from .utils import slugify, run_cmd

# Map messy names -> clean names
COLUMN_MAP = {
    "first name": "First",
    "firstname": "First",
    "last name": "Last",
    "lastname": "Last",
    "phone number": "Phone",
    "phone": "Phone",
    "email": "Email",
    "website": "Website",
}

def normalize(row: dict) -> dict:
    fixed = {}
    for k,v in row.items():
        key = k.strip().lower()
        fixed[COLUMN_MAP.get(key, k.strip())] = v
    return fixed

def ensure_ffmpeg(): return "ffmpeg"
def _run(cmd): run_cmd(cmd)

def render_one_lead(lead: Dict, data_dir: str):
    lead = normalize(lead)   # <-- important fix

    ff = ensure_ffmpeg()
    assets_dir = os.path.join(data_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Output folders
    out_videos = os.path.join(data_dir, "outputs", "videos")
    out_thumbs = os.path.join(data_dir, "outputs", "thumbs")
    os.makedirs(out_videos, exist_ok=True)
    os.makedirs(out_thumbs, exist_ok=True)

    safe_name = slugify(f"{lead.get('First','')}-{lead.get('Last','')}-{lead.get('index',0)}")
    tmp_dir = os.path.join(data_dir, "tmp", safe_name)
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)

    # make fake video file (for demo)
    final_path = os.path.join(out_videos, f"vid_{safe_name}.mp4")
    _run(f"{ff} -y -f lavfi -i color=blue:s=640x360:d=1 -vf drawtext=text='Video for {lead.get('First','')}' -c:v libx264 {final_path}")

    # make thumbnail
    thumb_path = os.path.join(out_thumbs, f"thumb_{safe_name}.png")
    _run(f"{ff} -y -f lavfi -i color=blue:s=640x360:d=1 -vframes 1 {thumb_path}")

    # log progress
    progress_csv = os.path.join(data_dir, "render_progress.csv")
    now = datetime.utcnow().isoformat()
    line = f"{lead.get('index',0)},{lead.get('First','')},{lead.get('Last','')},{os.path.basename(final_path)},{os.path.basename(thumb_path)},{now},Success\n"
    with open(progress_csv, "a") as f:
        if f.tell() == 0:
            f.write("index,First,Last,video,thumbnail,timestamp,status\n")
        f.write(line)

    shutil.rmtree(tmp_dir, ignore_errors=True)
    return final_path, thumb_path
