import json
import logging

from flask import Flask, current_app
from flask_praetorian import auth_required
from flask_restful import Api

import api.debug
import api.v1
import auth
import default_config
from blocks import guard
from config import config
from storage import db
from storage.db_models import User

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(config)
app.config.from_object(default_config.DefaultConfig)

restapi = Api(app, prefix="/api/v1")
restapi.add_resource(api.v1.User, "/user")
restapi.add_resource(api.v1.Token, "/token")

app.register_blueprint(api.debug.routes)
with app.app_context():
    guard.init_app(app, User, is_blacklisted=auth.is_blacklisted)


@app.route("/config")
@auth_required
def get_config():
    response = app.response_class(
        response=json.dumps(current_app.config, default=str, indent=4),
        status=200,
        mimetype="application/json",
    )
    return response


@app.before_first_request
def main():
    db.init_db()


@app.after_request
def after_request(response):
    db.db_session.remove()
    return response


if __name__ == "__main__":
    main()

# noinspection PyUnresolvedReferences
import commands
