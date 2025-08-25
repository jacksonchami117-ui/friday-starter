from __future__ import annotations
import os, json, csv, io, time, uuid, datetime as dt
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file, current_app

bp = Blueprint("campaigns", __name__, url_prefix="/campaigns")

def _state_dir() -> str:
    base = os.environ.get("STATE_DIR", "./state")
    os.makedirs(base, exist_ok=True)
    return base

def _campaigns_index_path() -> str:
    p = os.path.join(_state_dir(), "campaigns", "index.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8", newline="") as f:
            json.dump({"campaigns": []}, f)
    return p

def _load_index() -> Dict[str, Any]:
    with open(_campaigns_index_path(), "r", encoding="utf-8") as f:
        return json.load(f)

def _save_index(data: Dict[str, Any]) -> None:
    with open(_campaigns_index_path(), "w", encoding="utf-8", newline="") as f:
        json.dump(data, f, indent=2)

def _camp_dir(cid: str) -> str:
    p = os.path.join(_state_dir(), "campaigns", cid)
    os.makedirs(p, exist_ok=True)
    return p

def _meta_path(cid: str) -> str:
    return os.path.join(_camp_dir(cid), "meta.json")

def _leads_csv_path(cid: str) -> str:
    return os.path.join(_camp_dir(cid), "leads.csv")

def _issues_csv_path(cid: str) -> str:
    return os.path.join(_camp_dir(cid), "issues.csv")

def _manifest_path(cid: str) -> str:
    return os.path.join(_camp_dir(cid), "manifest.json")

def _progress_path(cid: str) -> str:
    # rolling progress log for analytics/export
    return os.path.join(_camp_dir(cid), "render_progress.csv")

def _thumbs_dir() -> str:
    p = os.path.join(_state_dir(), "outputs", "thumbs")
    os.makedirs(p, exist_ok=True)
    return p

DEFAULT_STEPS = [
    "Create Video Script","Record Template Video","Import Leads","Customize Landing Page",
    "Review Test Video","Generate Videos","Custom Domain","Export Videos","Send Videos",
    "Engage with Leads","Analytics","Add More Leads"
]

def _init_meta(cid: str, name: str) -> Dict[str, Any]:
    now = dt.datetime.utcnow().isoformat()
    meta = {
        "id": cid,
        "name": name,
        "created_at": now,
        "updated_at": now,
        "steps": {s: "Not started" for s in DEFAULT_STEPS},
        "counts": {"queued":0,"processing":0,"rendered":0,"failed":0,"invalid":0,"blocked":0,"temp":0},
        "lead_count": 0
    }
    with open(_meta_path(cid), "w", encoding="utf-8", newline="") as f:
        json.dump(meta, f, indent=2)
    return meta

def _load_meta(cid: str) -> Dict[str, Any]:
    p = _meta_path(cid)
    if not os.path.exists(p):
        return _init_meta(cid, "New Campaign")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_meta(cid: str, meta: Dict[str, Any]) -> None:
    meta["updated_at"] = dt.datetime.utcnow().isoformat()
    with open(_meta_path(cid), "w", encoding="utf-8", newline="") as f:
        json.dump(meta, f, indent=2)

@bp.route("/", methods=["GET"])
def campaigns_home():
    idx = _load_index()
    cards = []
    for c in idx.get("campaigns", []):
        meta = _load_meta(c["id"])
        total = meta.get("lead_count",0) or 0
        rendered = meta.get("counts",{}).get("rendered",0) or 0
        pct = 0
        if total > 0:
            pct = int(round((rendered*100.0)/total))
        cards.append({
            "id": c["id"],
            "name": meta.get("name", c.get("name","Campaign")),
            "lead_count": total,
            "rendered": rendered,
            "progress_pct": pct,
            "thumb": _find_any_thumb()
        })
    return render_template("campaigns.html", cards=cards)

def _find_any_thumb():
    td = _thumbs_dir()
    if not os.path.exists(td):
        return None
    for f in os.listdir(td):
        if f.lower().endswith((".jpg",".png",".jpeg",".webp")):
            return "/media/thumbs/" + f
    return None

@bp.route("/create", methods=["POST"])
def create_campaign():
    name = request.form.get("name","Untitled Campaign").strip() or "Untitled Campaign"
    cid = uuid.uuid4().hex[:8]
    idx = _load_index()
    idx["campaigns"].append({"id": cid, "name": name})
    _save_index(idx)
    _init_meta(cid, name)
    return redirect(url_for("campaigns.campaign_detail", cid=cid))

@bp.route("/<cid>", methods=["GET"])
def campaign_detail(cid: str):
    meta = _load_meta(cid)
    return render_template("campaign_detail.html", meta=meta, steps=DEFAULT_STEPS)

# ---------- Import: CSV with DnD ----------
@bp.route("/<cid>/import", methods=["GET"])
def import_page(cid: str):
    meta = _load_meta(cid)
    return render_template("campaign_import.html", meta=meta)

REQUIRED_FIELDS = ["business","first","last","email","website"]

