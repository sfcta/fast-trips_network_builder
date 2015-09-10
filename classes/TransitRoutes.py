__copyright__ = "Copyright 2015 Contributing Entities"
__license__   = """
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import os
import pandas as pd

#from .Logger import FastTripsLogger

class TransitRoutes(object):
    
    """
    Transit Routes class. Includes a read/write Pandas DataFrame to store attributes for each route. 
    """
    
    def __init__(self, data):
        '''
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds the attributes for an 
        individual Route. This is much faster than adding one record at a time to the DataFrame. 
        
        example:
        data = [
        {'shape_id' : 1', route_id' : 22, 'mode' = 'b', 'vehicle_id' = 5, 'description': '5 express to Seattle', 'headway' = 15, 'operator' =1},
        {'shape_id' : 2', 'route_id' : 22, 'mode' = 'b', 'vehicle_id' = 5, 'description': '5 express to 85th', 'headway' = 30, 'operator' = 1}
        ]
        '''
        #: Trips_stop_times DataFrame
        columns = ['shape_id', 'route_id', 'mode', 'vehicle_id', 'description', 'headway', 'operator']
        self.data_frame = pd.DataFrame(data, columns = columns)
        self.data_frame.sort(['shape_id'])