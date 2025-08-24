import os
import logging
from logging.handlers import RotatingFileHandler

import click
from flask import Flask, render_template, send_from_directory, current_app
from flask.cli import with_appcontext
import werkzeug
import importlib.metadata

# Provide backwards-compatible werkzeug.__version__ for Flask test_client
if not hasattr(werkzeug, "__version__"):
    try:
        werkzeug.__version__ = importlib.metadata.version("werkzeug")
    except importlib.metadata.PackageNotFoundError:  # pragma: no cover
        werkzeug.__version__ = "0"

from src.leads import leads_bp
from src.orders import orders_bp
from src.render_routes import render_bp
from src.exports import exports_bp
from src.diagnostics_routes import diagnostics_bp
from src.editor import editor_bp
from src.campaigns_routes import bp as campaigns_bp
from src.settings_routes import bp as settings_bp

# -------------------------------------------------
# Central Logging
# -------------------------------------------------
LOG_DIR = os.environ.get("LOG_DIR", "./logs")
os.makedirs(LOG_DIR, exist_ok=True)

file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "friday.log"),
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

# -------------------------------------------------
# CLI Diagnostics
# -------------------------------------------------
@click.command("diagnostics-selftest")
@with_appcontext
def diagnostics_selftest():
    client = current_app.test_client()
    endpoints = ["/health", "/", "/leads", "/editor", "/render", "/exports", "/diagnostics"]
    failures = []
    for ep in endpoints:
        resp = client.get(ep)
        if resp.status_code not in (200, 302):
            failures.append((ep, resp.status_code))
    if failures:
        raise SystemExit(f"❌ Failures: {failures}")
    print("✅ Diagnostics self-test passed")

def register_cli(app):
    app.cli.add_command(diagnostics_selftest)

# -------------------------------------------------
# App Factory
# -------------------------------------------------
def create_app():
    # Explicitly fetch os from global scope
    _os = __import__("os")

    app = Flask(__name__)
    app.secret_key = _os.getenv("SECRET_KEY", "dev-secret-key")

    if not app.logger.handlers:
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    # Optional Sentry
    if _os.environ.get("SENTRY_DSN"):
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        sentry_sdk.init(
            dsn=_os.environ["SENTRY_DSN"],
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
        )
        app.logger.info("Sentry initialized")

    # Ensure state dirs
    base_dir = _os.path.dirname(_os.path.abspath(__file__))
    data_dir = _os.getenv("DATA_DIR", _os.path.join(base_dir, "state"))
    app.config["DATA_DIR"] = data_dir
    for path in ["uploads", "outputs/videos", "outputs/thumbs", "logs", "batches", "assets", "templates"]:
        _os.makedirs(_os.path.join(data_dir, path), exist_ok=True)

    # Blueprints
    app.register_blueprint(leads_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(render_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(diagnostics_bp)
    app.register_blueprint(editor_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(settings_bp)

    # CLI
    register_cli(app)

    # Routes
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return "ok", 200

    @app.route("/media/assets/<path:filename>")
    def media_assets(filename):
        return send_from_directory(_os.path.join(data_dir, "assets"), filename)

    @app.route("/media/thumbs/<path:filename>")
    def media_thumbs(filename):
        return send_from_directory(_os.path.join(data_dir, "outputs", "thumbs"), filename)

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