@bp.route("/<cid>/import/csv", methods=["POST"])
def import_csv(cid: str):
    file = request.files.get("file")
    if not file:
        return jsonify({"ok": False, "error": "No file provided"}), 400
    # Read CSV
    text = file.read().decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    # basic validation
    issues = []
    cleaned = []
    for i, r in enumerate(rows, start=2):  # +1 header, +1 1-based
        item = {k.lower().strip(): (r.get(k) or "").strip() for k in r.keys()}
        # normalize names
        item["business"] = item.get("business") or item.get("company") or ""
        item["first"] = item.get("first") or item.get("first_name") or ""
        item["last"] = item.get("last") or item.get("last_name") or ""
        item["email"] = item.get("email") or ""
        item["website"] = item.get("website") or item.get("url") or ""
        missing = [f for f in REQUIRED_FIELDS if not item.get(f)]
        if missing:
            issues.append({"row": i, "reason": f"Missing fields: {', '.join(missing)}"})
        cleaned.append(item)

    # write outputs
    os.makedirs(os.path.dirname(_leads_csv_path(cid)), exist_ok=True)
    with open(_leads_csv_path(cid), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=REQUIRED_FIELDS)
        w.writeheader()
        for it in cleaned:
            w.writerow({k: it.get(k,"") for k in REQUIRED_FIELDS})

    with open(_issues_csv_path(cid), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["row","reason"])
        w.writeheader()
        for it in issues:
            w.writerow(it)

    meta = _load_meta(cid)
    meta["lead_count"] = len(cleaned)
    meta["steps"]["Import Leads"] = "Done" if not issues else "Needs attention"
    _save_meta(cid, meta)

    return jsonify({
        "ok": True,
        "total": len(cleaned),
        "issues": len(issues),
        "issues_csv": url_for("campaigns.download_issues_csv", cid=cid)
    })

@bp.route("/<cid>/issues.csv", methods=["GET"])
def download_issues_csv(cid: str):
    p = _issues_csv_path(cid)
    if not os.path.exists(p):
        return jsonify({"ok": False, "error": "No issues found"}), 404
    return send_file(p, as_attachment=True, download_name="issues.csv")

# ---------- Manifest save from Editor ----------
@bp.route("/<cid>/manifest", methods=["POST"])
def save_manifest(cid: str):
    data = request.get_json(force=True, silent=True) or {}
    with open(_manifest_path(cid), "w", encoding="utf-8", newline="") as f:
        json.dump(data, f, indent=2)
    meta = _load_meta(cid)
    meta["steps"]["Create Video Script"] = meta["steps"].get("Create Video Script","Done")
    meta["steps"]["Record Template Video"] = meta["steps"].get("Record Template Video","Done")
    _save_meta(cid, meta)
    return jsonify({"ok": True})

# ---------- Review / Generate / Analytics / Export pages ----------
@bp.route("/<cid>/review", methods=["GET"])
def review_page(cid: str):
    meta = _load_meta(cid)
    return render_template("campaign_review.html", meta=meta)

@bp.route("/<cid>/generate", methods=["GET"])
def generate_page(cid: str):
    meta = _load_meta(cid)
    return render_template("campaign_generate.html", meta=meta)

@bp.route("/<cid>/analytics", methods=["GET"])
def analytics_page(cid: str):
    meta = _load_meta(cid)
    # the page will poll /metrics and also read a rolling progress CSV if present
    return render_template("campaign_analytics.html", meta=meta)

@bp.route("/<cid>/export", methods=["GET"])
def export_page(cid: str):
    meta = _load_meta(cid)
    return render_template("campaign_export.html", meta=meta)

