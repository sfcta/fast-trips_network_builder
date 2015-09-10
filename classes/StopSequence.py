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

class StopSequence(object):
    """
    Stop Sequence class. Includes a read/write Pandas DataFrame to store attributes for the stops of
    each route.
    """
    
    def __init__(self, data, columns):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds the attributes for 
        individual stops in a Route. This is much faster than adding one record at a time to the DataFrame. 
        
        Field Description:
        'route_id' : 
        'order' : the order of the stop along the path and is 0-based
        'segment_time' : time in decimal minutes to traverse the links from the previous stop.
        'cumulative_time' : time in decimal minutes to traverse all links to reach current stop.  

        example:
        data = [
        {'route_id' : 21, 'order' = 0, 'stop_id' = 10, 'segment_time': 0, cumulative_time: 0},
        {'route_id' : 21, 'order' = 1, 'stop_id' = 13, 'segment_time': .80, cumulative_time: 0},
        {'route_id' : 21, 'order' = 2, 'stop_id' = 18, 'segment_time': .90, cumulative_time : 1.70}
        ]
        """
        #: Trips_stop_times DataFrame
        #columns = ['route_id', 'order', 'stop_id', 'segment_time', 'cumulative_time']
        self.data_frame = pd.DataFrame(data, columns = columns)
        self.data_frame = self.data_frame.sort(['shape_id', 'order'])
        self.stop_seq_by_route_df = None

    


        

   