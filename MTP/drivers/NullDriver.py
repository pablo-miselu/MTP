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

import serial

class NullDriver:
    """
    | A driver that doesn't do anything, very useful for debugging.
    | Also if you were to want console windows to just send messages,
    | this driver will let you do such.
    |
    | It is recommended to always create one *Communicator* (see :ref:`label_Communicator`)
    | with a null driver and make this one your "default" *Communicator*, that way you can
    | have a high level summary of what is going on, separate of all the other communications
    | going on.
    """
    def __init__(self):
        pass
    
    
    def transmit(self,data):
        """
        | Does nothing.
        
        Returns:
            None
        """
        pass
    
    
    def receive(self,bytesToRead):
        """
        | Does nothing.
        
        Returns:
            Empty string
        """
        return ''
    
    
    def close(self):
        """
        | Does nothing.
        
        Returns:
            None
        """
        pass