# ---------- JSON helpers for analytics/export ----------
@bp.route("/<cid>/progress.csv", methods=["GET"])
def download_progress(cid: str):
    """
    Expected columns (enhanced with share_token):
    business,first,last,email,website,phone,date,status,reason,video,thumb,share_token,share_url
    """
    p = _progress_path(cid)
    base_url = request.url_root.rstrip('/')
    
    if not os.path.exists(p):
        sio = io.StringIO()
        w = csv.writer(sio)
        w.writerow(["business","first","last","email","website","phone","date","status","reason","video","thumb","share_token","share_url"])
        return send_file(io.BytesIO(sio.getvalue().encode("utf-8")), as_attachment=True, download_name="render_progress.csv", mimetype="text/csv")
    
    # Read existing CSV and enhance with share URLs
    with open(p, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Enhanced header with share functionality
    enhanced_header = ["business","first","last","email","website","phone","date","status","reason","video","thumb","share_token","share_url"]
    
    sio = io.StringIO()
    w = csv.writer(sio)
    w.writerow(enhanced_header)
    
    for row in rows:
        # Generate share token based on email + video path
        email = row.get("email", "")
        video_path = row.get("video", "")
        
        share_token = ""
        share_url = ""
        
        if email and video_path and row.get("status") == "completed":
            # Generate deterministic token from email + video path
            import hashlib
            token_data = f"{email}_{video_path}_{cid}".encode('utf-8')
            share_token = hashlib.sha256(token_data).hexdigest()[:16]
            share_url = f"{base_url}/s/{share_token}"
        
        # Write enhanced row
        enhanced_row = []
        for col in enhanced_header:
            if col == "share_token":
                enhanced_row.append(share_token)
            elif col == "share_url":
                enhanced_row.append(share_url)
            else:
                enhanced_row.append(row.get(col, ""))
        
        w.writerow(enhanced_row)
    
    # Save enhanced CSV to exports directory for landing page lookup
    exports_dir = os.path.join(_state_dir(), "exports")
    os.makedirs(exports_dir, exist_ok=True)
    export_filename = f"campaign_{cid}_export_{int(time.time())}.csv"
    export_path = os.path.join(exports_dir, export_filename)
    
    with open(export_path, "w", newline="", encoding="utf-8") as f:
        f.write(sio.getvalue())
    
    return send_file(io.BytesIO(sio.getvalue().encode("utf-8")), as_attachment=True, download_name="render_progress.csv", mimetype="text/csv")

# ===== Editor + Assets (Append) =====
import subprocess, shlex
from flask import send_from_directory

def _assets_dir(cid: str) -> str:
    p = os.path.join(_camp_dir(cid), "assets")
    os.makedirs(p, exist_ok=True)
    return p

def _assets_thumbs_dir(cid: str) -> str:
    p = os.path.join(_assets_dir(cid), "thumbs")
    os.makedirs(p, exist_ok=True)
    return p

def _gen_thumb_asset(cid: str, filepath: str) -> str | None:
    # Generate a small jpg using ffmpeg; fallback to None if not available.
    try:
        out = os.path.join(_assets_thumbs_dir(cid), os.path.basename(filepath) + ".jpg")
        cmd = f"ffmpeg -y -ss 00:00:01 -i {shlex.quote(filepath)} -frames:v 1 -vf scale=320:-1 {shlex.quote(out)}"
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        return out if os.path.exists(out) else None
    except Exception:
        return None

# override earlier helper to return a proper url
def _find_any_thumb():
    td = _thumbs_dir()
    for f in os.listdir(td):
        fl = f.lower()
        if fl.endswith((".jpg",".png",".jpeg",".webp")):
            return url_for("campaigns.thumb", filename=f)
    return None

@bp.route("/thumbs/<filename>")
def thumb(filename: str):
    return send_from_directory(_thumbs_dir(), filename)

# -------- Editor pages & manifest --------
@bp.route("/<cid>/editor", methods=["GET"])
def editor_page(cid: str):
    meta = _load_meta(cid)
    # ensure manifest exists
    if not os.path.exists(_manifest_path(cid)):
        with open(_manifest_path(cid), "w", encoding="utf-8", newline="") as f:
            json.dump({"segments": [], "overlays": []}, f)
    return render_template("campaign_editor.html", meta=meta)

@bp.route("/<cid>/manifest", methods=["GET"])
def get_manifest(cid: str):
    p = _manifest_path(cid)
    if not os.path.exists(p):
        return jsonify({"segments": [], "overlays": []})
    with open(p, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

# assets API
ALLOWED_EXT = {".mp4",".mov",".m4v",".webm",".png",".jpg",".jpeg",".gif"}

@bp.route("/<cid>/assets", methods=["GET"])
def list_assets(cid: str):
    base = _assets_dir(cid)
    items = []
    for fn in sorted(os.listdir(base)):
        if fn == "thumbs": 
            continue
        ext = os.path.splitext(fn.lower())[1]
        if ext in ALLOWED_EXT:
            items.append({
                "name": fn,
                "url": url_for("campaigns.asset_file", cid=cid, filename=fn),
                "thumb": url_for("campaigns.asset_thumb", cid=cid, filename=fn+".jpg") if os.path.exists(os.path.join(_assets_thumbs_dir(cid), fn+".jpg")) else None,
                "type": "image" if ext in {".png",".jpg",".jpeg",".gif"} else "video"
            })
    return jsonify({"ok": True, "items": items})

@bp.route("/<cid>/assets/upload", methods=["POST"])
def upload_asset(cid: str):
    f = request.files.get("file")
    if not f:
        return jsonify({"ok": False, "error": "No file provided"}), 400
    name = f.filename
    ext = os.path.splitext(name.lower())[1]
    if ext not in ALLOWED_EXT:
        return jsonify({"ok": False, "error": f"Unsupported file type: {ext}"}), 400
    path = os.path.join(_assets_dir(cid), name)
    f.save(path)
    thumb = _gen_thumb_asset(cid, path)
    return jsonify({
        "ok": True,
        "item": {
            "name": name,
            "url": url_for("campaigns.asset_file", cid=cid, filename=name),
            "thumb": url_for("campaigns.asset_thumb", cid=cid, filename=name+".jpg") if thumb else None,
            "type": "image" if ext in {".png",".jpg",".jpeg",".gif"} else "video"
        }
    })

@bp.route("/<cid>/assets/file/<path:filename>")
def asset_file(cid: str, filename: str):
    return send_from_directory(_assets_dir(cid), filename, as_attachment=False)

@bp.route("/<cid>/assets/thumbs/<path:filename>")
def asset_thumb(cid: str, filename: str):
    return send_from_directory(_assets_thumbs_dir(cid), filename, as_attachment=False)
