"""
"""

from unittest2 import TestCase
from mock import Mock

from sentry_hipchat.models import HipchatMessage


class PayLoadTest(TestCase):
    pass


class PostProcessTest(TestCase):

    def test_old_message(self):
        """
        Make sure known messages aren't sent again if the new_only option is on
        """
        group = Mock()
        event = Mock()
        # event.project.
        plugin = HipchatMessage()
        plugin.get_option = Mock()
        plugin.post_process(group, event, True, False)
        print event.mock_calls
        assert False