# -*- coding: utf-8 -*-
from routes import register_routes
from flask import Flask
from dotenv import load_dotenv
from database import migrate_data
from helpers.gunicorn import StandaloneApplication, number_of_workers
import os


def set_config(app: Flask) -> None:
    """
    Set the configuration for the Flask app based on the environment variable.

    Args:
        app (Flask): The Flask app instance.

    Raises:
        ValueError: If the environment variable is unknown.
    """
    _deployed_env_ = os.getenv("ENVIRONMENT", default=None)
    if _deployed_env_ is None:
        print("No environment variable set for ENVIRONMENT. Defaulting to development.")
        app.config.from_object('config.DevelopmentConfig')
        return
    
    _deployed_env_ = _deployed_env_.lower()
        
    if _deployed_env_ == "production":
        app.config.from_object('config.ProductionConfig')
    elif _deployed_env_ == "staging":
        app.config.from_object('config.StagingConfig')
    elif _deployed_env_ == "development":
        app.config.from_object('config.DevelopmentConfig')
    else:
        raise ValueError(f"Unknown environment: {_deployed_env_}")

def create_app() -> Flask:
    app = Flask(__name__)
    load_dotenv()
    set_config(app)
    
    print(f"Creating app in {app.config.get("FLASK_ENV")} mode...")

    return app

if __name__ == "__main__":
    app = create_app()
    register_routes(app)
    migrate_data()
    
    if app.config["FLASK_ENV"] in ["staging", "production"]:
        StandaloneApplication(app, {'bind': '%s:%s' % ('0.0.0.0', '5000'),
            'workers': number_of_workers()}).run()
    else:
        port: int = int(os.environ.get("PORT", 5000))
        app.run(debug=True, host="0.0.0.0", port=port)
