from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from api import db, jwt

from api.auth_routes import auth_bp
from api.routes import profile_bp


def create_app():
    app = Flask(__name__)

    CORS(app,
         origins='*',
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Authorization', 'Content-Type', 'Accept', 'X-CSRF-TOKEN'],
         expose_headers=['Authorization', 'Content-Type'],
         supports_credentials=True,
        )

    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)

    @app.route('/api/v1/health', methods=['GET'])
    def healthCheck():
        return jsonify({'msg': 'The api is healthy'}), 200
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/v1')

    @app.errorhandler(Exception)
    def handle_error(e):
        status_code = getattr(e, 'code', 500)
        response = {'error': f'{e}'}
        return jsonify(response), status_code
    
    return app
    
app = create_app()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
