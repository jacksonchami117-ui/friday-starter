import os
import logging
from flask import Flask, render_template, send_from_directory

# Import blueprints
from src.leads import leads_bp
from src.orders import orders_bp
from src.render_routes import render_bp
from src.exports import exports_bp
from src.diagnostics_routes import diagnostics_bp
from src.editor import editor_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.getenv("DATA_DIR", os.path.join(base_dir, "state"))
    app.config["DATA_DIR"] = data_dir

    # Ensure runtime folders exist
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, "uploads"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "outputs", "videos"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "outputs", "thumbs"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "batches"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "assets"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "templates"), exist_ok=True)

    # Logging
    log_path = os.path.join(data_dir, "logs", "app.log")
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    app.logger = logging.getLogger(__name__)
    app.logger.info("=== FRIDAY System Startup ===")

    # Register blueprints
    app.register_blueprint(leads_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(render_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(diagnostics_bp)
    app.register_blueprint(editor_bp)

    # Routes
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return "OK", 200

    @app.route("/media/assets/<path:filename>")
    def media_assets(filename):
        return send_from_directory(os.path.join(data_dir, "assets"), filename)

    @app.route("/media/thumbs/<path:filename>")
    def media_thumbs(filename):
        return send_from_directory(os.path.join(data_dir, "outputs", "thumbs"), filename)

    return app


# ----------------------------------------------------
# Run locally (python app.py) OR expose for Gunicorn
# ----------------------------------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# Expose for Gunicorn (Render looks for app:app)
app = create_app()
