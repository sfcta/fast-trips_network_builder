import sys
import os 
import inro.emme.matrix as ematrix
import inro.emme.database.matrix
import inro.emme.database.emmebank as _eb
import numpy as np
import pandas as pd
import itertools
from itertools import groupby
from itertools import chain
from collections import defaultdict
import collections
from config.input_configuration import *
from functions.general_functions import *
from gtfs_classes.FareRules import *
from gtfs_classes.Trips import *
from gtfs_classes.StopTimes import *

# Fare Files
df_fares = pd.DataFrame.from_csv('inputs/fares/fare_id.csv', index_col=False)
df_stops_zones = pd.DataFrame.from_csv('inputs/fares/stop_zones.csv', index_col=False)

# A place to store in-memory emme networks
network_dict = {}

def main():
    # Creat outputs dir if one does not exist
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    # Lists to hold stop_times and trips records
    stop_times_list = []
    trips_list = []
    fare_rules = FareRules()

    # Generates a unique ID 
    id_generator = generate_unique_id(range(1,999999))
    
    # Load all the networks into the network_dict
    for tod in highway_assignment_tod.itervalues():
        with _eb.Emmebank(banks_path + tod + '/emmebank') as emmebank:
            current_scenario = emmebank.scenario(1002)
            network = current_scenario.get_network()
            network_dict[tod] = network

    for my_dict in transit_network_tod.itervalues():
        # Get the am or md transit network: 
        transit_network = network_dict[my_dict['transit_bank']]
        
        # Schedule each route and create data structure (list of dictionaries) for trips and stop_times. 
        for transit_line in transit_network.transit_lines():
            
            ###### FARES ######
            # Get a list of ordered stops for this route
            list_of_stops = get_emme_stop_sequence(transit_line)
            
            # Get the zones
            zone_list = get_zones_from_stops(list_of_stops, df_stops_zones)
    
            # Remove duplicates in sequence. [1,2,2,1] becomes [1,2,1]
            zone_list = [x[0] for x in groupby(zone_list)]
       
            # Get zone combos. Note: mode 'f' for ferry gets special treatment for PSRC. See function def.
            zone_combos = get_zone_combos(zone_list, transit_line.mode.id)
    
            # Return instance of fare_rules with populated dataframe
            populate_fare_rule(zone_combos, fare_rules.data_frame, transit_line, df_fares)

            ###### Schedule ######
            schedule_route(my_dict['start_time'], my_dict['end_time'], transit_line, id_generator, stop_times_list, trips_list, network_dict)

    # Instantiate classes
    stop_times = StopTimes(stop_times_list)
    trips = Trips(trips_list)
    
    # Write out text files
    stop_times.data_frame.to_csv('outputs/stop_times.txt', index = False)
    trips.data_frame.to_csv('outputs/trips.txt', index = False)
    fare_rules.data_frame.to_csv('outputs/fare_rules.txt', index = False)

if __name__ == "__main__":
    main()