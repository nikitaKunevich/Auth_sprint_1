.PHONY = help setup test dev clean
.DEFAULT_GOAL := help

env ?= dev
ifneq (,$(wildcard ./deploys/$(env).env))
    include deploys/$(env).env
    export
endif

dev:
	PYTHONPATH=auth_api FLASK_APP=auth_api/app.py flask run --host=$${HOST} --port=$${PORT}

setup_demo:
	set -ax; source deploys/dev.env; set +ax
	flask cleanup
	flask initdb
	flask create-user admin@example.com	ZpGD69P4qeU

run:
	docker-compose up --build

sweep:
	isort auth_api
	black auth_api
	flake8 auth_api

clean:
	docker-compose down -v --remove-orphans

help:
	@echo "available commands: help, setup, test, run, clean"

