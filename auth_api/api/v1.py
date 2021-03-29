import time
from contextlib import contextmanager

import sqlalchemy.exc
from flask import Response, current_app, jsonify, make_response, request
from flask_restful import Api, Resource
from pydantic import PydanticValueError, ValidationError
from werkzeug.exceptions import BadRequest, HTTPException, NotFound

import auth
from api.models import (
    TokenGrantOut,
    TokenIn,
    TokenInPassword,
    TokenInRefresh,
    TokenRevokeIn,
    UserIn,
)
from blocks import guard
from exceptions import AlreadyExistsError, RequestValidationError
from storage import db, db_models
from utils import parse_obj_raise, validate_password
import logging

logger = logging.getLogger(__name__)


class User(Resource):
    def post(self):
        """Регистрация."""
        user_data = parse_obj_raise(UserIn, request.get_json())
        try:
            auth.create_user(user_data.email, user_data.password.get_secret_value())
        except sqlalchemy.exc.IntegrityError:
            raise AlreadyExistsError(f"User {user_data.email} already exists")
        return "Created", 201


class Token(Resource):
    def post(self):
        logger.info("post")

        token_data = parse_obj_raise(TokenIn, request.get_json())
        logger.info("after")

        if isinstance(token_data, TokenInPassword):
            logger.info("info")
            access_token, refresh_token = auth.authenticate(
                token_data.email,
                token_data.password.get_secret_value(),
                request.user_agent,
                request.remote_addr
            )
            return jsonify(TokenGrantOut(access_token=access_token, refresh_token=refresh_token).dict())

        elif isinstance(token_data, TokenInRefresh):
            # give new access_token
            # old_token = guard.read_token_from_header()
            access_token = auth.issue_token(token_data.refresh_token)
            return jsonify(TokenGrantOut(access_token=access_token, refresh_token=token_data.refresh_token).dict())
        else:
            raise BadRequest("Unknown grant type")

    # logout
    def delete(self):
        token = parse_obj_raise(TokenRevokeIn, request.get_json())
        auth.blacklist_token(token.token)
        return "OK", 201
