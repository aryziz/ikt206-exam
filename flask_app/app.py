# -*- coding: utf-8 -*-
from routes import register_routes
from flask import Flask

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object('config')

    return app

if __name__ == "__main__":
    app = create_app()
    register_routes(app)
    app.run(debug=True, host="0.0.0.0")
