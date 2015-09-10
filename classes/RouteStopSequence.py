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

class RouteStopSequence(object):
    """
    Route Stop Sequence class. Includes a read/write Pandas DataFrame to store attributes for the stops of
    an individual route.
    """
    
    def __init__(self, StopSequence, shape_id):
        """
        To Do....
        """
        #: Trips_stop_times DataFrame
        #columns = ['route_id', 'order', 'stop_id', 'segment_time', 'cumulative_time']
        self.data_frame = StopSequence.data_frame.loc[(StopSequence.data_frame.shape_id == shape_id)]
        self.data_frame = self.data_frame.sort(['order'])
        

    