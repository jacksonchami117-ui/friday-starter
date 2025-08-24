import os
import time
import logging
from logging.handlers import RotatingFileHandler

import click
import werkzeug
import importlib.metadata

from flask import Flask, render_template, send_from_directory, jsonify, current_app
from flask.cli import with_appcontext
from flask_login import LoginManager, login_required
from werkzeug.exceptions import HTTPException

# Provide backwards-compatible werkzeug.__version__ for Flask test_client
if not hasattr(werkzeug, "__version__"):
    try:  # pragma: no cover
        werkzeug.__version__ = importlib.metadata.version("werkzeug")
    except importlib.metadata.PackageNotFoundError:
        werkzeug.__version__ = "0"

# Blueprints
from src.leads import leads_bp
from src.orders import orders_bp
from src.render_routes import render_bp
from src.exports import exports_bp
from src.diagnostics_routes import diagnostics_bp
from src.editor import editor_bp
from src.analytics_routes import analytics_bp

BUILD_HASH = str(int(time.time()))


@click.command("diagnostics-selftest")
@with_appcontext
def diagnostics_selftest():
    """Run self-test hitting critical endpoints"""
    client = current_app.test_client()
    endpoints = ["/health", "/", "/leads", "/editor", "/render", "/exports", "/diagnostics"]
    failures = []
    for ep in endpoints:
        resp = client.get(ep)
        if resp.status_code not in (200, 302):
            failures.append((ep, resp.status_code))
    if failures:
        click.echo(f"❌ Failures: {failures}")
        raise SystemExit(1)
    click.echo("✅ Diagnostics self-test passed")


def register_cli(app: Flask) -> None:
    app.cli.add_command(diagnostics_selftest)


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.getenv("DATA_DIR", os.path.join(base_dir, "state"))
    app.config["DATA_DIR"] = data_dir
    app.jinja_env.globals.update(BUILD_HASH=BUILD_HASH)

    # Ensure runtime dirs exist
    for p in [
        os.path.join(data_dir, "uploads"),
        os.path.join(data_dir, "outputs", "videos"),
        os.path.join(data_dir, "outputs", "thumbs"),
        os.path.join(data_dir, "logs"),
        os.path.join(data_dir, "batches"),
        os.path.join(data_dir, "assets"),
        os.path.join(data_dir, "templates"),
        os.path.join(data_dir, "exports"),
    ]:
        os.makedirs(p, exist_ok=True)

    # Logging
    log_path = os.path.join(data_dir, "logs", "app.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
    )
    app.logger.info("=== FRIDAY Startup ===")

    # Optional: Sentry
    if os.environ.get("SENTRY_DSN"):
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        sentry_sdk.init(
            dsn=os.environ["SENTRY_DSN"],
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
        )
        app.logger.info("Sentry initialized")

    # Blueprints
    app.register_blueprint(leads_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(render_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(diagnostics_bp)
    app.register_blueprint(editor_bp)
    app.register_blueprint(analytics_bp)

    # CLI
    register_cli(app)

    # Error handlers
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        current_app.logger.exception("Unhandled exception")
        return jsonify({"error": str(e)}), 500

    @app.errorhandler(404)
    def _404(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def _500(e):
        return render_template("500.html", message=str(e)), 500

    # Routes
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return "ok", 200

    @app.route("/media/assets/<path:filename>")
    @login_required
    def media_assets(filename):
        return send_from_directory(os.path.join(data_dir, "assets"), filename)

    @app.route("/media/thumbs/<path:filename>")
    @login_required
    def media_thumbs(filename):
        return send_from_directory(os.path.join(data_dir, "outputs", "thumbs"), filename)

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Expose for Gunicorn
app = create_app()
