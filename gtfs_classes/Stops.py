import os
import pandas as pd

class Stops(object):
    
    """
    Stops. 
    """
    columns = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'zone_id'] 
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS stop.txt. 
        """
        #: Trips_stop_times DataFrame
        
        self.data_frame = pd.DataFrame(data, columns = self.columns)