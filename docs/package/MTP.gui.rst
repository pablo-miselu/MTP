.. _label_gui:

gui Package
===========
This package is the container for gui type modules.
The gui is EXTREMELY detached of MTP as a whole. All communication from the gui to the rest happens through two queues. So if you were to want to write your own gui, so long as you service those requests trhough the queue's you have complete freedom, you could even use an entirely differen graphical toolkit. 

Going a step further, those calls to the queues are only in a few places through the code, mainly *Sequencer* and *Communicator* (see :ref:`label_Sequencer` and :ref:`label_Communicator` respectively), so even customizing that part is feasible with little effort.

In the directory *<MTP_TESTSTATION>/MTP/img* are stored images for the use of the gui modules.

.. _label_MtpGui:

:mod:`MtpGui` Module
--------------------

.. automodule:: MTP.gui.MtpGui
    :members:
    :undoc-members:
    :show-inheritance:

