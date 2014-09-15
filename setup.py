from django_zipkin import __version__
from setuptools import setup

setup(
    name='django-zipkin',
    version=__version__,
    description='django-zipkin is a Django middleware and api for recording and sending messages to Zipkin',
    author='Zoltan Nagy, Zsolt Dollenstein',
    author_email='zoltan.nagy@prezi.com, zsolt.dollenstein@prezi.com',
    url='https://github.com/prezi/django-zipkin',
    packages=['django_zipkin'],
    license='WTFPL License',
    keywords='django zipkin middleware',
    platforms=['any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=['thrift >= 0.9.1'],
    tests_require=['mock >= 1.0', 'unittest2 >= 0.5.1'],
    extras_require={
        'configglue_support': ['configglue']
    },
    test_suite='tests.main',
)
