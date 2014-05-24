develop:
	pip install -e .
	pip install "file://`pwd`#egg=sentry-hipchat[test]"

test: develop
	py.test
