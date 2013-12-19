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

class SerialDriver:
    """
    | A driver for the serial port that simply wraps around the standard pyserial python module.
    
    | On init it opens the connection.
    
    Args:
        This are the exact same that pyserial uses
    """

    def __init__(self,port,baudrate,
                 bytesize=8,parity='N',stopbits=1,
                 timeout=1,xonxoff=False,rtscts=False,
                 writeTimeout=None,dsrdtr=False,
                 interCharTimeout=None):
        
        self.conn = serial.Serial  (port,baudrate,
                                    bytesize,parity,stopbits,
                                    timeout,xonxoff,rtscts,
                                    writeTimeout,dsrdtr,
                                    interCharTimeout)
   
   
    def transmit(self,data):
        """
        Sends the data to the serial port.
        
        Args:
        
        * data (str): Data to send
        
        Returns:
            None
        """
        self.conn.write(data)
   
    
    def receive(self,bytesToRead):
        """
        Receives the data form the serial port.
        
        Args:
        
        * bytesToRead (int): The amount of bytes to read
        
        Returns:
            A string containing the bytes read
        """
        return self.conn.read(bytesToRead)
    
    
    def close(self):
        """
        Closses the connection to the serial port
        
        Args:
            None
        
        Returns:
            None
        """
        self.conn.close()