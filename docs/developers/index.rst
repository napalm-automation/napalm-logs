===========
Development
===========
Here we will outline how to add new functionality to ``napalm-logs``.

Pluggable Modules
+++++++++++++++++

``napalm-logs`` is designed to be pluggable, so new methods for both input and output and can be added easily. This is to allow for the widest compatibility possible.

Adding a New Module
-------------------

If you need to use a different method to pass in your syslog messages or to get the processed messages, and it is not yet defined, you can write your own.

These are the basic steps required, and are the same for all of the pluggable sections.

Create a new module in the appropriate directory, name it the same as the protocol it will be using.

Copy the general format from an existing module.

All options for your module can be specified in the general config file, these will be passed to your module as ``kwargs``.

The module will be initialised, then started by calling the ``start()`` function.

If a signal is sent to the parent process, it will send a ``SIGTERM`` to your module, therefore this should be caught and the module should exit cleanly.

This can be done by including the following in your ``start()``:

.. code-block:: python

    signal.signal(signal.SIGTERM, self._exit_gracefully)
    self.__up = True
    # Code before the loop
    while self.__up:
        # Code to execute for each object

Then adding the following function:

.. code-block:: python

    def _exit_gracefully(self, signum, _): 
        log.debug('Caught signal in <process name> process')
        self.stop()

And also having a ``stop()`` which closes everything cleanly.

It is a good idea to look at some of the other modules to get an idea of how to structure yours.

Once written you should update ``__init__`` in the appropriate directory to include your newly created class, and add this class to the ``dict`` of all selectable classes.

If your module has dependencies then you should add a check to make sure the dependency is present, and call that function before adding your class to the ``dict`` of all selectable classes.

If you would like to have any default values for your module you can add these to ``napalm_logs/config/__init__.py`` under the appropriate ``*_opts`` dictionary.
