# -*- coding: utf-8 -*-

_blueprints = []


def add_blueprint(blueprint):
    _blueprints.append(blueprint)


def register_blueprints(app):
    # creates and registers blueprints
    from bwg360.controllers import home

    for blueprint in _blueprints:
        app.register_blueprint(blueprint)
