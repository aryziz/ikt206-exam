import pytest
from flask import Flask
from app import create_app
from routes import register_routes
from flask.testing import FlaskClient

@pytest.fixture()
def app():
    app = create_app()
    register_routes(app)
    yield app
    
@pytest.fixture()
def client(app: Flask):
    with app.test_client() as client:
        yield client