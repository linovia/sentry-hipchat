sentry-hipchat
==============

An extension for Sentry which integrates with Hipchat.
It will send issues notification to Hipchat.

Install
-------

Install the package via ``pip``::

    pip install sentry-hipchat

Add ``sentry_hipchat`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        # ...
        'sentry',
        'sentry_hipchat',
    )

Configuration
-------------

Go to your project's configuration page (Projects -> [Project]) and select the
Hipchat tab. Enter the required credentials and click save changes.

