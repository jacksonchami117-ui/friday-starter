import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

class User(UserMixin):
    id = "admin"

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if not ADMIN_PASSWORD:
        return redirect(url_for("index"))  # auth disabled
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            login_user(User())
            return redirect(request.args.get('next') or url_for("index"))
        flash("Invalid password", "danger")
    return render_template("auth_login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
