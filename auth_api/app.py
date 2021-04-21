import logging

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint

import api.v1
import default_config
import token_store
from config import config
from storage import db
from storage.db_models import User

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.config.from_object(default_config.DefaultConfig)
    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
    )

    app.register_blueprint(api.v1.routes)

    SWAGGER_URL = "/swagger"
    API_URL = "/static/swagger.json"
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, config={"app_name": "Auth API"}
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

    @app.route("/static/swagger.json")
    def get_swagger():
        from openapi_spec import get_api_spec

        return jsonify(get_api_spec().to_dict())
        # return send_file(, mimetype='application/json')

    @app.before_first_request
    def startup():
        db.init_db()

    @app.after_request
    def after_request(response):
        db.session.remove()
        return response

    jwt = JWTManager(app)
    redis_host, redis_port = app.config["REDIS_SOCKET"].split(":")
    token_store.init(redis_host, redis_port, app.config["JWT_REFRESH_TOKEN_EXPIRES"])

    @jwt.user_identity_loader
    def user_identity_callback(user):
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.query(User).filter_by(id=identity).one_or_none()

    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(_jwt_header, jwt_payload):
        if jwt_payload.get("type") == "access":
            return False

        jti = jwt_payload.get("jti")
        return not token_store.does_refresh_token_exist(jti)

    app.cli = commands.cli

    return app


import commands  # noqa E402
