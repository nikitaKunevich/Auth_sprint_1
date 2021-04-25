import logging

from flask import Blueprint, jsonify, make_response, request, url_for
from flask_jwt_extended import current_user, get_jwt, jwt_required
from werkzeug.exceptions import Forbidden

import auth
from api.models import (
    TokenGrantOut,
    TokenInPassword,
    UserIn,
    UserInfoOut,
    UserLoginRecordsOut,
    UserPatchIn,
)
from storage import db
from storage.db_models import LoginRecord
from utils import parse_obj_raise

logger = logging.getLogger(__name__)

routes = Blueprint("v1", __name__, url_prefix="/api/v1")


@routes.route("/user", methods=["POST"])
def create_user():
    """create_user
    ---
    post:
      description: create_user
      summary: Create user
      requestBody:
        content:
          application/json:
            schema: UserIn

      responses:
        201:
          description: Ok
          headers:
            Location:
              description: uri with user info
              schema:
                type: string
                format: uri
                example: /user/dbdbed6b-95d1-4a4f-b7b9-6a6f78b6726e
          content:
            application/json:
              schema: UserInfoOut
        409:
          description: Conflict
      tags:
        - user
    """
    logger.debug("registration")
    user_data = parse_obj_raise(UserIn, request.get_json())
    logger.info(f"user with email: {user_data.email}")
    user = auth.create_user(user_data.email, user_data.password.get_secret_value())
    resp = make_response("Created", 201)
    resp.headers["Location"] = f"{url_for('.create_user')}/{user.id}"
    return resp


@routes.route("/user/<string:user_id>", methods=["GET"])
@jwt_required()
def get_user_info(user_id):
    """get_user_info
    ---
    get:
      description: get_user_info
      summary: Get detailed user info
      security:
        - jwt_access: []
      parameters:
      - name: user_id
        in: path
        description: user_id
        schema:
          type: string

      responses:
        200:
          description: Ok
          content:
            application/json:
              schema: UserInfoOut
        401:
          description: Unauthorized
        403:
          description: Forbidden
      tags:
        - user
    """
    logger.debug("get user info")

    if str(current_user.id) != user_id:
        raise Forbidden
    return UserInfoOut(
        id=str(current_user.id),
        email=current_user.email,
        registered_at=current_user.registered_at,
        active=current_user.active,
        roles=[role.name for role in current_user.roles],
    ).dict()


@routes.route("/user/<string:user_id>", methods=["PATCH"])
@jwt_required()
def change_user_info(user_id):
    """change_user_info
    ---
    patch:
      description: change_user_info
      summary: Change user email or password
      security:
        - jwt_access: []
      parameters:
      - name: user_id
        in: path
        description: user_id
        schema:
          type: string
      requestBody:
        content:
          'application/json':
            schema: UserPatchIn

      responses:
        200:
          description: Ok
        401:
          description: Unauthorized
        403:
          description: Forbidden
      tags:
        - user
    """
    logger.debug("change user info")
    if str(current_user.id) != user_id:
        raise Forbidden

    patch_data = parse_obj_raise(UserPatchIn, request.get_json())

    if patch_data.email:
        current_user.email = patch_data.email
    if patch_data.new_password_1:
        current_user.hashed_password = auth.hash_password(
            patch_data.new_password_1.get_secret_value()
        )
    db.session.add(current_user)
    db.session.commit()
    return "OK", 200


@routes.route("/user/<string:user_id>/login_history", methods=["GET"])
@jwt_required()
def get_login_history(user_id):
    """get_login_history
    ---
    get:
      description: get_login_history
      summary: Get login history
      security:
        - jwt_access: []
      parameters:
      - name: user_id
        in: path
        description: user_id
        schema:
          type: string

      responses:
        200:
          description: Return login history
          content:
            application/json:
              schema: UserLoginRecordsOut
        401:
          description: Unauthorized
        403:
          description: Forbidden
      tags:
        - login_history
    """
    logger.debug("get user login history")

    if str(current_user.id) != user_id:
        raise Forbidden

    records = db.session.query(LoginRecord).all()
    login_records = [record.to_api_model() for record in records]
    return UserLoginRecordsOut(logins=login_records).dict()


@routes.route("/token", methods=["POST"])
def create_token_pair():
    """Create token pair.
    ---
    post:
      description: Create token pair
      summary: Create new token pair for device
      requestBody:
        content:
          'application/json':
            schema: TokenInPassword

      responses:
        200:
          description: Return new tokens
          content:
            application/json:
              schema: TokenGrantOut
        400:
          description: Access error
      tags:
        - token
    """
    logger.debug("get token pair")

    # получение токена
    token_data = parse_obj_raise(TokenInPassword, request.get_json())

    user = auth.authenticate_with_email(
        token_data.email, token_data.password.get_secret_value()
    )
    access_token, refresh_token = auth.issue_tokens(
        user, request.user_agent, request.remote_addr
    )
    return jsonify(
        TokenGrantOut(access_token=access_token, refresh_token=refresh_token).dict()
    )


@routes.route("/refresh_token", methods=["POST"])
@jwt_required(refresh=True)
def update_token_pair():
    """update_token_pair
    ---
    post:
      description: update_token_pair
      summary: Revoke current token and create new token pair for device
      security:
        - jwt_refresh: []
      responses:
        200:
          description: OK
          content:
           application/json:
             schema: TokenGrantOut
        401:
          description: Unauthorized
      tags:
        - token
    """
    logger.debug("update token pair")
    token_data = get_jwt()
    access_token, refresh_token = auth.refresh_tokens(current_user, token_data)
    return jsonify(
        TokenGrantOut(access_token=access_token, refresh_token=refresh_token).dict()
    )


@routes.route("/refresh_token", methods=["DELETE"])
@jwt_required()
def revoke_refresh_token():
    """revoke_refresh_token
    ---
    delete:
      description: revoke_refresh_token
      summary: Revoke current refresh_token or all user's refresh_tokens
      security:
        - jwt_access: []
      parameters:
      - name: all
        in: query
        description: whether to logout from all devices
        schema:
          type: boolean

      responses:
        200:
          description: OK
        401:
          description: Unauthorized
      tags:
        - token
    """
    logger.debug("logout")

    if request.args.get("all") == "true":
        auth.logout_all_user_devices(current_user)
    else:
        auth.remove_device_token(current_user, request.user_agent)
    return "OK", 200
