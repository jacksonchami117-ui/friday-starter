from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import os

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

def require_admin():
    if session.get("is_admin"):
        return
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["is_admin"] = True
            return
    flash("Admin login required", "error")
    return redirect(url_for("admin.login"))

@bp_admin.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin.users"))
        else:
            flash("Incorrect password", "error")
    return render_template("admin_login.html")

@bp_admin.route("/users")
def users():
    require_admin()
    users = [{"id": 1, "email": "user1@example.com", "active": True}, {"id": 2, "email": "user2@example.com", "active": False}]
    return render_template("admin_users.html", users=users)

@bp_admin.route("/jobs")
def jobs():
    require_admin()
    jobs = [{"id": 101, "template": "t1", "status": "completed"}, {"id": 102, "template": "t2", "status": "pending"}]
    return render_template("admin_jobs.html", jobs=jobs)

@bp_admin.route("/leads")
def leads():
    require_admin()
    leads = [{"id": 201, "name": "Lead1", "email": "a@a.com", "status": "accepted"}, {"id": 202, "name": "Lead2", "email": "b@b.com", "status": "rejected"}]
    return render_template("admin_leads.html", leads=leads)