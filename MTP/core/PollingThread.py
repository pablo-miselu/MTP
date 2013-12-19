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

import threading
from time import sleep

class PollingThread (threading.Thread):
    """
    | A generic thread for polling tasks.
    | It is used by the *Communicator* (see :ref:`label_Communicator`)
    | to retrieve data from a specific interface and places it into a buffer.
    
    Args:
    
    * pollingMethodCallback (func): The function that the thread will call everytime it polls
    * pollingInterval (float): Time in seconds that the thread will sleep between polls
    """
    def __init__(self,pollingMethodCallback,pollingInterval):
        super(PollingThread,self).__init__()
        
        self.pollingMethodCallback = pollingMethodCallback
        self.pollingInterval = pollingInterval
        
        self.stopFlag = False
    
    
    def run(self):
        """
        | The code that runs on the thread.
        | It will execute the specified callback until it is signal to stop.
        """
        while(not self.stopFlag):
            self.pollingMethodCallback()
            sleep(self.pollingInterval)
    
            
    def endThread(self):
        """
        Signals the thread to stop
        """
        self.stopFlag = True
    