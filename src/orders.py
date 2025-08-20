
from flask import Blueprint

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

@orders_bp.route("/", methods=["GET"])
def orders_home():
    return "Orders module (placeholder)."
