.. _device-profiles:

===============
Device Profiles
===============

Most network equipment vendors use different syslog message format to each other, some even use a different format for each of their devices. For ``napalm-logs`` to be able to take a syslog message from a device and output it in a vendor agnostic way, it needs to know the format of that device's messages.

The syslog format for each device is stored in a file which is titled the same as the operating system in question, under the directory ``napalm_logs/config/``.

Structure
+++++++++

The config file uses ``yaml`` format.

Each config file has two distinct sections, one to identify the OS that the message originated from, and one to identify each log message that ``napalm-logs`` should convert.

``Prefix``
----------

This section defines the log message ``prefix`` that will appear on all log messages from the OS in question.

Here is the config for ``junos``:

.. code-block:: yaml

	prefix:
	  time_format: "%b %d %H:%M:%S"
	  values:
		date: (\w+\s+\d+)
		time: (\d\d:\d\d:\d\d)
		hostPrefix: (re\d.)?
		host: ([^ ]+)
		processName: /?(\w+)
		processId: \[?(\d+)?\]?
		tag: (\w+)
	  line: '{date} {time} {hostPrefix}{host} {processName}{processId}: {tag}: '

What does each option mean?

``line``
--------

This represents the format of the part of the log message that present most of the time. Each section of the message that can change should be replaced by a variable. If a variable isn't always present then you should add it to the line but make that variable optional (covered in the ``values`` section).

Any white space in ``line`` will match any number of contiguous white space, therefore if it is possible for there to be either one white space or two white spaces, you should only add one white space to ``line``.

``values``
----------

This is used to specify the regex pattern for each of the variables specified in ``line``. All variables in ``line`` should have an entry under ``values``, even if you have no use for them.

Each of these variables will be output in a message dict after processing.

``messages``
++++++++++++

Here is where all log messages that should be matched are specified.

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

This is the vendor agnostic ID for the error message, the ``error`` for each message should be unique. Currently we are using the ``junos`` definitions where possible, this is likely to change.

``tag``
-------

This is the ID from the device itself.

This field is used when identifying if the log message is related to the configured error. Some devices use the same name for different types of logs, therefore this does not need to be unique.

If you look at the config for ``prefix`` above, you will see the variable ``tag`` in ``line``, this is the same ``tag`` as configured here and matched on.

``line``
--------

This is the same as ``line`` above.

``values``
----------

This is the same as ``values`` above, other than the fact they can be used in ``mapping`` (this will be covered under ``mapping``).

``replace``
-----------

This is used to manipulate a variable taken from the message via a lambda function which are defined under ``napalm_logs/config/__init__.py``. The reason for this is that sometimes the OpenConfig model expects variables in a certain format, i.e uppercase rather than lowercase.

``model``
---------

This is the OpenConfig model to use to output the log message. You can find all models and their structure here_.

.. _here: http://ops.openconfig.net/branches/master/

``mapping``
------------

This shows where in the OpenConfig model each of the variables in the message should be placed. There are two options, ``variables`` and ``static``. ``variables`` should be used when the value being set is taken from the message, and ``static`` should be used when the value is manually set.
