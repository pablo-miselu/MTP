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

import os

class DeviceDriver:
    """
    | A device driver that simply wraps around the standard os python module.
    
    | On init it opens the connection.
    
    Args:
        * device (str):  Device to connect ot (e.g. /dev/midi2)
    """

    def __init__(self,device):
        self.conn = os.open(device, os.O_RDWR|os.O_NONBLOCK)
   
    def transmit(self,data):
        """
        Sends the data to the device.
        
        Args:
        
        * data (str): Data to send
        
        Returns:
            None
        """
        os.write(self.conn,data)

    
    def receive(self,bytesToRead):
        """
        Receives all available the data, at the time of the function call, from the device.
        
        Args:
            None
        
        Returns:
            A string containing the bytes read. Empty string if there was nothing to read.
        """
        try:
            return os.read(self.conn,bytesToRead)
        except:
            return ''
    
    
    def close(self):
        """
        Closses the connection to the device
        
        Args:
            None
        
        Returns:
            None
        """
        os.close(self.conn)