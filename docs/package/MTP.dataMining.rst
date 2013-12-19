dataMining Package
==================
Once you have all your data in a nice ordered format in a database you may want to mine it and do somethign with it. That is what the module(s) in this package are for.

The directory *<MTP_TESTSTATION>/MTP/visualizations* contains visualizations that can be used with the data returned from *DataMiningApi* (see :ref:`label_DataMiningApi`).

* html
    These templates work with django as they are, you may need to adapt them a little bit for other web frameworks. Also for convenience if the template is loaded directly into a web browser (instead of rendering from a web server and passing to it actual data) the template will use some default data to show an example of how that type of visualization looks.

.. _label_DataMiningApi:

:mod:`DataMiningApi` Module
---------------------------
Contains calls to mine the data that then can easily be represented in the graphical form of choice.

Note: DataMiningApi and DatabaseApi are very similar, (they are like twin sisters) they could both be one thing. The reasons they are separate are, one, for clarity since they have different pusposes: while DatabaseApi is for the database interactions required for the line to run, DataMiningApi is all about report generation. The second and most important reason for them to be separate is the high likelyhood of them being executed in different machines and have different teams of developers. 

.. automodule:: MTP.dataMining.DataMiningApi
    :members:
    :undoc-members:
    :show-inheritance:

