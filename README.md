# django-zipkin

TBD: Travis CI banner once the repo is opened and Travis CI integration is a go

*django-zipkin* is a middleware and an api for recording and sending messages to [Zipkin](https://github.com/twitter/zipkin).

## Getting started

Install the library:

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
TBD: list, when is each one added, example values

## Things to keep in mind
TBD: middleware order, special annotations

## Customizing
TBD: config values
TBD: (django-)configglue support

## Hacking

TBD: branch, PR

### Implementation details
TBD: thread local store
TBD: internal architecture

Testing: `python setup.py test` (ideally in a virtualenv)