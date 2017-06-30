===========
Instalation
===========

Creating a Virtualenv
+++++++++++++++++++++

It is recommended to install all the modules required for a new program into a ``Virtual Environment``. This ensures that the project dependencies are kept in its own environment, making sure that you don't have any versioning issues when other programs have the same dependencies.

.. code-block:: bash

    virtualenv napalm-logs

This will create a directory called ``napalm-logs`` in the directory that you are currently in.

Now you need to activate the virtualenv:

.. code-block:: bash

    source napalm-logs/bin/activate

Installing Napalm-logs
++++++++++++++++++++++

Now install napalm-logs using pip:

.. code-block:: bash

    pip install napalm-logs
