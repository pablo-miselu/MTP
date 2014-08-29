# Copyright 2013 Pablo De La Garza, Miselu Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 

class BaseTestSuite:
    """
    A base object to be inherit from when creating a test suite (see :ref:`label_testSuites`).

    On init:
    
    .. code-block:: python
    
        #Instantiates the dictionaries for custom data logging:
        self.numericDictionary = {}
        self.stringDictionary = {}
        self.filePointerDictionary = {}
        
        #Sets object variables with apropriate object handles
        self.configurationManager = configurationManager
        self.limitManager = limitManager
        self.commDict = self.configurationManager.getCommDict()
        self.guiApi = self.configurationManager.getGuiApi()   
    
    Args:
    
    * configurationManager (ConfigurationManager): An instance of a *ConfigurationManager* (see :ref:`label_ConfigurationManager`)
    """

    def __init__(self,configurationManager,limitManager):
        
        #Instantiates the dictionaries for custom data logging:
        self.numericDictionary = {}
        self.stringDictionary = {}
        self.filePointerDictionary = {}
        
        #Sets object variables with apropriate object handles
        self.configurationManager = configurationManager
        self.limitManager = limitManager
        self.commDict = self.configurationManager.getCommDict()
        self.guiApi = self.configurationManager.getGuiApi()
        
            
    def cleanup(self):
        """
        | Place holder.
        | It does nothing.
        
        Args:
            None
            
        Returns:
            None
        """

        return
       

    def debugTest_pass(self):
        """
        | A simple test that always passes.
        | Useful for development, testing and troubleshooting.
        
        Args:
            None
            
        Returns:
            The dictionary *{'testResult':'PASS'}*
        """
        return {'testResult':'PASS'}

    
    def debugTest_fail(self):
        """
        | A simple test that always fails.
        | Useful for development, testing and troubleshooting.
        
        Args:
            None
            
        Returns:
            The dictionary *{'testResult':'PASS'}*
        """

        return {'testResult':'FAIL'}


    def debugTest_helloWorld(self):
        """
        | A simple test that always passes.
        | It sends a *HelloWorld* to the default communicator (see :ref:`label_Communicator`)     
        | Useful for development, testing and troubleshooting.
        
        Args:
            None
            
        Returns:
            The dictionary *{'testResult':'PASS'}*
        """

        self.commDict['default'].log('HelloWorld',0)
        return {'testResult':'PASS'}


    def debugTest_sleep(self):
        """
        | A simple test that always passes.
        | It sleeps for 1 second.
        | Useful for development, testing and troubleshooting.
        
        Args:
            None
            
        Returns:
            The dictionary *{'testResult':'PASS'}*
        """
   
        from time import sleep
        sleep(1)
        return {'testResult':'PASS'}


    def debugTest_window_pDialog(self):
        """
        | A simple test that always passes.
        | Displays a dialog window.
        | Useful for development, testing and troubleshooting.
        
        Args:
            None
            
        Returns:
            The dictionary *{'testResult':'PASS'}*
        """
   
        self.guiApi.sendMessage({'command':'pDialog',
                                 'title':'pDialog Full Features',
                                 'imageFileName':'pass.png',
                                 'msg':'Hola!',
                                 'inputHeight':30,
                                 'buttonTextList':['YES','NO','Maybe'],
                                 'defaultButtonText':'NO'})
        
        t = None
        while (t==None):
            t = self.guiApi.getDialogReturn()
        self.commDict['default'].log(str(t),3)
        
        return {'testResult':'PASS'}