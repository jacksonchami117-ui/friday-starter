import os
import csv
import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def _data_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.getenv("DATA_DIR", os.path.join(base, "state"))

def _paths():
    d = _data_dir()
    return {
        "accepted": os.path.join(d, "accepted_leads.csv"),
        "rejected": os.path.join(d, "rejected_leads.csv"),
        "jobs": os.path.join(d, "jobs.json"),
        "users": os.path.join(d, "users.json"),
        "logs": os.path.join(d, "logs"),
    }

# Mock user data - in a real system, this would come from a database
def get_mock_users():
    return [
        {"id": 1, "username": "admin", "email": "admin@friday.com", "role": "admin", "status": "active", "created": "2024-01-01"},
        {"id": 2, "username": "user1", "email": "user1@friday.com", "role": "user", "status": "active", "created": "2024-01-15"},
        {"id": 3, "username": "user2", "email": "user2@friday.com", "role": "user", "status": "inactive", "created": "2024-02-01"},
    ]

# Mock job data - in a real system, this would come from a database  
def get_mock_jobs():
    return [
        {"id": 1, "type": "video_generation", "status": "running", "progress": 75, "created": "2024-01-20 10:30:00", "lead_count": 150},
        {"id": 2, "type": "lead_processing", "status": "completed", "progress": 100, "created": "2024-01-19 14:20:00", "lead_count": 200},
        {"id": 3, "type": "export_data", "status": "failed", "progress": 0, "created": "2024-01-18 09:15:00", "lead_count": 0},
        {"id": 4, "type": "video_generation", "status": "queued", "progress": 0, "created": "2024-01-21 16:45:00", "lead_count": 85},
    ]

