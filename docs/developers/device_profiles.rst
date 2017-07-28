.. _device-profiles:

===============
Device Profiles
===============

Most network equipment vendors use different syslog message format to each other,
some even use a different format for each of their devices. For ``napalm-logs``
to be able to take a syslog message from a device and output it in a
vendor-agnostic way, it needs to know the format of that device's messages.

Each network operating system has a set of profiles, defined under a directory
with the name of the platform, by default defined under ``napalm_logs/config``.
For example, the profiles for ``eos`` are defined under
``napalm_logs/config/eos/``, for ``junos`` under ``napalm_logs/config/junos/``
and so on.

Directory tree structure example:

.. code-block:: text

    napalm_logs/config/
    ├── __init__.py
    ├── eos
    │   └── init.yml
    ├── iosxr
    │   └── __init__.py
    ├── junos
    │   └── init.yml
    └── nxos
        └── init.yml

The user can select to extend the capabilities of the public library,
by defining profiles under a directory, specifying the path using the
:ref:`extension-config-path` option.

Custom directory tree example:

.. code-block:: text

    /pat/to/custom/config/
    ├── eos
    │   └── bgp_3_notification.py
    ├── junos
        └── init.yml
        └── UI_DBASE_LOGIN_EVENT.py
        └── SNMP_TRAP_LINK_DOWN.py

Each syslog message can be divided into two logical sections:

- the identification section, which provides enough information to identify the operating system that generated the message, together with other details, such as datetime, hostname, PRI_, process daemon, PID, etc. In napalm-logs, this section will be referenced as *prefix*.
- the actual message section, which is the part of the syslog message which contains the useful information. In napalm-logs, this section will be referenced as *message*.

.. _PRI: https://www.balabit.com/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html/bsdsyslog-pri.html

Example: given the message ``Mar 30 12:45:19 re0.edge01.bjm01 rpd[15852]: BGP_PREFIX_THRESH_EXCEEDED 1.2.3.4 (External AS 15169): Configured maximum prefix-limit threshold(160) exceeded for inet-unicast nlri: 181 (instance master)``:

- ``Mar 30 12:45:19 re0.edge01.bjm01 rpd[15852]: BGP_PREFIX_THRESH_EXCEEDED`` is the *prefix* section.
- ``1.2.3.4 (External AS 15169): Configured maximum prefix-limit threshold(160) exceeded for inet-unicast nlri: 181 (instance master)`` is the *message* section.

Both sections are platform-specific, and the *prefix* part can be used to
idenfiy the operating system that generated a certain syslog message. The
identification is done via *prefix matchers* (*prefix parsers*). Similarly,
the extraction of the information from the message section is done via
*message parsers*.

Please note that some platforms do not respect a single prefix pattern, but a
variety, this is why we need a couple of *prefix matchers*.

YAML Profiles
+++++++++++++

Each config file has two distinct sections, one to identify the OS that the
message originated from (called ``prefixes``), and one to identify each log
message that ``napalm-logs`` should convert (called ``messages``).

``prefixes``
^^^^^^^^^^^^

This section defines what we have defined above as *prefix matches*, or *prefix
parsers*, for the OS in question.

Here is the config for ``junos``:

.. code-block:: yaml

  prefixes:
    - time_format: "%b %d %H:%M:%S"
      values:
      date: (\w+\s+\d+)
      time: (\d\d:\d\d:\d\d)
      hostPrefix: (re\d.)?
      host: ([^ ]+)
      processName: /?(\w+)
      processId: \[?(\d+)?\]?
      tag: (\w+)
      line: '{date} {time} {hostPrefix}{host} {processName}{processId}: {tag}: '


.. note::

    Prefix parsers are usually defined as ``__init__.yml``, ``init.yml`` or
    ``index.yml``.

What does each option mean?

``line``
--------

This represents the format of the part of the log message that present most of
the time. Each section of the message that can change should be replaced by a
variable. If a variable isn't always present then you should add it to the line
but make that variable optional (covered in the ``values`` section).

Any white space in ``line`` will match any number of contiguous white space,
therefore if it is possible for there to be either one white space or two white
spaces, you should only add one white space to ``line``.

``values``
----------

