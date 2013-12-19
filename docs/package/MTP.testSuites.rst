.. _label_testSuites:

testSuites Package
==================
Here is where the test suites will reside.
A test suite in this context is a collections of tests for one product. Putting them all in one object allows for easily moving test around across stations. Not something you want to do on a full speed mass production line, HOWEVER, when prototyping new technologies, it is priceless.

Inside we have... nothing! for it is for you to create it.

The test suite should inherit from class *MTP.core.BaseTestSuite.BaseTestSuite* (see :ref:`label_BaseTestSuite`).

This is the basic structure of a test suite object.


.. code-block:: python
       
    #import the BaseTestSuite
    from MTP.core.BaseTestSuite import BaseTestSuite
    
    #Create a class that inherits from it
    class MyTestSuite (BaseTestSuite):
            
        #Create one or many tests
        #You can name it whatever you want to, but
        #must not have any arguments other than 'self'
        def myTest(self):
            
            #Write some code.
            
            #Must return a dictionary with pairs of "measurementName":"measurementValue".
            #If it was a pass fail test, then:
            return {'testResult':'PASS'}

| The <measurementName> keyword should match one included on your limits file.
| The name of the file should match the name of the class inside (In this example would be MyTestSuite.py).