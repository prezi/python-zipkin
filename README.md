# django-zipkin

TBD: Travis CI banner once the repo is opened and Travis CI integration is a go

*django-zipkin* is a middleware and an api for recording and sending messages to [Zipkin](https://github.com/twitter/zipkin).

## Getting started

Install the library:

TBD: release to PyPI, tag release, update this
```
pip install https://github.com/prezi/django-zipkin.git
```

Add the middleware to the list of installed middlewares:

```python
MIDDLEWARE_CLASSES = ('...',
                      'django_zipkin.middleware.ZipkinMiddleware',
                      '...')
```

Set the name your service will use to identify itself. This will appear as the service name in Zipkin.

```python
ZIPKIN_SERVICE_NAME = 'awesome-service'
```

`django-zipkin` is now logging data compatible with the Zipkin collector to the logger called `zipkin`.

### Getting the data to Zipkin

From here you it's up to you to get the messages to Zipkin. Here's how we do it at [Prezi](https://prezi.com):

 - We configure logging in each service using `django-zipkin` to send log messages from the `zipkin` logger to the
   locally running Scribe instance, into the category `zipkin`.
 - The Scribe instances are configured to forward the `zipkin` category directly to the Zipkin collector. This is
   useful because Scribe buffers messages in case the collector (or the network to it) is down.
   
   
Another alternative may be logging to syslog, and using `scribe_apache` shipped with Scribe to send data to Zipkin
(possibly via a local Scribe server).

### Recording annotations

`django-zipkin` creates a single span per served requests. It automatically adds a number of annotations (see below).
You can also add your own annotations from anywhere in your code:

```python
from django_zipkin.api import api

api.record_event('MySQL: "SELECT * FROM auth_users"', duration=15000)  # Note duration is in microseconds, as defined by Zipkin
api.record_key_value('Cache misses', 15)  # You can use string, int, long and bool values
```

### Propagating tracing information

To identify which spans belong to the same trace, some information must be passed on with inter-service calls. `django-zipkin`
provides facilities for this on both the client and the server side. The middleware automatically reads the trace 
propagation HTTP headers described [in the Zipkin documentation](https://github.com/twitter/zipkin/blob/master/doc/collector-api.md#traceid-propagation).
For propagating data to outgoing requests, a function returning a dict of the correct HTTP headers is provided:

```python
from django_zipkin.api import api
headers = api.get_headers_for_downstream_request()

# During a request returns something like this:
{'X-B3-Sampled': 'false', 'X-B3-TraceId': 'b059fb34103a46f7', 'X-B3-Flags': '0', 'X-B3-SpanId': 'a42f4f3a045c54a5'}
```

### Automatically generated annotations

`sr` and `ss` annotations are automatically added by the middleware. The following binary (key-value) annotations are
also added:

Annotation | Example value | Added if
-----------|---------------|---------
http.uri                  | `/api/v1/login` | Always
http.statuscode           | `200`           | Always
django.view.func_name     | `login`         | Always
django.view.class         | `AuthView`      | If the view function is the method of a view-based class
django.view.args          | `('oauth')`     | Always
django.view.kwargs        | `{"next": "/index"}` | Always
django.url_name           | `myapp.views.login`  | Always
django.tastypie.resource_name | `user`      | If the request is served by Tastypie (specifically, when the view gets a kwarg `resource_name`)

It's up to you to add `cs` and `cr` (client send and client receive) annotations in whatever client you use.

## Things to keep in mind

### Middleware order

If a middleware above `django-zipkin` returns a response, then the request processing part of `django-zipkin` will never
be called, resulting in an inconsistent internal state. In this case your custom annotations and most of the automatically
added annotations will be lost, and timing information will be incorrect. An extra annotation will be added with the following value:`No ZipkinData
in thread local store. This can happen if process_request didn't run due to a previous middleware returning a response.
Timing information is invalid.` 

### View wrappers

If your view is wrapped (for example with a decorator) without using the `functools.wraps` decorator, then `django-zipkin`
has no way of retrieving the name of the view. In this case `django.view.func_name` will be the function name of the
wrapper function. This is something you'll want to avoid in your own code.

One offender is Tastypie: `django.view.func_name` will always be `wrapper`. On requests served by Tastypie
the annotation `django.tastypie.resource_name` will be added with the name of the Tastypie resource, and `django.url_name`
will be something useful like `api_dispatch_list`.

### Zipkin UI vs. JSON annotation values

The `django.view.kwargs` annotation has a JSON string as its value for easier automated processing. Unfortunately
this make the UI display the value as `[object Object]`. See [Zipkin issue #410](https://github.com/twitter/zipkin/issues/410)
for any progress on this. If you want to find the value on the web UI, you can open the page source and search for
`django.view.kwargs`.

## Customizing

You can customize the way `django-zipkin` works with the following settings values. They are defined in
`django_zipkin/defaults.py`.

### Settings variables

**ZIPKIN_SERVICE_NAME**: Default `None`. The service name that will appear on Zipkin (the `service_name` value in the sent Thrift objects).

**ZIPKIN_LOGGER_NAME**: Default `'zipkin'`. The name of the logger to use when sending Zipkin messages through the Python logging system.

**ZIPKIN_DATA_STORE_CLASS**: Default `'django_zipkin.data_store.ThreadLocalDataStore'`. `django-zipkin` needs to pass 
some data from the request processor to the response processor. This same data needs to be accessible from anywhere in 
the users code. The default implementation for this is to use thread-local storage. `gevent` and `greenlet` monkey-patch
it, so this implementation works fine even under `gunicorn` and friends. You can provide your own implementation - it
needs to implement the methods of `django_zipkin.data_store.BaseDataStore`.
 
**`ZIPKIN_ID_GENERATOR_CLASS`**: Default `'django_zipkin.id_generator.SimpleIdGenerator'`. The class used to generate span
and trace ids if we don't get one from the incoming request.

### Configglue

`configglue` support is provided via `django_zipkin.schema`; you can include it into your applications schema like this:


```python
from django_zipkin.schema import DjangoZipkinSection


class MySchema(...):
   ...
   class zipkin(DjangoZipkinSection):
       pass
```

## Hacking

TBD: branch, PR
TBD: testing

### Implementation details
TBD: thread local store
TBD: internal architecture

Testing: `python setup.py test` (ideally in a virtualenv)