This is used to specify the regex pattern for each of the variables specified
in ``line``. All variables in ``line`` should have an entry under ``values``,
even if you have no use for them.

Each of these variables will be output in a message dict after processing.

``messages``
^^^^^^^^^^^^

Here is where all log messages that should be matched are specified.

.. note::

    Message parsers are usually defined under a YAML file having the name of
    the error ID they produce. However, this is not absolutely mandatory.

Here is an example message:

.. code-block:: yaml

    messages:
      - error: INTERFACE_DOWN
        tag: SNMP_TRAP_LINK_DOWN
        values:
          snmpID: (\d+)
          adminStatusString: (\w+)
          adminStatusValue: (\d)
          operStatusString: (\w+)
          operStatusValue: (\d)
          interface: ([\w\-\/]+)
        replace:
          adminStatusString: uppercase
          operStatusString: uppercase
        line: 'ifIndex {snmpID}, ifAdminStatus {adminStatusString}({adminStatusValue}), ifOperStatus {operStatusString}({operStatusValue}), ifName {interface}'
        model: openconfig_interfaces
        mapping:
          variables:
          interfaces//interface//{interface}//state//admin_status: adminStatusString
          interfaces//interface//{interface}//state//oper_status: operStatusString
          static: {}

What does each option mean?

``error``
---------

This is the vendor agnostic ID for the error message, the ``error`` for each
message should be unique. Currently we are using the ``junos`` definitions where
possible, this is likely to change.

``tag``
-------

This is the unique ID from the device itself.

This field is used when identifying if the log message is related to the
configured error. Some devices use the same name for different types of logs,
therefore this does not need to be unique.

If you look at the config for ``prefix`` above, you will see the variable
``tag`` in ``line``, this is the same ``tag`` as configured here and matched on.

``match_on``: ``tag``
---------------------

This field name the field that try to match on. Defaults to ``tag``.

``line``
--------

This is the same as ``line`` above.

``values``
----------

This is the same as ``values`` above, other than the fact they can be used in
``mapping`` (this will be covered under ``mapping``).

``replace``
-----------

This is used to manipulate a variable taken from the message via a lambda
function which are defined under ``napalm_logs/config/__init__.py``. The reason
for this is that sometimes the YANG model expects variables in a certain
format, i.e uppercase rather than lowercase.

``model``
---------

This is the YANG model to use to output the log message. You can find all
models and their structure here_.

.. _here: http://ops.openconfig.net/branches/master/

``mapping``
------------

This shows where in the OpenConfig model each of the variables in the message
should be placed. There are two options, ``variables`` and ``static``.
``variables`` should be used when the value being set is taken from the message,
and ``static`` should be used when the value is manually set.

Pure Python profiles
++++++++++++++++++++

Writing YAML profiles is flexible and fast, but this model comes with many
logical limitations. For this reason, the developer can equally write pure
Python ``prefixes`` or ``messages`` parsers. They can be defined under the same
directory as the YAML descriptors, and they will be loaded dynamically.

.. note::

    The user is allowed to use any combination of YAML and pure Python parsers
    to match the messages and defined the prefixes.

Similarly to the YAML profilers, the Python profiles have two logical sections:
``prefixes`` that provide the operating system identification and ``messages``
that extract the information from the raw syslog messages and maps to an
object having the YANG hierarchy. Both are free-form Python modules,
with a single constraint that will be explained below.

``prefixes``
^^^^^^^^^^^^

A pure Python module that provides the prefix configuration, in order to
identify the operating system generating the message.

A module providing the prefix needs to define a function called ``extract``
that takes a single argument, ``msg`` which is the raw syslog message received
from the network device. The function has to return a dictionary with the
parts extracted from the syslog message, without any further processing. The
following keys are mandatory:

- ``host``: the network device hostname, as provided in the syslog message
prefix section.
- ``tag``: which is the unique identification tag of the syslog message, e.g. in the message ``Mar 30 12:45:19 re0.edge01.bjm01 rpd[15852]: BGP_PREFIX_THRESH_EXCEEDED 1.2.3.4 (External AS 15169): Configured maximum prefix-limit threshold(160) exceeded for inet-unicast nlri: 181 (instance master)``, the ``tag`` is ``BGP_PREFIX_THRESH_EXCEEDED``. Other tag examples: ``bgp_read_message``, ``ROUTING-BGP-5-MAXPFX`` or even ``Alarm set``.
- ``message``: is the message that what we have defied earlier as *the message section*, e.g. ``User 'dummy' entering configuration mode``.

