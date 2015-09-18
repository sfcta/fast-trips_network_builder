import os
import pandas as pd

class FareRules(object):
    """
    Fare Rules.
    """
    columns = ['fare_id', 'route_id', 'origin_id', 'destination_id', 'contains_id']
    
    def __init__(self):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS fare_rules.txt. 
        """
        #: Trips_stop_times DataFrame
        
        df = pd.DataFrame(columns=self.columns)
        self.data_frame = df
       
