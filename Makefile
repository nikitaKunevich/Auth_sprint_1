.PHONY = help setup test dev clean
.DEFAULT_GOAL := help

env ?= dev
ifneq (,$(wildcard ./deploys/$(env).env))
    include deploys/$(env).env
    export
endif

dev:
	PYTHONPATH=auth_api FLASK_APP=auth_api/app.py flask run --host=$${HOST} --port=$${PORT}

run:
	docker-compose up --build

help:
	@echo "available commands: help, setup, test, run, clean"

