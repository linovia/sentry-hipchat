"""
sentry_hipchat.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 by Linovia, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django import forms

from sentry.conf import settings
from sentry.plugins import Plugin, register

import sentry_hipchat

import urllib
import urllib2
import json
import logging

COLORS = {
    'ERROR': 'red',
    'WARNING': 'yellow',
    'INFO': 'green',
    'DEBUG': 'purple',
}


class HipchatOptionsForm(forms.Form):
    token = forms.CharField(help_text="Your hipchat API token.")
    room = forms.CharField(help_text="Room name or ID.")
    new_only = forms.BooleanField(help_text='Only send new messages.', required=False)
    notify = forms.BooleanField(help_text='Notify message in chat window.', required=False)
    include_project_name = forms.BooleanField(help_text='Include project name in message.', required=False)


@register
class HipchatMessage(Plugin):
    author = 'Xavier Ordoquy'
    author_url = 'https://github.com/linovia/sentry-hipchat'
    version = sentry_hipchat.VERSION
    description = "Event notification to Hipchat."

    slug = 'hipchat'
    title = 'Hipchat'
    conf_title = title
    conf_key = 'hipchat'
    project_conf_form = HipchatOptionsForm

    def is_configured(self, project):
        return all((self.get_option(k, project) for k in ('room', 'token')))

    def post_process(self, group, event, is_new, is_sample, **kwargs):
        new_only = self.get_option('new_only', event.project)
        if new_only and not is_new:
            return

        token = self.get_option('token', event.project)
        room = self.get_option('room', event.project)
        notify = self.get_option('notify', event.project) or False
        include_project_name = self.get_option('include_project_name', event.project) or False
        level = event.get_level_display().upper()
        link = '<a href="%s/%s/group/%d/">(link)</a>' % (settings.URL_PREFIX, group.project.slug, group.id)

        if token and room:
            self.send_payload(token, room, '%(site)s[%(server)s]%(project_name)s %(message)s %(link)s' % {
                    'server': event.server_name,
                    'site': ('%s ' % event.site) if event.site else '',
                    'project_name': (' <strong>%s</strong>' % event.project.name) if include_project_name else '',
                    'message': event.message,
                    'link': link,
                },
                notify, color=COLORS.get(level, 'purple'))

    def send_payload(self, token, room, message, notify, color='red'):
        url = "https://api.hipchat.com/v1/rooms/message"
        values = {
            'auth_token': token,
            'room_id': room,
            'from': 'Sentry',
            'message': message,
            'notify': int(notify),
            'color': color,
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
