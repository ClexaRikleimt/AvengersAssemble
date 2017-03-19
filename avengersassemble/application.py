# encoding=utf-8
from flask import Flask
from celery import Celery

from flask_sqlalchemy import SQLAlchemy

from avengersassemble.config import metadata

db = SQLAlchemy(metadata=metadata)
celery = None


def create_app():
    app = Flask(__name__)
    app.config.from_object('avengersassemble.config')

    db.init_app(app)

    global celery
    celery = make_celery(app)

    return app


def make_celery(app):
    celery_ = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                     broker=app.config['CELERY_BROKER_URL'])
    celery_.conf.update(app.config)
    TaskBase = celery_.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery_.Task = ContextTask
    return celery_