.. note::

    Prefix parsers are usually defined as ``__init__.py``, ``init.py`` or
    ``index.py``.

The following example is a Python prefix parser for NX-OS:

.. code-block:: python

    import re
    from collections import OrderedDict

    import napalm_logs.utils

    _RGX_PARTS = [
        ('pri', r'(\d+)'),
        ('host', r'([^ ]+)'),
        ('date', r'(\d+ \w+ +\d+)'),
        ('time', r'(\d\d:\d\d:\d\d)'),
        ('timeZone', r'(\w\w\w)'),
        ('tag', r'([\w\d-]+)'),
        ('message', r'(.*)')
    ]
    _RGX_PARTS = OrderedDict(_RGX_PARTS)

    _RGX = '\<{0[pri]}\>{0[host]}: {0[date]} {0[time]} {0[timeZone]}: %{0[tag]}: {0[message]}'.format(_RGX_PARTS)


    def extract(msg):
        return napalm_logs.utils.extract(_RGX, msg, _RGX_PARTS)

The example above matches messages from NX-OS looking like: ``<190>sw01.bjm01: 2017 Jul 26 14:42:46 UTC: %SOME-TAG: this is a very useful syslog message``,
and extracts the following details:

- ``pri``: 190
- ``host``: sw01.bjm01
- ``tag``: SOME-TAG
- ``date``: 2017 Jul 26
- ``time``: 14:42:46
- ``timeZone``: UTC
- ``message``: this is a very useful syslog message

These details are returned by the ``extract`` function, which returns a
dictionary such as:

.. code-block:: python

    {
      'pri': '190',
      'host': 'sw01.bjm01',
      'tag': 'SOME-TAG',
      'time': '14:42:46',
      'date': '2017 Jul 26',
      'timeZone': 'UTC',
      'message': 'this is a very useful syslog message'
    }

Except ``tag``, ``host`` and ``message``, all the other fields can be optional,
and **they are platform-specific** (or even message-type-specific, in some very
sad cases). However, there are some particular cases when the other fields can
provide interesting information, eventually to be used to match messages using
the ``match_on`` option.

``messages``
^^^^^^^^^^^^

Writing a message parser can be equally simple and flexible, the rules to
consider being:

- Define a function called ``emit`` that generates the syslog message.
- A dunder called ``__yang_model__`` that specifies the YANG model.
- A variable names ``__tag__`` that specifies the tag name, that is used to match when comparing the value of the ``tag`` field extracted from the message prefix and determine what parser should process the syslog message. However, this variable is optional -- when not defined, it will use the filename as tag.
- A variable called ``__error__`` that defines the name of the global error. Each structured message published by napalm-logs has a certain error tag, that is unique and cross-platform. This variable is also optional -- when not defined, the error ID will be the file name.

.. note::

    Message parsers are usually defined under a Python file having the name of
    the error ID they produce. However, this is not absolutely mandatory.

Useful function
^^^^^^^^^^^^^^^

At times, the developer may find very useful several function, in order to
acomplish recurrent tasks:

- ``napalm_logs.utils.extract``: Extracts the fields from a unstructured text, given a field-regex mapping. Please check the previous paragraph for an usage example.
- ``napalm_logs.utils.setval``: Set a value under the dictionary hierarchy identified under the key. The key ``'foo//bar//baz'`` will configure the value under the dictionary hierarchy ``{'foo': {'bar': {'baz': {}}}}``. Example:

.. code-block:: python

    >>> napalm_logs.utils.setval('foo//bar//baz', 'value')
    {'foo': {'bar': {'baz': 'value'}}}

- ``napalm_logs.utils.traverse``: Traverse a dict or list using a slash delimiter target string. The target ``'foo//bar//0'`` will return ``data['foo']['bar'][0]`` if this value exists, otherwise will return empty dict. Return ``None`` when not found. This can be used to verify if a certain key exists under dictionary hierarchy.
