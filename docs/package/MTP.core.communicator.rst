.. _label_Communicator:

communicator Package
====================
This package is to contain all communicators.
The *GenericCommunicator* handles most situations, however for very specific conditions a new communicator module can be created and inserted here. A typical scenario where you would want to create your own communicator is if you are working with a specific binary protocol (*note: in some cases you can just inherit from GenericCommunicator and add your changes*).

A communicator, as its name suggests, handles the communication with the UUT and any other instrument or device in the system.

Here is how it works:

* One communicator is instantiated for each device or instrument that the test station computer wants to communicate with. The type of communicator to use is specified in the test station config file.
* The communicator takes care of:
  
  * Instantiating the driver (also specified in the test station config file)
  * Providing methods for send and receive data
  * Providing methods for easy parsing of the replies.
  * Logging and dispatching everything that goes through that communication channel
  * Sending the data on the communication channel to the appropriate "screen console"
  * Providing a method to create preformatted, time-stamped entries for informational purpose.
  * Handling all the buffers required to performed the tasks listed above.



:mod:`GenericCommunicator` Module
---------------------------------

.. automodule:: MTP.core.communicator.GenericCommunicator
    :members:
    :undoc-members:
    :show-inheritance: