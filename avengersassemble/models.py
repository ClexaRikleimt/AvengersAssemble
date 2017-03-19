# encoding=utf-8
from avengersassemble.application import db


class Avengers(db.Model):
    """Who are part of the Bandrona Council?"""
    __tablename__ = 'avenger'
    id = db.Column(db.Integer, primary_key=True)
    slack_id = db.Column(db.String(15), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, username, slack_id):
        self.username = username
        self.slack_id = slack_id


class AuthedUsers(db.Model):
    """Users authenticated with the Slack integration"""
    __tablename__ = 'authed_users'
    id = db.Column(db.Integer, primary_key=True)
    slack_id = db.Column(db.String(15), unique=True)
    authentication_token = db.Column(db.String(255), nullable=False)

    def __init__(self, slack_id, auth_token):
        self.slack_id = slack_id
        self.authentication_token = auth_token

