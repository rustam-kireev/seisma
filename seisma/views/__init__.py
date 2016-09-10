# -*- coding: utf-8 -*-

import os

from .. import loader


PATH_TO_BLUEPRINTS = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'blueprints',
    ),
)

BLUEPRINTS_PACKAGE_PATH = 'seisma.views.blueprints'


def setup(app):
    blueprints = loader.load_blueprints(
        PATH_TO_BLUEPRINTS,
        package=BLUEPRINTS_PACKAGE_PATH,
    )
    for blueprint in blueprints:
        app.register_blueprint(blueprint)