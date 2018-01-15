.. _serializer:

==========
Serializer
==========

.. versionadded:: 0.4.0

The Serializer subsystem is a pluggable interface used just before a structured
napalm-logs document is sent just before being published.

The default serializer used is :ref:`serializer-msgpack`.

From the command line, the Serializer can be selected using the ``--serializer``
(or ``-s``) option, e.g.:

.. code-block:: bash

  $ napalm-logs -s yaml
  $ napalm-logs --serializer pprint

From the configuration file, the Serializer can be specified using the
``serializer`` option.

Configuration file example:

.. code-block:: yaml

  serializer: json

Multiple Publishers
-------------------

It is possible to select a separate serializer per Publisher, specifying the 
name using the :ref:`publisher-opts-serializer` configuration option.

Available serializers
---------------------

.. toctree::
   :maxdepth: 1

   msgpack
   json
   yaml
   pprint
   str
