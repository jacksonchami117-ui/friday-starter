import os
import logging
from flask import Flask, render_template, send_from_directory, redirect, url_for, current_app
from werkzeug.exceptions import HTTPException

# Blueprints
from src.leads import leads_bp
from src.orders import orders_bp
from src.render_routes import render_bp
from src.exports import exports_bp
from src.diagnostics_routes import diagnostics_bp
from src.editor import editor_bp
from src.logs import logs_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.getenv("DATA_DIR", os.path.join(base_dir, "state"))
    app.config["DATA_DIR"] = data_dir

    # Ensure runtime dirs exist
    for p in [
        data_dir,
        os.path.join(data_dir, "uploads"),
        os.path.join(data_dir, "outputs", "videos"),
        os.path.join(data_dir, "outputs", "thumbs"),
        os.path.join(data_dir, "logs"),
        os.path.join(data_dir, "batches"),
        os.path.join(data_dir, "assets"),
        os.path.join(data_dir, "templates"),
    ]:
        os.makedirs(p, exist_ok=True)

    # Logging to file + console
    log_path = os.path.join(data_dir, "logs", "app.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
    )
    app.logger.info("=== FRIDAY System Startup ===")

    # Register blueprints
    app.register_blueprint(leads_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(render_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(diagnostics_bp)
    app.register_blueprint(editor_bp)
    app.register_blueprint(logs_bp)

    # Safety: global error handler
    @app.errorhandler(Exception)
    def _err(e):
        if isinstance(e, HTTPException):
            return e
        current_app.logger.exception("Unhandled exception")
        return render_template("500.html", message=str(e)), 500

    @app.errorhandler(404)
    def _404(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def _500(e):
        return render_template("500.html", message=str(e)), 500

    SAFE_MODE = os.getenv("SAFE_MODE", "0") == "1"

    @app.route("/")
    def boot():
        if SAFE_MODE:
            return "FRIDAY safe-mode: up. Visit /home or /health."
        try:
            return render_template("intro_boot.html")
        except Exception:
            current_app.logger.exception("intro_boot.html failed, falling back to /home")
            return redirect(url_for("index"))

    @app.route("/home")
    def index():
        try:
            return render_template("index.html")
        except Exception:
            current_app.logger.exception("index.html failed")
            return "Home failed to render (see logs).", 500

    @app.route("/skip-intro")
    def skip_intro():
        return redirect(url_for("index"))

    @app.route("/health")
    def health():
        return "OK", 200

    @app.route("/media/assets/<path:filename>")
    def media_assets(filename):
        return send_from_directory(os.path.join(data_dir, "assets"), filename)

    @app.route("/media/thumbs/<path:filename>")
    def media_thumbs(filename):
        return send_from_directory(os.path.join(data_dir, "outputs", "thumbs"), filename)

    # Debug helpers
    @app.route("/__debug/templates")
    def __debug_templates():
        rows = []
        tdir = os.path.join(base_dir, "templates")
        if not os.path.isdir(tdir):
            return "<pre>(no /templates)</pre>"
        for root, _, files in os.walk(tdir):
            for name in files:
                rows.append(os.path.relpath(os.path.join(root, name), tdir))
        rows.sort()
        return "<pre>" + "\n".join(rows) + "</pre>"

    @app.route("/__debug/static")
    def __debug_static():
        sdir = os.path.join(base_dir, "static")
        rows = []
        if not os.path.isdir(sdir):
            return "<pre>(no /static)</pre>"
        for root, _, files in os.walk(sdir):
            for name in files:
                rows.append(os.path.relpath(os.path.join(root, name), sdir))
        rows.sort()
        return "<pre>" + "\n".join(rows) + "</pre>"

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Expose for Gunicorn
app = create_app()
