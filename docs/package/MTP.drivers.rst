.. _label_drivers:

drivers Package
===============
Here is where all "MTP level drivers" should be placed.

An MTP level driver is an object that has the methods:

* def __init__(self, <params> )
    Here you initialize or open the connection.
    You can spacify as many parameters as you want so long that this matches the params entry on the configuration file for the test station

* def transmit(self,data):
   Here you send data
    
* def receive(self,bytesToRead):
   Here you receive data
        
* def close(self):
   Here you close the connection.

You can create your own drivers if the ones listed below does not meet your needs.

.. _label_NullDriver:

:mod:`NullDriver` Module
------------------------

.. automodule:: MTP.drivers.NullDriver
    :members:
    :undoc-members:
    :show-inheritance:


.. _label_SerialDriver:

:mod:`SerialDriver` Module
--------------------------

.. automodule:: MTP.drivers.SerialDriver
    :members:
    :undoc-members:
    :show-inheritance:

