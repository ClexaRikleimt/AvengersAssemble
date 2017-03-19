# encoding=utf-8
from sqlalchemy import MetaData

metadata = MetaData(
    naming_convention={
        'pk': 'pk_%(table_name)s',
        'fk': 'fk_%(table_name)s_%(referred_table_name)s_%(referred_column_0_name)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        "ix": 'ix_%(column_0_label)s',
        "ck": "ck_%(table_name)s_%(constraint_name)s"
    }
)

SECRET_KEY = ''
SQLALCHEMY_DATABASE_URI = ''

SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_POOL_TIMEOUT = 20

CELERY_BROKER_URL = ''
CELERY_RESULT_BACKEND = ''

SLACK_VERIFICATION_TOKEN = ''
SLACK_CLIENT_ID = ''
SLACK_CLIENT_SECRET = ''
SLACK_OAUTH_STATE = ''

LOGIN_USERNAME = ''
LOGIN_PASSWORD = ''
