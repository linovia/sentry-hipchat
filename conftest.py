import os


def pytest_configure(config):
    from django.conf import settings

    os.environ['DJANGO_SETTINGS_MODULE'] = 'sentry.conf.server'
    settings.DATABASES['default'].update({
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    })
