#!/usr/bin/env python
import sys


def run_tests():
    import django
    from django.conf import global_settings
    from django.conf import settings
    settings.configure(
        INSTALLED_APPS=['django_zipkin'],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'TEST_NAME': ':memory:',
                },
            },
        MIDDLEWARE_CLASSES=global_settings.MIDDLEWARE_CLASSES + (
            'django_zipkin.middleware.ZipkinMiddleware',),
        )
    if hasattr(django, 'setup'):
        django.setup()

    from django.test.simple import DjangoTestSuiteRunner

    test_runner = DjangoTestSuiteRunner(verbosity=1)
    return test_runner.run_tests(['django_zipkin'])


def main():
    failures = run_tests()
    sys.exit(failures)

if __name__ == '__main__':
    main()
