# encoding=utf-8
from copy import deepcopy

from flask import request, jsonify, redirect, url_for, render_template, flash
from flask.views import View, MethodView

from werkzeug.exceptions import BadRequest, NotFound

import requests

from avengersassemble.application import db
from avengersassemble.config import SLACK_VERIFICATION_TOKEN, SLACK_CLIENT_ID, SLACK_CLIENT_SECRET, SLACK_OAUTH_STATE
from avengersassemble.decorators import requires_auth
from avengersassemble.tasks import parse_incoming_data
from avengersassemble.models import AuthedUsers, Avengers


class EventHook(MethodView):
    endpoint = 'event_hook'

    def post(self):
        data = request.get_json()
        if 'type' not in data or 'token' not in data:
            raise BadRequest()

        if data['token'] != SLACK_VERIFICATION_TOKEN:
            raise BadRequest()

        if data['type'] == 'url_verification':
            # Event challenge
            return jsonify(challenge=data['challenge'])
        elif data['type'] == 'event_callback' and data['event']['type'] == 'message':
            # Push the full dataset to celery, let it handle asynchronously
            parse_incoming_data.delay(data)
            # Reply to slack ASAP
            return jsonify(status='200 OK')  # For debugging... just reply with 200 OK, but now it is readable
        else:
            print(data)
            raise NotFound()


class Index(View):
    endpoint = 'index'
    decorators = [requires_auth]

    def dispatch_request(self):
        install_url = 'https://slack.com/oauth/authorize?client_id={0}&scope={1}&state={2}'.format(
            SLACK_CLIENT_ID,
            '%20'.join([
                'channels%3Aread',
                'channels%3Awrite',
                'channels%3Ahistory',
                'groups%3Aread',
                'groups%3Awrite',
                'groups%3Ahistory',
                'chat%3Awrite%3Abot',
                'users%3Aread'
            ]),
            SLACK_OAUTH_STATE
        )
        return render_template('index.html', install_url=install_url)


class OAuthRedirect(View):
    endpoint = 'oauth_redirect'

    def dispatch_request(self):
        if request.args.get('state') != SLACK_OAUTH_STATE:
            raise BadRequest()

        r = requests.post('https://slack.com/api/oauth.access', data={
            'client_id': SLACK_CLIENT_ID,
            'client_secret': SLACK_CLIENT_SECRET,
            'code': request.args.get('code')
        })

        data = r.json()

        if not data['ok']:
            # TODO: Handle error
            return jsonify(data)

        user = AuthedUsers.query.filter(AuthedUsers.slack_id == data['user_id']).first()
        if not user:
            user = AuthedUsers(data['user_id'], data['access_token'])
            db.session.add(user)
        else:
            user.authentication_token = data['access_token']

        db.session.commit()

        return redirect(url_for('bandrona_settings'))


class BandronaSettings(MethodView):
    endpoint = 'bandrona_settings'
    decorators = [requires_auth]

    def get(self):
        avengers = Avengers.query.all()

        token = AuthedUsers.query.first().authentication_token  # TODO...
        r = requests.post('https://slack.com/api/users.list', data={
            'token': token
        })
        data = r.json()
        if not data['ok']:
            # TODO: Handle error
            return jsonify(data)

        return render_template('bandrona.html', members=data['members'],
                               avengers=[avenger.slack_id for avenger in avengers])

    def post(self):
        token = AuthedUsers.query.first().authentication_token  # TODO...

        r = requests.post('https://slack.com/api/users.list', data={
            'token': token
        })
        data = r.json()
        if not data['ok']:
            # TODO: Handle error
            return jsonify(data)

        current_avengers = [avenger.slack_id for avenger in Avengers.query.all()]
        current_avengers_ = deepcopy(current_avengers)
        new_avengers = []

        # Check if existing council members disappeared
        for avenger in current_avengers:
            if avenger not in request.form:
                current_avengers_.remove(avenger)

        # Check if new council members were added
        for avenger in request.form.keys():
            if avenger not in current_avengers_:
                new_avengers.append(avenger)

        # Check what is different between new and old, and remove the old ones from the database
        for avenger in current_avengers:
            if avenger not in current_avengers_:
                # Remove
                Avengers.query.filter(Avengers.slack_id == avenger).delete()

        # Scroll through list of all members and add the new council members to the database
        for member in data['members']:
            if member['id'] in new_avengers:
                avenger = Avengers(member['name'], member['id'])
                db.session.add(avenger)

        # Commit changes
        db.session.commit()

        flash('Saved changes')

        return redirect(url_for('bandrona_settings'))
