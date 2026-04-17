# Creating Flask app in function

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

from config import config_map
from app.database import init_db

def create_app(config_name = 'development'):
    app = Flask(__name__)

    app.config.from_object(config_map[config_name])

    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
        hours = app.config.get('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 24)
    )

    CORS (app, resources = {
        r"/api/*":{
            "origins": [app.config['FRONTEND_URL'], "http://localhost:5500"],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    jwt = JWTManager(app)

    # Database

    with app.app_context():
        init_db(app)

    # Register Blueprints

    from app.auth import auth_bp
    from app.tasks import tasks_bp
    from app.analytics import analytics_bp

    app.register_blueprint(auth_bp, url_prefix = '/api/auth')
    app.register_blueprint(tasks_bp, url_prefix = '/api')
    app.register_blueprint(analytics_bp, url_prefix = '/api')

    # Check route

    @app.route('/api/health')
    def health(): 
        return {'status': 'ok', 'message': 'ProductivityPro API is running'}

    return app