.. _label_gettingStarted:

Getting Started
===============

Dependencies
------------
* **python 2.7.x**
    * pyserial
    * pyQT4
    * psycopg2
    
* **postgresql 9.x** (http://www.postgresql.org)
* **pUtils** (https://github.com/GawpAzrag/pUtils.git)
* **d3** (http://d3js.org/)
    *d3 is only required for the visualizations*
* **Sphinx** (http://sphinx-doc.org/install.html)
    *Sphinx is only required to generate documentation*

Installing MTP
--------------
#. Create a container directory and *cd* into it.
#. Clone the MTP repo (https://github.com/pablo-miselu/MTP.git).
#. Create an environment variable named *MTP_TESTSTATION* tha points to the directory you just created.
    * From this point on the value of the environment variable you created can be used as *$MTP_TESTSTATION* in linux and OsX. If you are using windows, use *%MTP_TESTSTATION%* instead.
#. Add *$MTP_TESTSTATION/MTP* to your *PYTHONPATH*.
#. Initialize your postgres database with the initDB.sql script (*$MTP_TESTSTATION/MTP/scripts/initDB.sql*).
#. Set the parameters in *$MTP_TESTSTATION/MTP/config/database/helloWorldDbConfig.json* to match your database setup.
#. Run
    ``python $MTP_TESTSTATION/MTP/MTP/gui/MtpGui.py helloWorld.json helloWorldLimits.json helloWorldDbConfig.json helloWorldProcess``

    * Click the *Start Test* button
    * See the *Hello World!* pop up
    * Click *OK*
    * See the *PASS* pop up
    * Click *OK*
    * See the MTP main window is back to the *Start Test* button
    * Click on the *X* on the upper right corner to close it
    
**Congratulations you have installed an executed MTP!!**


