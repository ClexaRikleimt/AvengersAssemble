# encoding=utf-8
import requests

from avengersassemble.application import celery
from avengersassemble.models import Avengers, AuthedUsers


@celery.task
def parse_incoming_data(data):
    if 'event' not in data or 'authed_users' not in data:
        # Ignore malformed stuff
        return

    if 'channel' not in data['event'] or 'text' not in data['event']:
        # Malformed -> ignore
        return

    if 'avengers assemble' not in data['event']['text'].lower() or 'username' in data['event']:
        # Ignore message if message does not include 'avengers assemble' in any case and it is not sent by a bot
        return

    # There we go...
    # Update channels for the first authed user for this incoming set
    user = AuthedUsers.query.filter(AuthedUsers.slack_id == data['authed_users'][0]).first()

    # User will always exist, we can only get a user in the db when they are authenticated on the slack OAuth
    # First list public channels, if not in public channel, check private channels
    r_channels = requests.post('https://slack.com/api/channels.list', data={
        'token': user.authentication_token
    })
    r_channels_data = r_channels.json()
    if r_channels_data['ok']:
        for channel in r_channels_data['channels']:
            if channel['id'] == data['event']['channel']:
                handle_assembling(user, data['event']['channel'], False)
                return
        else:
            # TODO: Stop violating PEP20 and reformat this
            r_groups = requests.post('https://slack.com/api/groups.list', data={
                'token': user.authentication_token
            })
            r_groups_data = r_groups.json()
            if r_groups_data['ok']:
                for channel in r_groups_data['groups']:
                    if channel['id'] == data['event']['channel']:
                        handle_assembling(user, data['event']['channel'], True)
                else:
                    # Not a group or a channel. Probably a (group) DM. Ignore for now TODO
                    pass
            else:
                # Handle error TODO
                pass
    else:
        # Handle error TODO
        pass


def handle_assembling(user, channel, is_group):
    avengers = Avengers.query.all()
    for avenger in avengers:

        if is_group:
            url = 'https://slack.com/api/groups.invite'
        else:
            url = 'https://slack.com/api/channels.invite'

        if avenger.slack_id == user.slack_id:
            # skip self
            continue

        r = requests.post(url, data={
            'token': user.authentication_token,
            'channel': channel,
            'user': avenger.slack_id
        })
        r_data = r.json()
        if not r_data['ok']:
            # Handle error TODO
            pass

    # All avengers invited, send the bot message
    r_outgoing_bot = requests.post('https://slack.com/api/chat.postMessage', data={
        'token': user.authentication_token,
        'channel': channel,
        'text': 'AVENGERS ASSEMBLE!! :space_invader: {0}'.format(
            ' '.join('@{0}'.format(avenger.username) for avenger in avengers)
        ),
        'link_names': True,
        'as_user': False,
        'username': 'Bandrona helper',
        'icon_emoji': ':space_invader:'
    })
    r_outgoing_bot_data = r_outgoing_bot.json()
    if not r_outgoing_bot_data['ok']:
        # Handle error TODO
        pass
