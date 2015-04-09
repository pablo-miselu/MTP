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

import psycopg2
import json
import os
import pUtils

class SQL:
    
    """
    A simple wrapper of psycopg2, to use to talk to the database.
    
    Args:
    
    * host (str): Host computer where the database is
    * port (int): Port where the host is listening for database connections
    * dbname (str): Database name
    * user (str): Username to use when connecting
    * password (str): Password to use when connecting to the database
    """
    
    def __init__(self,host,port,dbname,user,password):
        self.dbConfig = {'host':host,'port':port,'dbname':dbname,'user':user,'password':password}

    def conn(self):
        """
        Opens a connection using the parameters passed on init. Stores as object variables the connection handle and the cursor handle.
        
        Args:
            None
            
        Returns:
            None
        """
        self.cnx = psycopg2.connect(**self.dbConfig) 
        self.cur = self.cnx.cursor()
    
    def read(self,s,v):
        """
        Executes the specified SQL statement and returns the resulting table as a nested list of lists.
        
        Args:
        
        * s (str): A string containing the sql query
        * v (list): A vector containing any parametrized arguments of the query
        
        Returns:
            A list of lists with the data of the table resulting from the query.
        """
        self.cur.execute(s,v)
        data = self.cur.fetchall()
        return data
        
    def execute(self,s,v):
        """
        Executes the specified SQL statement.
        
        Args:
        
        * s (str): A string containing the sql query
        * v (list): A vector containing any parametrized arguments of the query
        
        Returns:
            None
        """
        self.cur.execute(s,v)
    
    def commit(self):
        """
        Commits changes to the database.
        
        Args:
            None
            
        Returns:
            None
        """
        self.cnx.commit()
        
    def close(self):
        """
        Closses the connection
        
        Args:
            None
            
        Returns:
            None
        """
        self.cur.close()
        self.cnx.close()

    def quickSqlRead(self,s,v,withHeaders=False):
        """
        Opens a connection, executes the specified SQL statement, retrieves the data and closes the connection.
        
        Args:
        
        * s (str): A string containing the sql query
        * v (list): A vector containing any parametrized arguments of the query
        * withHeaders (bool): If true returns also the table headers
        
        Returns:
            A list of lists with the data of the table resulting from the query.
        """
        self.conn()
        
        
        self.cur.execute(s,v)
        headers = [desc[0] for desc in self.cur.description]
        data = self.cur.fetchall()
        self.close()
        
        if withHeaders:
            return data, headers
        return data
        
        
    def quickSqlWrite(self,s,v):
        """
        Opens a connection, executes the specified SQL statement, commits the changes and closes the connection.
        
        Args:
        
        * s (str): A string containing the sql query
        * v (list): A vector containing any parametrized arguments of the query
        
        Returns:
            None
        """
        self.conn()
        self.execute(s,v)
        self.commit()
        self.close() 