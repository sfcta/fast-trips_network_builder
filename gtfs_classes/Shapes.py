import os
import pandas as pd

#from .Logger import FastTripsLogger

class Shapes(object):
    
    """
    Shapes
    """
    columns = ['shape_id', 'shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence']
    
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS shapes.txt. 
        """
        #: Trips_stop_times DataFrame
        
        self.data_frame = pd.DataFrame(data, columns = self.columns)