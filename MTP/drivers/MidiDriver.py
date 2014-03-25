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

class MidiDriver:
    """
    | A driver for a midi device over usb that simply wraps around the standard os python module.
    
    | On init it opens the connection.
    
    Args:
        * midiDevice (str):  Device to connect ot (e.g. /dev/midi2 )
    """

    def __init__(self,midiDevice):
        self.conn = os.open(midiDevice, os.O_RDWR|os.O_NONBLOCK)
   
    def transmit(self,data):
        """
        Sends the data to the midi device.
        
        Args:
        
        * data (bytearray): Data to send
        
        Returns:
            None
        """
        os.write(self.conn,data)

    
    def receive(self,bytesToRead):
        """
        Receives all available the data, at the time of the function call, from the midi device.
        
        Args:
            None
        
        Returns:
            A bytearray containing the bytes read
        """
        try:
            return bytearray (os.read(self.conn,bytesToRead))
        except:
            return bytearray()
    
    
    def close(self):
        """
        Closses the connection to midi device
        
        Args:
            None
        
        Returns:
            None
        """
        os.close(self.conn)