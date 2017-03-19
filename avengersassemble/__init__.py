# encoding=utf-8
from urllib.parse import unquote
from avengersassemble.application import create_app

app = create_app()

# Now that celery is initialised, import the views
from avengersassemble.views import EventHook, OAuthRedirect, BandronaSettings, Index


@app.template_filter('urldecode')
def jinja_filter_urldecode(s):
    return unquote(s)


@app.template_filter('split_slack_icon_url')
def jinja_filter_split_slack_icon_url(s):
    return s.split('&d=')[-1]


app.add_url_rule('/', Index.endpoint, view_func=Index.as_view(Index.endpoint))
app.add_url_rule('/slack/oauth', OAuthRedirect.endpoint, view_func=OAuthRedirect.as_view(OAuthRedirect.endpoint))
app.add_url_rule('/slack/message', EventHook.endpoint, view_func=EventHook.as_view(EventHook.endpoint),
                 methods=['POST'])
app.add_url_rule('/settings', BandronaSettings.endpoint, view_func=BandronaSettings.as_view(BandronaSettings.endpoint),
                 methods=['GET', 'POST'])


if __name__ == '__main__':
    app.run()
