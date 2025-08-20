import os
import logging
from flask import Flask, render_template, send_from_directory, redirect, url_for, current_app

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
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.getenv("DATA_DIR", os.path.join(base_dir, "state"))
    app.config["DATA_DIR"] = data_dir

    # Ensure runtime folders exist
    for p in [
        data_dir,
        os.path.join(data_dir, "uploads"),
        os.path.join(data_dir, "outputs", "videos"),
        os.path.join(data_dir, "outputs", "thumbs"),
        os.path.join(data_dir, "logs"),
        os.path.join(data_dir, "batches"),
        os.path.join(data_dir, "assets"),
    ]:
        os.makedirs(p, exist_ok=True)

    # Logging (console + file)
    log_path = os.path.join(data_dir, "logs", "app.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()]
    )
    app.logger.info("=== FRIDAY System Startup ===")

    # Register blueprints
    app.register_blueprint(leads_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(render_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(diagnostics_bp)
    app.register_blueprint(editor_bp)

    # Routes
    @app.route("/")  # New Render-style intro
    def boot():
        try:
            return render_template("intro_boot.html")
        except Exception as e:
            current_app.logger.exception("Intro failed, falling back to /home")
            return redirect(url_for("index"))

    @app.route("/home")
    def index():
        return render_template("index.html")

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

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Expose for Gunicorn (Render looks for app:app)
app = create_app()
