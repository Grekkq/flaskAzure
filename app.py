from flask import Flask
from pathlib import Path


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        # DATABASE=Path.joinpath(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    @app.route('/')
    def hello():
        return 'Pustka!'

    @app.route('/hello')
    def hello():
        return 'No hej!'

    return app
