import logging
from typing import Optional

from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from passlib.hash import argon2
from werkzeug.useragents import UserAgent

import token_store
from exceptions import AlreadyExistsError, PasswordAuthenticationError
from storage import db
from storage.db_models import LoginRecord, User

logger = logging.getLogger(__name__)


def verify_password(user: User, password: str):
    return argon2.verify(password, user.hashed_password)


def hash_password(password: str) -> str:
    return argon2.hash(password)


def create_user(email: str, password: str) -> Optional[User]:
    # checking if user already exists
    user_exists = User.get_user_universal(email) is not None
    if user_exists:
        raise AlreadyExistsError(f"User {email} already exists")

    hashed_pass = hash_password(password)
    user = User(email=email, hashed_password=hashed_pass)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_with_email(email: str, password: str) -> User:
    user = User.get_user_universal(email=email)
    if not user:
        logger.debug(f"user with email {email} not found")
        raise PasswordAuthenticationError
    if not verify_password(user, password):
        logger.debug("password is not valid")
        raise PasswordAuthenticationError
    return user


def issue_tokens(user: User, user_agent: UserAgent, ip: str) -> tuple[str, str]:
    device_id = token_store.user_agent_to_device_id(user_agent)
    access_token = create_access_token(user, additional_claims={"device": device_id})
    refresh_token = create_refresh_token(user, additional_claims={"device": device_id})
    token_data = decode_token(refresh_token)
    token_store.replace_refresh_token(
        token_data["jti"], token_data["sub"], token_data["device"]
    )

    # save login in history
    browser_string = user_agent.browser
    if user_agent.version:
        browser_string = f"{browser_string}-{user_agent.version}"
    record = LoginRecord(
        user_id=user.id,
        ip=ip,
        user_agent=user_agent.string,
        platform=user_agent.platform,
        browser=browser_string,
    )
    db.session.add(record)
    db.session.commit()

    return access_token, refresh_token


def refresh_tokens(user: User, token_data: dict) -> tuple[str, str]:
    logger.debug(f"refresh_tokens: {token_data=}, {user=}")

    device_id = token_data["device"]

    access_token = create_access_token(user, additional_claims={"device": device_id})
    refresh_token = create_refresh_token(user, additional_claims={"device": device_id})
    new_token_jti = decode_token(refresh_token)["jti"]

    token_store.replace_refresh_token(
        new_token_jti, token_data["sub"], token_data["device"]
    )

    return access_token, refresh_token


def logout_all_user_devices(user: User):
    token_store.remove_all_user_refresh_tokens(user.id)


def remove_device_token(user: User, user_agent: UserAgent):
    device_id = token_store.user_agent_to_device_id(user_agent)
    token_store.remove_refresh_token(user.id, device_id)
