from flask_praetorian.constants import REFRESH_EXPIRATION_CLAIM
from werkzeug.useragents import UserAgent

from blocks import guard, jwt_blocklist
from constants import TIME_SLACK
from storage.db import db_session
from storage.db_models import User, LoginRecord


def verify_password(user: User, password: str):
    return guard.verify_and_update(user, password)


def create_user(email: str, password: str) -> None:
    hashed_pass = guard.hash_password(password)
    admin = User(email, hashed_pass)
    db_session.add(admin)
    db_session.commit()


def blacklist_token(token: str):
    token_data = guard.extract_jwt_token(token)
    expire_after = max(token_data["exp"], token_data.get(REFRESH_EXPIRATION_CLAIM, 0))
    jwt_blocklist.setex(f"bl:{token_data['jti']}", expire_after + TIME_SLACK, 1)


def is_blacklisted(jti: str) -> bool:
    return bool(jwt_blocklist.get(f'bl:{jti}'))


def authenticate(email: str, password: str, user_agent: UserAgent, ip: str) -> tuple[str, str]:
    user = guard.authenticate(email, password)
    access_token = refresh_token = guard.encode_jwt_token(user)

    # save login in history
    user_agent_str = f'{user_agent.platform}-{user_agent.browser}',

    record = LoginRecord(user_id=user.id, user_agent=user_agent_str, ip=ip)
    db_session.add(record)
    db_session.commit()

    return access_token, refresh_token


def issue_token(refresh_token: str) -> str:
    return guard.refresh_jwt_token(refresh_token)
