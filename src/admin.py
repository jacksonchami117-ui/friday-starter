from flask import Blueprint, render_template

bp_admin = Blueprint("admin", __name__, url_prefix="/admin")

@bp_admin.route("/users")
def users():
    users = [
        {"id": 1, "name": "admin", "status": "active"},
        {"id": 2, "name": "demo", "status": "disabled"},
    ]
    return render_template("admin_users.html", users=users)

@bp_admin.route("/jobs")
def jobs():
    jobs = [
        {"id": 101, "status": "queued"},
        {"id": 102, "status": "done"},
    ]
    return render_template("admin_jobs.html", jobs=jobs)

@bp_admin.route("/leads")
def leads():
    leads = [
        {"id": 1, "email": "demo@example.com", "status": "accepted"},
        {"id": 2, "email": "bad@example.com", "status": "rejected"},
    ]
    return render_template("admin_leads.html", leads=leads)