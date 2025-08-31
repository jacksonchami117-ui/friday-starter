import os
import time
import logging
import sys
from logging.handlers import RotatingFileHandler

import click
import werkzeug
import importlib.metadata

from flask import Flask, render_template, send_from_directory, jsonify, current_app, redirect, url_for
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
from src.auth import auth_bp, User, ADMIN_PASSWORD
from src.health_routes import health_bp

BUILD_HASH = str(int(time.time()))


@click.command("diagnostics-selftest")
@with_appcontext
def diagnostics_selftest():
    """Run self-test hitting critical endpoints"""
    client = current_app.test_client()
    endpoints = ["/health", "/", "/leads/", "/editor/", "/render/", "/exports/", "/diagnostics/"]
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
    try:
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

        # Logging with rotating handler
        log_path = os.path.join(data_dir, "logs", "app.log")
        handlers = [logging.StreamHandler()]
        # Add rotating file handler
        if not os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
        rotating_handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=3)
        handlers.append(rotating_handler)
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=handlers,
        )
        app.logger.info("=== FRIDAY Startup ===")

        # Initialize Flask-Login
        login_manager = LoginManager()
        login_manager.login_view = "auth.login"
        login_manager.init_app(app)

        @login_manager.user_loader
        def load_user(user_id):
            return User() if ADMIN_PASSWORD and user_id == "admin" else None

        # Optional: Sentry
        if os.environ.get("SENTRY_DSN"):
            try:
                import sentry_sdk
                from sentry_sdk.integrations.flask import FlaskIntegration
                sentry_sdk.init(
                    dsn=os.environ["SENTRY_DSN"],
                    integrations=[FlaskIntegration()],
                    traces_sample_rate=1.0,
                )
                app.logger.info("Sentry initialized")
            except ImportError:
                app.logger.warning("Sentry SDK not available")

        # Blueprints - with error handling
        blueprints = [
            (leads_bp, "leads"),
            (orders_bp, "orders"), 
            (render_bp, "render"),
            (exports_bp, "exports"),
            (diagnostics_bp, "diagnostics"),
            (editor_bp, "editor"),
            (analytics_bp, "analytics"),
            (auth_bp, "auth"),
            (health_bp, "health"),
        ]
        
        for blueprint, name in blueprints:
            try:
                app.register_blueprint(blueprint)
                app.logger.debug(f"Registered blueprint: {name}")
            except Exception as e:
                app.logger.error(f"Failed to register blueprint {name}: {e}")
                raise

        # CLI
        register_cli(app)

        # Error handlers
        @app.errorhandler(Exception)
        def handle_exception(e):
            if isinstance(e, HTTPException):
                return e
            app.logger.exception("Unhandled exception")
            return jsonify({"error": str(e)}), 500

        @app.errorhandler(404)
        def _404(e):
            return render_template("404.html"), 404

        @app.errorhandler(500)
        def _500(e):
            return render_template("500.html", message=str(e)), 500

        # Routes
        @app.route("/")
        def home():
            return render_template("intro.html")
            
        @app.route("/dashboard")
        def dashboard():
            return render_template("index.html")
            
        @app.route("/home")
        def home_alt():
            return redirect(url_for('dashboard'))
            
        @app.route("/test-intro")
        def test_intro():
            return "INTRO ROUTE TEST - If you see this, the new code is deployed!"

        @app.route("/health")
        def health():
            return "ok", 200

        @app.route("/media/assets/<path:filename>")
        def media_assets(filename):
            if ADMIN_PASSWORD:
                # Apply login protection only if admin password is set
                from flask_login import current_user
                if not current_user.is_authenticated:
                    return redirect(url_for('auth.login'))
            return send_from_directory(os.path.join(data_dir, "assets"), filename)

        @app.route("/media/thumbs/<path:filename>")
        def media_thumbs(filename):
            if ADMIN_PASSWORD:
                # Apply login protection only if admin password is set
                from flask_login import current_user
                if not current_user.is_authenticated:
                    return redirect(url_for('auth.login'))
            return send_from_directory(os.path.join(data_dir, "outputs", "thumbs"), filename)

        return app

    except Exception as e:
        # If app creation fails, log the error and re-raise
        print(f"FATAL: Failed to create Flask app: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise


# Create app instance for Gunicorn
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
