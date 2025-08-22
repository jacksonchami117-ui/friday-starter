import os
import logging
from flask import Flask, render_template, send_from_directory, redirect, url_for, current_app
from flask_login import LoginManager, login_required, current_user
from werkzeug.exceptions import HTTPException
import time

# Blueprints
from src.leads import leads_bp
from src.orders import orders_bp
from src.render_routes import render_bp
from src.exports import exports_bp
from src.diagnostics_routes import diagnostics_bp
from src.editor import editor_bp

BUILD_HASH = str(int(time.time()))

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config['ENABLE_REGISTRATION'] = os.environ.get("ENABLE_REGISTRATION", "").lower() in ("1", "true", "yes")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.getenv("DATA_DIR", os.path.join(base_dir, "state"))
    app.config["DATA_DIR"] = data_dir

    app.jinja_env.globals.update(BUILD_HASH=BUILD_HASH)

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
        os.path.join(data_dir, "exports"),
    ]:
        os.makedirs(p, exist_ok=True)

    # Initialize database and Flask-Login
    try:
        from src import db
        db.init()
        db.ensure_default_admin()
        
        from src.user import User
        
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'accounts.login'
        login_manager.login_message = 'Please log in to access this page.'
        login_manager.login_message_category = 'info'
        
        @login_manager.user_loader
        def load_user(email):
            return User.get(email)
            
    except ImportError as e:
        print(f"Warning: Could not initialize authentication: {e}")

    # Logging to file + console
    log_path = os.path.join(data_dir, "logs", "app.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
    )
    app.logger.info("=== FRIDAY System Startup ===")

    # --- Authentication blueprint
    try:
        from src.accounts_routes import bp as accounts_bp
        app.register_blueprint(accounts_bp, url_prefix='/accounts')
    except Exception as e:
        print("[WARN] accounts blueprint not loaded:", e)
        
    # --- Landing pages (public, no auth required)
    try:
        from src.landing_routes import bp as landing_bp
        app.register_blueprint(landing_bp)
    except Exception as e:
        print("[WARN] landing blueprint not loaded:", e)

    # --- Settings blueprint + housekeeping
    try:
        from src.settings_routes import bp as settings_bp
        app.register_blueprint(settings_bp)
    except Exception as e:
        print("[WARN] settings blueprint not loaded:", e)

    try:
        from src.housekeeping import start_housekeeping_thread
        start_housekeeping_thread()
    except Exception as e:
        print("[WARN] housekeeping not started:", e)

    # --- Campaigns blueprint (Pitchlane-style UI)
    try:
        from src.campaigns_routes import bp as campaigns_bp
        app.register_blueprint(campaigns_bp)
    except Exception as e:
        print("[WARN] campaigns blueprint not loaded:", e)

    # --- Analytics blueprint
    try:
        from src.analytics_routes import analytics_bp
        app.register_blueprint(analytics_bp)
    except Exception as e:
        print("[WARN] analytics blueprint not loaded:", e)

    # Register blueprints
    app.register_blueprint(leads_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(render_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(diagnostics_bp)
    app.register_blueprint(editor_bp)

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
            return render_template("dashboard.html")
        except Exception as e:
            return f"Error rendering template: {str(e)}", 500

    @app.route("/home")
    def home():
        return render_template("dashboard.html")

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