@admin_bp.route("/")
def admin_dashboard():
    """Admin dashboard with overview stats"""
    try:
        users = get_mock_users()
        jobs = get_mock_jobs()
        
        # Calculate stats
        stats = {
            "total_users": len(users),
            "active_users": len([u for u in users if u["status"] == "active"]),
            "total_jobs": len(jobs),
            "running_jobs": len([j for j in jobs if j["status"] == "running"]),
            "failed_jobs": len([j for j in jobs if j["status"] == "failed"]),
        }
        
        # Get lead stats
        paths = _paths()
        lead_stats = {"accepted": 0, "rejected": 0}
        
        if os.path.exists(paths["accepted"]):
            try:
                with open(paths["accepted"], newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    lead_stats["accepted"] = len(list(reader))
            except Exception:
                pass
                
        if os.path.exists(paths["rejected"]):
            try:
                with open(paths["rejected"], newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    lead_stats["rejected"] = len(list(reader))
            except Exception:
                pass
        
        return render_template("admin/dashboard.html", stats=stats, lead_stats=lead_stats)
    except Exception as e:
        current_app.logger.exception("Admin dashboard failed")
        flash(f"Dashboard error: {str(e)}", "danger")
        return redirect(url_for("index"))

@admin_bp.route("/users")
def admin_users():
    """User management interface"""
    try:
        users = get_mock_users()
        return render_template("admin/users.html", users=users)
    except Exception as e:
        current_app.logger.exception("Admin users failed")
        flash(f"Users page error: {str(e)}", "danger")
        return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
def toggle_user_status(user_id):
    """Toggle user active/inactive status"""
    try:
        users = get_mock_users()
        user = next((u for u in users if u["id"] == user_id), None)
        
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        # Mock toggle
        new_status = "inactive" if user["status"] == "active" else "active"
        user["status"] = new_status
        
        return jsonify({
            "status": "success", 
            "message": f"User {user['username']} is now {new_status}",
            "new_status": new_status
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@admin_bp.route("/jobs")
def admin_jobs():
    """Job monitoring interface"""
    try:
        jobs = get_mock_jobs()
        return render_template("admin/jobs.html", jobs=jobs)
    except Exception as e:
        current_app.logger.exception("Admin jobs failed")
        flash(f"Jobs page error: {str(e)}", "danger")
        return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/jobs/<int:job_id>/cancel", methods=["POST"])
def cancel_job(job_id):
    """Cancel a running job"""
    try:
        jobs = get_mock_jobs()
        job = next((j for j in jobs if j["id"] == job_id), None)
        
        if not job:
            return jsonify({"status": "error", "message": "Job not found"}), 404
        
        if job["status"] not in ["running", "queued"]:
            return jsonify({"status": "error", "message": "Job cannot be cancelled"}), 400
        
        # Mock cancellation
        job["status"] = "cancelled"
        job["progress"] = 0
        
        return jsonify({
            "status": "success",
            "message": f"Job {job_id} cancelled",
            "new_status": "cancelled"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@admin_bp.route("/jobs/<int:job_id>/restart", methods=["POST"])
def restart_job(job_id):
    """Restart a failed job"""
    try:
        jobs = get_mock_jobs()
        job = next((j for j in jobs if j["id"] == job_id), None)
        
        if not job:
            return jsonify({"status": "error", "message": "Job not found"}), 404
        
        if job["status"] != "failed":
            return jsonify({"status": "error", "message": "Only failed jobs can be restarted"}), 400
        
        # Mock restart
        job["status"] = "queued"
        job["progress"] = 0
        
        return jsonify({
            "status": "success",
            "message": f"Job {job_id} restarted",
            "new_status": "queued"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@admin_bp.route("/leads")
def admin_leads():
    """Lead oversight interface"""
    try:
        paths = _paths()
        
        accepted_leads = []
        rejected_leads = []
        
        # Load accepted leads
        if os.path.exists(paths["accepted"]):
            try:
                with open(paths["accepted"], newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    accepted_leads = list(reader)
            except Exception as e:
                current_app.logger.warning(f"Could not read accepted leads: {e}")
        
        # Load rejected leads
        if os.path.exists(paths["rejected"]):
            try:
                with open(paths["rejected"], newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rejected_leads = list(reader)
            except Exception as e:
                current_app.logger.warning(f"Could not read rejected leads: {e}")
        
        # Get filter parameters
        status_filter = request.args.get("status", "all")
        search_query = request.args.get("search", "").strip().lower()
        
        # Apply filters
        all_leads = []
        
        for lead in accepted_leads:
            lead["status"] = "accepted"
            all_leads.append(lead)
        
        for lead in rejected_leads:
            lead["status"] = "rejected"
            all_leads.append(lead)
        
        # Filter by status
        if status_filter != "all":
            all_leads = [l for l in all_leads if l["status"] == status_filter]
        
        # Filter by search
        if search_query:
            filtered_leads = []
            for lead in all_leads:
                # Search in email, name fields
                searchable_text = ""
                for key, value in lead.items():
                    searchable_text += str(value).lower() + " "
                
                if search_query in searchable_text:
                    filtered_leads.append(lead)
            all_leads = filtered_leads
        
        return render_template("admin/leads.html", 
                             leads=all_leads, 
                             total_accepted=len(accepted_leads),
                             total_rejected=len(rejected_leads),
                             status_filter=status_filter,
                             search_query=request.args.get("search", ""))
                             
    except Exception as e:
        current_app.logger.exception("Admin leads failed")
        flash(f"Leads page error: {str(e)}", "danger")
        return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/leads/reprocess", methods=["POST"])
def reprocess_leads():
    """Bulk reprocess rejected leads"""
    try:
        # This would implement actual reprocessing logic
        # For now, just return success
        return jsonify({
            "status": "success",
            "message": "Lead reprocessing initiated. Check jobs page for progress."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@admin_bp.route("/leads/export", methods=["POST"])
def export_leads():
    """Export leads data"""
    try:
        export_type = request.json.get("type", "all")
        
        # This would implement actual export logic
        # For now, just return success
        return jsonify({
            "status": "success",
            "message": f"Export of {export_type} leads initiated. Download will be available shortly.",
            "download_url": "/admin/leads/download/latest.csv"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500