from flask import Flask, jsonify
from flask_cors import CORS

from .routes import api


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(api, url_prefix="/api")

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
