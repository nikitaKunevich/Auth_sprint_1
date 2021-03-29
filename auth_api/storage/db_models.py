import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from storage.db import Base, db_session


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column("password", String(255), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    active = Column(Boolean, default=True, nullable=False)
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))

    def __init__(self, email, hashed_password):
        self.email = email
        self.hashed_password = hashed_password

    def __repr__(self):
        return f"<User {self.email}, active: {self.active}, registered_at: {self.registered_at.date().isoformat()}>"

    @property
    def identity(self):
        return self.id

    @property
    def rolenames(self):
        return []

    @property
    def password(self):
        return self.hashed_password

    @classmethod
    def lookup(cls, email):
        return db_session.query(cls).filter_by(email=email).one_or_none()

    @classmethod
    def identify(cls, user_id):
        return db_session.query(cls).get(user_id)


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class RolesUsers(Base):
    __tablename__ = "roles_users"
    id = Column(Integer, primary_key=True)
    user_id = Column("user_id", UUID, ForeignKey("users.id"))
    role_id = Column("role_id", Integer, ForeignKey("roles.id"))


class LoginRecord(Base):
    __tablename__ = 'login_entries'
    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column("user_id", UUID, ForeignKey("users.id"))
    user_agent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip = Column(String(100))

    def __init__(self, user_id, user_agent, ip):
        self.user_id = user_id
        self.user_agent = user_agent
        self.ip = ip
