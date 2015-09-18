import os
import pandas as pd

class Trips(object):
    
    """
    Trips. 
    """
    columns = ['route_id', 'service_id', 'trip_id'] 
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS stop_times.txt. 
        """
        #: Trips_stop_times DataFrame
        
        self.data_frame = pd.DataFrame(data, columns = self.columns)