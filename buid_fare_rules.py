import emme_network_functions
import inro.emme.matrix as ematrix
import inro.emme.database.matrix
import inro.emme.database.emmebank as _eb
import numpy as np
from TransitRoutes import *
from StopSequence import *
from FareRules import *
from TransitRoute import *
import itertools
from itertools import groupby

global df_fares 
global df_stops_zones

def get_fare_id(operator, origin, destination):
    '''Returns fare_id from df_fares using origin, destination, operator'''
    
    row = df_fares.loc[(df_fares.operator == operator) & (df_fares.origin_zone == origin) & (df_fares.destination_zone == destination)]
    
    return row['fare_id'].iloc[0]

def get_zone_combos(list_of_zones, mode):
    '''Returns a list of tuples containing the feasible zone combos from a list of zones. The zone list must be in
       sequence- the zones encountered along the path'''

    # Check to see if only one zone for entire route:
    if len(set(list_of_zones)) <=1:
        return[(list_of_zones[0], list_of_zones[0])]
    
    # Ferries- only want origin, destination combo. 
    elif mode == 'f':
        return[(list_of_zones[0], list_of_zones[1])]
    
    else:
        # Creates a list of tuples of possible zone pairs for a sequence of zones.  
        zone_combos = []
        x = 0
        for zone in list_of_zones:
            for i in range(x, len(list_of_zones)):
                combo = (zone, list_of_zones[i])
                zone_combos.append(combo)
            x = x + 1
        
        return list(set(zone_combos))

def get_zone_combos_contains_id(list_of_zones):
    '''Not fully implemented but contains the logic to be used when using the list_of_zones convention in fare_rules.txt'''
    
    # Check to see if only one zone for entire route:
    if len(set(list_of_zones)) <=1:
        
        return[(list_of_zones[0], list_of_zones[0])]
    
    else:
        # Creates a list of tuples of possible zone pairs for a sequence of zones.  
        zone_combos = []
        x = 0
        for zone in list_of_zones:
            combos = []
            for i in range(x, len(list_of_zones)):
                combos.append(list_of_zones[i])
                zone_combos.append(tuple(combos))  
            x = x + 1
        
        return list(set(zone_combos))
                   
def get_zones_from_stops(list_of_stops, df_stops_zones):
    '''Returns a list of zones using list_of_stops and the stop_zone look up, df_stops_zones'''

    df = pd.DataFrame(np.asarray(list_of_stops),index=None,columns=['NODE_ID'])
    df = df.merge(df_stops_zones, 'left', left_on = ["NODE_ID"], right_on = ["ID"])
    zone_list = df['ZoneID'].tolist()
    
    return zone_list
    

def populate_fare_rule(zone_pairs, df_fare_rules, route):
    '''Updates dataframe on instance of Fare_Rules with all possible rules for a given route'''

    for pair in zone_pairs:
        origin = pair[0]
        destination = pair[1]
        print route.route_id
        print origin, destination
        fare_id = get_fare_id(route.operator, origin, destination)
        print fare_id
        df_fare_rules.loc[len(df_fare_rules)] = [fare_id, route.route_id, origin, destination, 0]

def test_fare_rules(route_stops, df_fare_rules, route_id):
    """
       This is a unit test that checks every route to see if all feasible stop combinations have valid records in fare_rules. 
    """
    x = 0
    zones = get_zones_from_stops(route_stops)
    for o_zone in zones:
        for i in range(x+1, len(zones)):
            d_zone = zones[i]
            row = df_fare_rules.loc[(df_fare_rules.route_id == route_id) & (df_fare_rules.origin_id == o_zone) & (df_fare_rules.destination_id == d_zone)]
            x = x + 1
            return len(row)
            
         
# Inputs:
bank_path = r'D:\TransportationFutures2010\Banks\7to8\emmebank'
path = 'X:/DSA/fastrips/Fares/'
df_fares = pd.DataFrame.from_csv(path + 'fare_id.csv', index_col=False)
df_stops_zones = pd.DataFrame.from_csv(path + 'stop_zones.csv', index_col=False)

# Get emme network data to populate TransitRoutes & Stop_Sequence classes. 
with _eb.Emmebank(bank_path) as emmebank:
    
    current_scenario = emmebank.scenario(1002)
    network = current_scenario.get_network()
    #get a list of network elments to create StopSequence and TransitRoute objects:
    list_of_stop_sequence = emme_network_functions.get_emme_stop_sequence(network)
    #stop_sequence = StopSequence(emme_network_functions.get_emme_stop_sequence(network))
    list_of_route_attributes = emme_network_functions.get_emme_troutes(network)
    
# Instantiate TransitRoute, StopSequence, FareRules objects. Here we have left emme dependency:
transit_routes = TransitRoutes(list_of_route_attributes)
stop_sequence = StopSequence(list_of_stop_sequence)
fare_rules = FareRules()

# Get a list of uniques routes:
route_list = sorted(list(set(transit_routes.data_frame['route_id'].tolist())))

# Loop through each route
for route_id in route_list:

    # Instantiate a TransitRoute Object, makes it easier to get route attributes
    route = TransitRoute(transit_routes, route_id)
    
    # Get the segs for this route:
    df_route_stop_seq = stop_sequence.data_frame.loc[(stop_sequence.data_frame.route_id == route_id)]
    
    # Get the zones
    zone_list = get_zones_from_stops(df_route_stop_seq['stop_id'].tolist(), df_stops_zones)
    
    # Remove duplicates in sequence. [1,2,2,1] becomes [1,2,1]
    zone_list = [x[0] for x in groupby(zone_list)]
       
    # Get zone combos. Note: mode 'f' for ferry gets special treatment for PSRC. See function def.
    zone_combos = get_zone_combos(zone_list, route.mode)
    
    # Return instance of fare_rules with populated dataframe
    populate_fare_rule(zone_combos, fare_rules.data_frame, route)

















