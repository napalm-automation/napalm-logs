.. _publisher-alerta:

================
Alerta Publisher
================

.. versionadded:: 0.9.0

Publish napalm-logs events to an `Alerta <https://alerta.io/>`__ endpoint.

.. note::

    The :ref:`configuration-options-address` must have contain the ``http://``
    or ``https://`` schema. The address can however be specified more explicitly
    under the publisher configuration options, using the
    :ref:`publisher-alerta-address` field.

    Also, note that you need to provide the URL to the Alerta API, typically 
    ending in ``/api``, but that may differ depending on your installation.

.. image:: ../_static/alerta_screenshot.png
    :width: 100%
    :alt: Alerta Screenshot

Configuration examples:

- From the command line

.. code-block:: bash

  $ napalm-logs --publisher alerta --address https://alerta.example.com/api

- Basic YAML configuration

.. code-block:: yaml

  publisher: alerta

- YAML configuration with more options

.. code-block:: yaml

  publisher:
    - alerta:
        address: https://alerta.example.com/api
        environment: Production
        key: HUGcQvd1_C-TKDrHVoZiNqaKS4jCcFYsGKuT0_W8
        max_clients: 20

Available options
^^^^^^^^^^^^^^^^^

.. _publisher-alerta-pairs:

``pairs``
---------

.. versionadded:: 0.10.0

Hash that defines the remapping of a specific *napalm-logs* notification to a
pair notification that will close the previous alert. For example, 
an ``INTERFACE_UP`` alert would close an existing ``INTERFACE_DOWN`` alert, 
instead of creating an alert for ``INTERFACE_UP``, and so on.

``pair`` defaults to:

.. code-block:: yaml

    pairs:
      INTERFACE_UP: INTERFACE_DOWN
      OSPF_NEIGHBOR_UP: OSPF_NEIGHBOR_DOWN
      ISIS_NEIGHBOR_UP: ISIS_NEIGHBOR_DOWN

The next options are generally inherited from the :ref:`publisher-http`
Publisher, with the following notes:

.. _publisher-alerta-address:

``address``
-----------

Specifies the Alerta API address. The value must contain the ``http://`` or
``https://`` schema.

Example:

.. code-block:: yaml

  publisher:
    - alerta:
        address: 'https://alerta.example.com/api'

.. _publisher-alerta-headers:

``headers``
-----------

The headers to use with the HTTP requests.


Some headers such as ``Content-type`` are added by default, while others
such as ``Authorization`` are added depending on the
:ref:`publisher-alerta-key` or :ref:`publisher-alerta-token` options.

.. _publisher-alerta-key:

``key``
-------

Optional value when executing the HTTP requests using an Alerta API key.

Example:

.. code-block:: yaml

  publisher:
    - alerta:
        address: 'https://alerta.example.com/api'
        key: HUGcQvd1_C-TKDrHVoZiNqaKS4jCcFYsGKuT0_W8

.. _publisher-alerta-token:

``token``
---------

Optional value when executing the HTTP requests using a bearer authentication.

Example:

.. code-block:: yaml

  publisher:
    - alerta:
        address: 'https://alerta.example.com/api'
        token: AbCdEf123456
