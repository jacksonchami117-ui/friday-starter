from flask import Blueprint, render_template

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

@orders_bp.route("/", methods=["GET"])
def orders_home():
    return render_template("orders.html")
