django-zipkin
=============

|Build Status|

*django-zipkin* is a middleware and api for recording and sending
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

**Django**: ``1.3`` - ``1.7``


Getting started
---------------

Install the library:

::

    pip install django-zipkin

Add the middleware to the list of installed middlewares:

.. code:: python

    MIDDLEWARE_CLASSES = ('...',
                          'django_zipkin.middleware.ZipkinMiddleware',
                          '...')

Set the name your service will use to identify itself. This will appear
as the service name in Zipkin.

.. code:: python

    ZIPKIN_SERVICE_NAME = 'awesome-service'

``django-zipkin`` is now logging data compatible with the Zipkin
collector to the logger called ``zipkin``.

Getting the data to Zipkin
~~~~~~~~~~~~~~~~~~~~~~~~~~

From here you it's up to you to get the messages to Zipkin. Here's how
we do it at `Prezi <https://prezi.com>`_:

-  We configure logging in each service using ``django-zipkin`` to send
   log messages from the ``zipkin`` logger to the locally running Scribe
   instance, into the category ``zipkin``.
-  The Scribe instances are configured to forward the ``zipkin``
   category directly to the Zipkin collector. This is useful because
   Scribe buffers messages in case the collector (or the network to it)
   is down.

Another alternative may be logging to syslog, and using
``scribe_apache`` shipped with Scribe to send data to Zipkin (possibly
via a local Scribe server).

Recording annotations
~~~~~~~~~~~~~~~~~~~~~

``django-zipkin`` creates a single span per served requests. It
automatically adds a number of annotations (see below). You can also add
your own annotations from anywhere in your code:

.. code:: python

    from django_zipkin.api import api as zipkin_api

    zipkin_api.record_event('MySQL: "SELECT * FROM auth_users"', duration=15000)  # Note duration is in microseconds, as defined by Zipkin
    zipkin_api.record_key_value('Cache misses', 15)  # You can use string, int, long and bool values

Propagating tracing information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To identify which spans belong to the same trace, some information must
be passed on with inter-service calls. ``django-zipkin`` provides
facilities for this on both the client and the server side. The
middleware automatically reads the trace propagation HTTP headers
described `in the Zipkin
documentation <https://github.com/twitter/zipkin/blob/master/doc/collector-api.md#traceid-propagation>`_.
For propagating data to outgoing requests, a function returning a dict
of the correct HTTP headers is provided:

.. code:: python

    from django_zipkin.api import api as zipkin_api
    headers = zipkin_api.get_headers_for_downstream_request()

    # During a request returns something like this:
    {'X-B3-Sampled': 'false', 'X-B3-TraceId': 'b059fb34103a46f7', 'X-B3-Flags': '0', 'X-B3-SpanId': 'a42f4f3a045c54a5'}

Automatically generated annotations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``sr`` and ``ss`` annotations are automatically added by the middleware.
The following binary (key-value) annotations are also added:

+----------------------------------+--------------------------+-----------------------------------------------------------------------------------------------------+
| Annotation                       | Example value            | Added if                                                                                            |
+==================================+==========================+=====================================================================================================+
| http.uri                         | ``/api/v1/login``        | Always                                                                                              |
+----------------------------------+--------------------------+-----------------------------------------------------------------------------------------------------+
| http.statuscode                  | ``200``                  | Always                                                                                              |
+----------------------------------+--------------------------+-----------------------------------------------------------------------------------------------------+
| django.view.func\_name           | ``login``                | Always                                                                                              |
+----------------------------------+--------------------------+-----------------------------------------------------------------------------------------------------+
| django.view.class                | ``AuthView``             | If the view function is the method of a view-based class                                            |
+----------------------------------+--------------------------+-----------------------------------------------------------------------------------------------------+
| django.view.args                 | ``('oauth')``            | Always                                                                                              |
+----------------------------------+--------------------------+-----------------------------------------------------------------------------------------------------+
| django.view.kwargs               | ``{"next": "/index"}``   | Always                                                                                              |
+----------------------------------+--------------------------+-----------------------------------------------------------------------------------------------------+
| django.url\_name                 | ``myapp.views.login``    | Always                                                                                              |
+----------------------------------+--------------------------+-----------------------------------------------------------------------------------------------------+
| django.tastypie.resource\_name   | ``user``                 | If the request is served by Tastypie (specifically, when the view gets a kwarg ``resource_name``)   |
+----------------------------------+--------------------------+-----------------------------------------------------------------------------------------------------+

