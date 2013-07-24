"""
"""

from mock import Mock, call
import pytest

from sentry_hipchat.models import HipchatMessage
from sentry.conf import settings


class PayLoadTest(object):
    pass


DEFAULT_PLUGIN_CONFIGURATION = {
    'token': 'abcdefghijklmn',
    'room': 'test',
    'notify': False,
    'include_project_name': True,
    'new_only': False,
    'name': 'test project'
}


@pytest.fixture
def event():
    result = Mock()
    for k, v in DEFAULT_PLUGIN_CONFIGURATION.items():
        setattr(result.project, k, v)

    result.get_level_display = Mock()
    result.get_level_display.return_value = 'ERROR'

    result.message = 'An error has occured'

    return result


@pytest.fixture
def plugin():
    def get_option(k, d):
        return getattr(d, k)
    plugin = HipchatMessage()
    plugin.get_option = get_option

    plugin.get_url = Mock()
    plugin.get_url.return_value = 'http://localhost/someurl'

    plugin.send_payload = Mock()
    plugin.send_payload.return_value = None

    return plugin


class TestPostProcess(object):

    def test_old_message(self, event, plugin):
        """
        Make sure known messages aren't sent again if the new_only option is on
        """
        group = Mock()
        group.id = 1
        group.project.slug = "demo"

        settings.URL_PREFIX = 'http://localhost'

        event.project.new_only = True
        plugin.post_process(group, event, False, False)
        assert plugin.send_payload.mock_calls == []

        event.project.new_only = False
        plugin.post_process(group, event, False, False)
        assert plugin.send_payload.mock_calls == [
            call('abcdefghijklmn', 'test',
                '[ERROR] <strong>test project</strong> An error has occured [<a href="http://localhost/demo/group/1/">view on sentry</a>]',
                False, color='red')
        ]
