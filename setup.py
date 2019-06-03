from zipkin import __version__
from setuptools import find_packages, setup

setup(
    name='zipkin',
    version=__version__,
    description='python api for sending data to Zipkin',
    author='Zoltan Nagy, Zsolt Dollenstein',
    author_email='zoltan.nagy@prezi.com, zsolt.dollenstein@prezi.com',
    url='https://github.com/prezi/python-zipkin',
    packages=find_packages(),
    package_data={'zipkin': ['thrift/*.thrift']},
    license='Apache2',
    keywords='zipkin python',
    platforms=['any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
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
    install_requires=['thriftpy >= 0.3.9', 'ply >= 3.9'],
    tests_require=['mock >= 1.0', 'unittest2 >= 0.5.1', 'pep8 >= 1.6.2', 'facebook-scribe >= 2.0'],
    test_suite='zipkin.tests',
)
