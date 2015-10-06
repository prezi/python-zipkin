python-zipkin
=============

|Build Status|

*python-zipkin* is an api for recording and sending
messages to `Zipkin <http://twitter.github.io/zipkin/>`_. Why use it?
From the http://twitter.github.io/zipkin/:

"Collecting traces helps developers gain deeper knowledge about how
certain requests perform in a distributed system. Let's say we're having
problems with user requests timing out. We can look up traced requests
that timed out and display it in the web UI. We'll be able to quickly
find the service responsible for adding the unexpected response time. If
the service has been annotated adequately we can also find out where in
that service the issue is happening."

Supported versions
------------------

**Python**: ``2.6``, ``2.7`` (the current Python Thrift release doesn't
support Python 3)

Recording annotations
~~~~~~~~~~~~~~~~~~~~~

``python-zipkin`` creates a single span per served requests. It
automatically adds a number of annotations (see below). You can also add
your own annotations from anywhere in your code:

.. code:: python

    from zipkin.api import api as zipkin_api

    zipkin_api.record_event('MySQL: "SELECT * FROM auth_users"', duration=15000)  # Note duration is in microseconds, as defined by Zipkin
    zipkin_api.record_key_value('Cache misses', 15)  # You can use string, int, long and bool values


Hacking
-------

See
`CONTRIBUTING.md <https://github.com/prezi/python-zipkin/blob/master/CONTRIBUTING.md>`_
for guidelines.

You can start hacking on ``python-zipkin`` with:

.. code:: sh

    git clone https://github.com/prezi/python-zipkin.git
    cd python-zipkin
    git remote rename origin upstream
    virtualenv virtualenv
    . virtualenv/bin/activate
    python setup.py test

.. |Build Status| image:: https://travis-ci.org/prezi/python-zipkin.svg?branch=master
   :target: https://travis-ci.org/prezi/python-zipkin
