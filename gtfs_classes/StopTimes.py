import os
import pandas as pd

#from .Logger import FastTripsLogger

class StopTimes(object):
    
    """
    Stop Times
    """
    columns = ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence']
    
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS stop_times.txt. 
        """
        #: Trips_stop_times DataFrame
        
        self.data_frame = pd.DataFrame(data, columns = self.columns)
        