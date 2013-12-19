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

from MTP.core.BaseTestSuite import BaseTestSuite

class helloWorldTestSuite (BaseTestSuite):
    """
    A TestSuite created for example purposes
    """
        
    def helloWorld_msgBox(self):
        """
        | A simple test that always passes for example purposes.
        | Displays a helloWorld dialog window.
        
        Args:
            None
            
        Returns:
            The dictionary *{'testResult':'PASS'}*
        """
   
        self.guiApi.sendMessage({'command':'pDialog',
                                 'title':'Message Box',
                                 'msg':'Hello World!!',
                                 'buttonTextList':['OK']})
        
        t = None
        while (t==None):
            t = self.guiApi.getDialogReturn()
        self.commDict['default'].log(str(t),3)
        
        return {'testResult':'PASS'}
