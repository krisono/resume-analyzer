import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.app_factory import create_app
    app = create_app()
except Exception as e:
    # Fallback for Vercel
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({"status": "ok", "error": str(e)})
    
    @app.route('/api/health')
    def api_health():
        return jsonify({"status": "ok", "error": str(e)})

# Vercel handler
app
