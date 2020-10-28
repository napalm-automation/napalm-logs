.. _local_testing:

=============
Local Testing
=============

When adding new functionality to ``napalm-logs``, in particular new parsing templates, it can be helpful to run an end-to-end simulation.

Testing Installation
++++++++++++++++++++

As referenced in the :ref:`installation <installation>` documentation, it's advisable to use a Python Virtual Environment. This also applies for the testing installation.
Once you have the environment setup, you can install your local copy (with modifications) of ``napalm-logs`` in it:

.. code-block:: bash

    pip install -e <local_path/url>

Suggested startup options for ``napalm-logs`` once it's installed:

.. code-block:: bash

    napalm-logs -l debug --disable-security --publisher cli  --listener udp --port 5514

This will run ``napalm-logs`` in a ``debug`` log-level, without certificate-based authentication, using the ``cli`` publisher, while listening for ``syslog`` messages on UDP port 5514.
You can then proceed to send a sample ``syslog`` message to ``napalm-logs`` using ``netcat``:

.. code-block:: bash

    nc -w0 -u 127.0.0.1 5514 <<< "<32>Oct 24 20:21:27  vmx01 jlaunchd: System reaching processes ceiling high watermark: Contact to system administrator to clean up unnecessary processes or increase maxproc ceiling. Further process fork request may be denied."

The debug output will go to ``/var/log/napalm/logs/`` by default, and it will output the yang message on the CLI.
