from flask import Blueprint, render_template, abort, send_file, jsonify
import hashlib
import os
import csv
from .campaigns_routes import _progress_path

bp = Blueprint("landing", __name__, url_prefix="/s")

def get_video_data(token: str) -> dict:
    """Get video metadata from CSV exports"""
    exports_dir = os.path.join(os.environ.get("STATE_DIR", "./state"), "exports")
    
    for filename in os.listdir(exports_dir) if os.path.exists(exports_dir) else []:
        if not filename.endswith(".csv"):
            continue
            
        filepath = os.path.join(exports_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("share_token") == token:
                        return {
                            "name": row.get("name", "Video"),
                            "status": row.get("status", "unknown"),
                            "video_path": row.get("video_path"),
                            "thumbnail_path": row.get("thumbnail_path"),
                            "created_at": row.get("created_at"),
                            "duration": row.get("duration"),
                            "email": row.get("email", ""),
                            "campaign_id": row.get("campaign_id")
                        }
        except:
            continue
    
    return {}

@bp.route("/<token>")
def share(token: str):
    """Public video sharing page"""
    if not token or len(token) < 10:
        abort(404)
    
    video = get_video_data(token)
    if not video:
        abort(404)
    
    # Check if video file exists
    video_path = video.get("video_path")
    if video_path and os.path.exists(video_path):
        video_url = f"/s/{token}/video"
        thumbnail_url = f"/s/{token}/thumbnail"
    else:
        video_url = None
        thumbnail_url = None
    
    return render_template("landing/share.html",
                         video=video,
                         token=token,
                         video_url=video_url,
                         thumbnail_url=thumbnail_url)

@bp.route("/<token>/video")
def video(token: str):
    """Serve video file"""
    video = get_video_data(token)
    if not video:
        abort(404)
    
    video_path = video.get("video_path")
    if not video_path or not os.path.exists(video_path):
        abort(404)
    
    return send_file(video_path, mimetype="video/mp4", as_attachment=False)

@bp.route("/<token>/thumbnail")
def thumbnail(token: str):
    """Serve thumbnail file"""
    video = get_video_data(token)
    if not video:
        abort(404)
    
    thumb_path = video.get("thumbnail_path")
    if not thumb_path or not os.path.exists(thumb_path):
        # Fallback to generic thumbnail
        static_thumb = os.path.join("static", "images", "video-placeholder.jpg")
        if os.path.exists(static_thumb):
            return send_file(static_thumb)
        abort(404)
    
    return send_file(thumb_path, mimetype="image/jpeg")

@bp.route("/<token>/info")
def info(token: str):
    """API endpoint for video info"""
    video = get_video_data(token)
    if not video:
        abort(404)
    
    return jsonify({
        "name": video.get("name"),
        "status": video.get("status"),
        "duration": video.get("duration"),
        "created_at": video.get("created_at"),
        "has_video": bool(video.get("video_path") and os.path.exists(video.get("video_path", ""))),
        "has_thumbnail": bool(video.get("thumbnail_path") and os.path.exists(video.get("thumbnail_path", "")))
    })

def tok(email): return hashlib.sha1((email or "").encode()).hexdigest()[:16]
@bp.route("/v/<cid>/<token>")
def view(cid,token):
    p=_progress_path(cid)
    if not os.path.exists(p): abort(404)
    for r in csv.DictReader(open(p)):
        if tok(r.get("email",""))==token: return render_template("landing_view.html",r=r)
    abort(404)
