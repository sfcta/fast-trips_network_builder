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

class FareRules:
    """
    Route class.  Documentation forthcoming.
    """

    #: File with routes.
    #: TODO document format
    
    def __init__(self):
        """
        Constructor from dictionary mapping attribute to value.
        """
        #: Trips_stop_times DataFrame
        columns = ['fare_id', 'route_id', 'origin_id', 'destination_id', 'contains_id']
        df = pd.DataFrame(columns=columns)
        self.data_frame = df
        

#test = FareRules()