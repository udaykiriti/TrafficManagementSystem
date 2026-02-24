from flask import Flask
from flask_cors import CORS
import os
import argparse
import sys

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    # --- Configuration ---
    MAX_UPLOAD_SIZE_MB = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "200"))
    UPLOADS_DIR = os.path.abspath('uploads')
    DEBUG_UPLOAD = os.environ.get("DEBUG_UPLOAD", "1") == "1"

    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_MB * 4 * 1024 * 1024  # 4 files
    app.config["MAX_UPLOAD_SIZE_MB"] = MAX_UPLOAD_SIZE_MB
    app.config["UPLOADS_DIR"] = UPLOADS_DIR
    app.config["DEBUG_UPLOAD"] = DEBUG_UPLOAD

    # --- Ensure uploads directory exists ---
    try:
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        # Test write permissions
        test_file = os.path.join(UPLOADS_DIR, '.write_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        app.logger.info(f"Uploads directory ready: {UPLOADS_DIR}")
    except Exception as e:
        app.logger.error(f"Failed to initialize uploads directory: {e}")
        app.logger.error(f"Directory: {UPLOADS_DIR}, exists: {os.path.exists(UPLOADS_DIR)}")
        if os.path.exists(UPLOADS_DIR):
            import stat
            st = os.stat(UPLOADS_DIR)
            app.logger.error(f"Permissions: {oct(st.st_mode)}, Owner: {st.st_uid}:{st.st_gid}")

    # --- Register Blueprints ---
    # Add the src directory to the Python path
    sys.path.append(os.path.dirname(__file__))

    from src.routes import api
    app.register_blueprint(api)

    return app

app = create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Traffic optimizer API / live camera runner")
    parser.add_argument('--real', action='store_true', help='Run live camera ingestion instead of API server')
    parser.add_argument('--camera', action='append', help='Camera source (use multiple --camera entries, expected 4)')
    parser.add_argument('--verbose', action='store_true', help='Verbose optimizer output')
    args = parser.parse_args()

    if args.real:
        sources = args.camera if args.camera else []
        if not sources:
            env_sources = os.environ.get("CAM_SOURCES", "")
            sources = [s.strip() for s in env_sources.split(",") if s.strip()]
        if len(sources) != 4:
            print(f"[Live] Expected 4 camera sources, got {len(sources)}. Provide --camera four times or CAM_SOURCES comma-list.")
            raise SystemExit(1)

        try:
            from stream_ingest import run_live_optimization
        except Exception as e:
            print(f"[Live] Failed to import stream_ingest: {e}")
            raise SystemExit(1)

        payload, errors = run_live_optimization(sources, verbose=args.verbose)
        print("\n=== Live Optimization Result ===")
        print(payload)
        if any(errors):
            print("\nErrors:", errors)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
