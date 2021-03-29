import click

import auth
from app import app
from storage import db
from storage.db import Base, engine


@app.cli.command("initdb")
def initdb():
    db.init_db()


@app.cli.command("create-user")
@click.argument("name")
@click.argument("password")
def create_user(name, password):
    auth.create_user(name, password)


@app.cli.command("cleanup")
def cleanup():
    Base.metadata.drop_all(engine)
