.. _label_config:

The Configuration System
========================

There are many aspects that are configuration driven.
When dealing with configurations some desired capabilities are:

* Change all settings in a single place
* Have all settings logocally ordered without overlap so it can easily be found
* Switch easily and fast between configuration sets (without having to change each setting one by one)
* Mix and match easily and speedily logically grouped settings

Those are the guiding principles.

The *Config* Directory
----------------------
*path MTP_TESTSTATION/MTP/config*

Here is where all configuration data is neatly stored. 
All of the configurations are loaded into memory by *SequencerThread* (see :ref:`label_SequencerThread`) and then passed to *Sequencer* (see :ref:`label_Sequencer`) which in turn passes the data to the appropriate modules (as described below). This is to maximize flexibility. This provides a single point where any configuration data could dynamically be modified and then it would flow seemlessly thorugh the entire system. And sometimes (especially on prototype builds) that is required.

| Having said that lets take a look at the contents of the config folder.
| Here we have:

**siteID.cfg**  *(file)*
    Contains simply one strings that uniquely identifies the site. 

**testStationConfig** *(folder)*
    Contains the configuration files that describe each of the test stations.
    This data is passed to and handled from that point on by the *ConfigurationManager* (see :ref:`label_ConfigurationManager`). It could be called the TestStationConfigurationManager to be more precise, but that makes the name kind of long :P .

**database** *(folder)*
    Contains the configuration of how to talk to the database.
    This data is passed to and handle from that point on by the *DatabaseApi* (see :ref:`label_DatabaseApi`).

**routeControl** *(folder)*
    Contains the configurations that describe the apropiate flow of units across the line (note that the configuration to enable or disable route control belongs in the specific testStationConfig files).
    This data is passed to and handled from that point on by the *RouteController* (see :ref:`label_RouteController`).

**limits** *(folder)*
    Contains the configuration files that specifies the limits for the parameters to be measure.
    This data is passed to and handled from that point on by the *LimitManager* (see :ref:`label_LimitManager`).
    
Specifying the config sets to use
---------------------------------

MTP uses one set of configuration of each *type*. That is why when launching MTP, 4 parameters are required. Which are the file names of the config sets/files to use. In the case of *routeControl* it refers to a folder that contain all the config/descriptor files of how the process (i.e the flow through the line) should be.

``python <MTP_TESTSTATION>/MTP/gui/MtpGui.py <testStationConfigFile> <limitsFile> <databaseFile> <routeControlProcess>``

| For example, the command you used on the getting started section:
| ``python <MTP_TESTSTATION>/MTP/gui/MtpGui.py helloWorld.json helloWorldLimits.json helloWorldDbConfig.json helloWorldProcess``

This gives you great flexibility, for example:

* Develop and troubleshoot every test station from one workstation
* Dynamic load balancing of test throughput capacity
* And so many other peculiar scenario that arise on the pre-production builds

*Usually a deployed test station will just have a one line script that specifies the config sets to use.*