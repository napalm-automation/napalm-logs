.. _docker:

======
Docker
======

Use the official napalm-logs Docker image
-----------------------------------------

.. versionadded: 0.5.0

Starting with :ref:`release-0.5.0`, there's a Docker image available at 
`<https://hub.docker.com/r/mirceaulinic/napalm-logs/>`_.

Pull the Docker image (example):

.. code-block:: bash

  docker pull mirceaulinic/napalm-logs:0.5.0

The :ref:`configuration-options-config-file` can, for example, be mounted as
volume to the container:

.. code-block:: bash

  docker run -d --name napalm-logs -v /path/to/napalm-logs/config/file:/etc/napalm/logs mirceaulinic/napalm-logs:0.5.0

For further details, please check the `Docker run reference 
<https://docs.docker.com/engine/reference/run/>`_ and how to `share filesystems 
<https://docs.docker.com/engine/reference/run/#volume-shared-filesystems>`_.
