.. _publisher-http:

====
HTTP
====

.. versionadded:: 0.3.0

Publish objects by invoking a HTTP endpoint.

This Publisher module can use several backends (currently just two: Tornado
and Requests). If no explicity backend is specified, using the
:ref:`publisher-http-backend` option, Tornado has the higher precedence due to
its speed, as it allows asynchronous requests.

.. note::
  
    The ref:`configuration-options-address` must have contain the ``http://``
    or ``https://`` schema. The address can however be specified more explicitly
    under the publisher configuration options, using the
    ref:`publisher-http-address` field.

Configuration examples:

- From the command line

.. code-block:: bash

  $ napalm-logs --publisher http --address https://example.com/hook

- Basic YAML configuration

.. code-block:: yaml

  publisher: http

- YAML configuration with more options

.. code-block:: yaml

  publisher:
    http:
      address: 'https://example.com/hook'
      method: POST
      headers:
        Authorization: OAuth 89a229ce1a8dbcf9f
      backend: tornado

Available options
^^^^^^^^^^^^^^^^^

.. _publisher-http-address:

``address``
-----------

Specifies the endpoint to invoke when a new event is published. The value
must contain the ``http://`` or ``https://`` schema.

Example:

.. code-block:: yaml

  publisher:
    http:
      address: 'https://example.com/hook'

.. _publisher-http-backend:

``backend``
-----------

The name of the toolset to use as backend to execute the HTTP requests. Can
choose between:

- ``tornado``
- ``requests``

When this option is not specifically configured, the publisher will try to use
the library found to be installed on the machine, Tornado having the highest
precedence.

Example:

.. code-block:: yaml

  publisher:
    http:
      backend: requests

.. _publisher-http-headers:

``headers``
-----------

A dictionary (hash / mapping) of the headers.

Example:

.. code-block:: yaml

  publisher:
    http:
      headers:
        Content-Type: text/json
        Pragma: no-cache
        Cache-Control: no-cache

.. _publisher-http-max_clients:

``max_clients``: ``10``
-----------------------

The maximum number of parallel clients.

Example:

.. code-block:: yaml

  publisher:
    http:
      max_clients: 20

.. _publisher-http-method:

``method``: ``POST``
--------------------

HTTP method to use. Choose from: ``GET``, ``POST``, ``PUT``, ``HEAD`` (the
others probably don't make sense, however they are allowed). For more details
see `this document <https://www.w3schools.com/tags/ref_httpmethods.asp>`_.

Example:

.. code-block:: yaml

  publisher:
    http:
      method: GET

.. _publisher-http-params:

``params``
----------

A set of parameters (key-value) to be sent together with the request.

Example:

.. code-block:: yaml

  publisher:
    http:
      params: key1=val1&key2=val2

.. _publisher-http-password:

``password``
------------

The password if needed to authenticate the HTTP request.

Example:

.. code-block:: yaml

  publisher:
    http:
      password: example

.. _publisher-http-username:

``username``
------------

The username if needed to authenticate the HTTP request.

Example:

.. code-block:: yaml

  publisher:
    http:
      username: example

.. _publisher-http-verify_ssl:

``verify_ssl``: ``true``
------------------------

By default, SSL certificates will be verified. However, for testing or debugging
purposes, SSL verification can be turned off. It is higly discouraged to disable
thio option in production environments.

Example:

.. code-block:: yaml

  publisher:
    http:
      verify_ssl: false
