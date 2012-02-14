"""
sentry_hipchat.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 by Linovia, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django import forms

from sentry.models import ProjectOption
from sentry.plugins import Plugin, register
from sentry.plugins.helpers import get_option

import urllib
import urllib2
import json
import logging


class HipchatOptionsForm(forms.Form):
    token = forms.CharField(help_text="Your hipchat API token.")
    room = forms.CharField(help_text="Room name or ID.")


@register
class HipchatMessage(Plugin):
    title = 'Hipchat'
    conf_title = 'Hipchat'
    conf_key = 'hipchat'
    project_conf_form = HipchatOptionsForm

    def __init__(self, *args, **kwargs):
        super(HipchatMessage, self).__init__(*args, **kwargs)

    def is_configured(self, project):
        return bool(self.get_config(project))

    def get_config(self, project):
        if project.pk not in self._config:
            prefix = self.get_conf_key()
            config = {}
            for option in ('room', 'token'):
                try:
                    value = ProjectOption.objects.get_value(project, '%s:%s' % (prefix, option))
                except KeyError:
                    return {}
                config[option] = value
            self._config[project.pk] = config
        return self._config[project.pk]

    def post_process(self, group, event, is_new, is_sample, **kwargs):
        try:
            token = get_option('hipchat:token', event.project)
            room = get_option('hipchat:room', event.project)
            if token and room:
                self.send_payload(token, room, '[%s] %s' % (event.server_name, event.message))
        except Exception as e:
            # Avoid blocking event registration
            logger = logging.getLogger('sentry.plugins.hipchat')
            logger.error(str(e))

    def send_payload(self, token, room, message):
        url = "https://api.hipchat.com/v1/rooms/message"
        values = {
            'auth_token': token,
            'room_id': room,
            'from': 'Sentry',
            'message': message,
            'notify': False,
            'color': 'red',
        }
        data = urllib.urlencode(values)
        request = urllib2.Request(url, data)
        response = urllib2.urlopen(request)
        raw_response_data = response.read()
        response_data = json.loads(raw_response_data)
        if 'status' not in response_data:
            logger = logging.getLogger('sentry.plugins.hipchat')
            logger.error('Unexpected response')
        if response_data['status'] != 'sent':
            logger = logging.getLogger('sentry.plugins.hipchat')
            logger.error('Event was not sent to hipchat')
