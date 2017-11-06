.. _device-configuration:

===================================
Supported devices and configuration
===================================

Napalm-logs can process syslog messages from the following network operating
systems:

.. toctree::
   :maxdepth: 1

   junos
   iosxr
   eos
   nxos

To see how to configure the network device, check the documents referenced
above. Note that the examples in each case represents the configuration used to
send the syslog messages over UDP to a certain IP address and port. Remember
that napalm-logs is able to receive the messages over UDP (by default), as well
as via other channels - see :ref:`listener`. While napalm-logs can be the UDP
endpoint configured to receive the messages straight from the network device,
there is no standard configuration, setup or architecture for the rest of the
Listeners, but rather it depends very much on how you want to design your own
use case.

Napalm-logs is able to publish messages from unidentified operating systems (or
partially parsed messages), but this behaviour is disabled by default.
To allow publishing messages from operating systems that are not supported yet
by napalm-logs (but they will not be parsed at all), you can configure the
:ref:`publisher-opts-send-unknown` option on the publisher (i.e.,
``send_unknow: true``). To publish partially parsed messages from supported
operating systems, but without a mapping for a certain class of messages, you
can use the :ref:`publisher-opts-send-raw` option.
