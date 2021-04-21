import click
from flask.cli import AppGroup, with_appcontext
from sqlalchemy_utils import create_database, database_exists

import auth
from openapi_spec import get_api_spec
from storage import db
from storage.db import Base, engine

cli = AppGroup()


@cli.command("initdb")
@with_appcontext
def initdb():
    if not database_exists(engine.url):
        print(f"creating database: {engine.url}")
        create_database(engine.url)
    db.init_db()


@cli.command("create-user")
@click.argument("name")
@click.argument("password")
@with_appcontext
def create_user(name, password):
    auth.create_user(name, password)


@cli.command("cleanup")
@with_appcontext
def cleanup():
    if database_exists(engine.url):
        Base.metadata.drop_all(engine)


@cli.command("showapi")
@with_appcontext
def showapi():
    print(get_api_spec().to_yaml())
