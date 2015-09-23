import os
import pandas as pd

class Routes(object):
    
    """
    Routes. 
    """
    columns = ['route_id', 'route_short_name', 'route_long_name', 'route_desc', 'route_type'] 
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS routes.txt. 
        """
        #: Trips_stop_times DataFrame
        
        self.data_frame = pd.DataFrame(data, columns = self.columns)
    