It's up to you to add ``cs`` and ``cr`` (client send and client receive)
annotations in whatever client you use.

Things to keep in mind
----------------------

Middleware order
~~~~~~~~~~~~~~~~

If a middleware above ``django-zipkin`` returns a response, then the
request processing part of ``django-zipkin`` will never be called,
resulting in an inconsistent internal state. In this case your custom
annotations and most of the automatically added annotations will be
lost, and timing information will be incorrect. An extra annotation will
be added with the following
value:\ ``No ZipkinData in thread local store. This can happen if process_request didn't run due to a previous middleware returning a response. Timing information is invalid.``

View wrappers
~~~~~~~~~~~~~

If your view is wrapped (for example with a decorator) without using the
``functools.wraps`` decorator, then ``django-zipkin`` has no way of
retrieving the name of the view. In this case ``django.view.func_name``
will be the function name of the wrapper function. This is something
you'll want to avoid in your own code.

One offender is Tastypie: ``django.view.func_name`` will always be
``wrapper``. On requests served by Tastypie the annotation
``django.tastypie.resource_name`` will be added with the name of the
Tastypie resource, and ``django.url_name`` will be something useful like
``api_dispatch_list``.

Zipkin UI vs. JSON annotation values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``django.view.kwargs`` annotation has a JSON string as its value for
easier automated processing. Unfortunately this make the UI display the
value as ``[object Object]``. See `Zipkin issue
#410 <https://github.com/twitter/zipkin/issues/410>`_ for any progress
on this. If you want to find the value on the web UI, you can open the
page source and search for ``django.view.kwargs``.

Customizing
-----------

You can customize the way ``django-zipkin`` works with the following
settings values. They are defined in ``django_zipkin/defaults.py``.

Settings variables
~~~~~~~~~~~~~~~~~~

**ZIPKIN\_SERVICE\_NAME**: Default ``None``. The service name that will
appear on Zipkin (the ``service_name`` value in the sent Thrift
objects).

**ZIPKIN\_LOGGER\_NAME**: Default ``'zipkin'``. The name of the logger
to use when sending Zipkin messages through the Python logging system.

**ZIPKIN\_DATA\_STORE\_CLASS**: Default
``'django_zipkin.data_store.ThreadLocalDataStore'``. ``django-zipkin``
needs to pass some data from the request processor to the response
processor. This same data needs to be accessible from anywhere in the
users code. The default implementation for this is to use thread-local
storage. ``gevent`` and ``greenlet`` monkey-patch it, so this
implementation works fine even under ``gunicorn`` and friends. You can
provide your own implementation - it needs to implement the methods of
``django_zipkin.data_store.BaseDataStore``.

**ZIPKIN\_ID\_GENERATOR\_CLASS**: Default
``'django_zipkin.id_generator.SimpleIdGenerator'``. The class used to
generate span and trace ids if we don't get one from the incoming
request.

Configglue
~~~~~~~~~~

``configglue`` support is provided via ``django_zipkin.schema``; you can
include it into your own schema like this:

.. code:: python

    from django_zipkin.schema import DjangoZipkinSection


    class MySchema(...):
       ...
       class zipkin(DjangoZipkinSection):
           pass

Hacking
-------

See
`CONTRIBUTING.md <https://github.com/prezi/django-zipkin/blob/master/CONTRIBUTING.md>`_
for guidelines.

You can start hacking on ``django-zipkin`` with:

.. code:: sh

    git clone https://github.com/prezi/django-zipkin.git
    cd django-zipkin
    git remote rename origin upstream
    virtualenv virtualenv
    . virtualenv/bin/activate
    pip install django
    python setup.py test

.. |Build Status| image:: https://travis-ci.org/prezi/django-zipkin.svg?branch=master
   :target: https://travis-ci.org/prezi/django-zipkin
