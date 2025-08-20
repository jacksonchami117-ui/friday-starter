from flask import Blueprint, render_template

render_bp = Blueprint("render", __name__, url_prefix="/render")

@render_bp.route("/", methods=["GET"])
def render_home():
    return render_template("render.html")
