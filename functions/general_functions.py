import inro.emme.matrix as ematrix
import inro.emme.database.matrix
import inro.emme.database.emmebank as _eb
import numpy as np
import time
from config.input_configuration import *
import itertools
from itertools import groupby
from gtfs_classes.Trips import *
from gtfs_classes.StopTimes import *
from gtfs_classes.FareRules import *
from gtfs_classes.Shapes import *
from pyproj import Proj, transform
import random 


def get_emme_stop_sequence(emme_transit_line):
    
    record_list = []
# Loop through the segments of each route
    for segment in emme_transit_line.segments():
            last_segment_number = max(enumerate(emme_transit_line.segments()))[1].number
            #segment_time = calc_transit_time(segment)
            
            # A one segment line (ferry):
            if segment.number == 0 and last_segment_number == 0:
                record_list.append(int(segment.i_node.id))
                record_list.append(int(segment.j_node.id))
                
            elif segment.number == 0:
                record_list.append(int(segment.i_node.id))

            elif segment.number == last_segment_number:
            # Last stop, need time of last segment
                if segment.allow_alightings:
                    record_list.append(int(segment.i_node.id))
                record_list.append(int(segment.j_node.id))

            else:
                if segment.allow_alightings:
                    record_list.append(int(segment.i_node.id))

    return record_list


def reproject_to_wgs84(longitude, latitude, ESPG = "+init=EPSG:2926", conversion = 0.3048006096012192):
    '''Converts the passed in coordinates from their native projection (default is state plane WA North-EPSG:2926)
       to wgs84. Returns a two item tuple containing the longitude (x) and latitude (y) in wgs84. Coordinates
       must be in meters hence the default conversion factor- PSRC's are in state plane feet.  
    '''
    # Remember long is x and lat is y!
    prj_wgs = Proj(init='epsg:4326')
    prj_sp = Proj(ESPG)
    
    # Need to convert feet to meters:
    longitude = longitude * conversion
    latitude = latitude * conversion
    x, y = transform(prj_sp, prj_wgs, longitude, latitude)
    
    return x, y

def get_fare_id(operator, origin, destination):
    '''
    Returns fare_id from df_fares using origin, destination, operator
    '''
    
    row = df_fares.loc[(df_fares.operator == operator) & (df_fares.origin_zone == origin) & (df_fares.destination_zone == destination)]
    
    return row['fare_id'].iloc[0]

def get_zone_combos(list_of_zones, mode):
    '''
    Returns a list of tuples containing the feasible zone combos from a list of zones. The zone list must be in
    sequence- the zones encountered along the path
    '''

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

def get_pseudo_random_departure_time(time_period_start, headway, min_start_time = 0):
    '''
    Using a normal distribution, computes a pseudo random departure time in number of minutes based on a time window. The
    time window ranges from a default of 0 to half the headway. From this range, the mean and standard deviation are 
    calculated and then used as paramaters in the random.normalvariate function. This result is added to time_period_start, 
    and result is the departure time in number of minutes past midnight. The idea behind this methodology is that first 
    departures 1) should not all happen at the same time, 2) Indviudal routes should have a first departure time well less than 
    their headway so that their hourly frequencies are met at most stops, and 3) longer headways (less fequent service) should 
    have start times farther away from the begining of the time period compared to routes with more frequent service. Item 3
    is not guaranteed but highly probable.    
    '''
    # Assume max start time is half the headway for now:
    max_start_time = headway * .5
    start_time = max_start_time
    # Make sure start_time is < max_start_time
    while start_time >= max_start_time or start_time < 0:
        mean = (max_start_time + min_start_time)/2
        # Using 3 because 3 Standard deviatons should account for 99.7% of a population in a normal distribution. 
        sd = mean/3
        start_time = random.normalvariate(mean, sd)
    start_time = start_time + time_period_start 
    return start_time

def get_zone_combos_contains_id(list_of_zones):
    '''
    Not fully implemented but contains the logic to be used when using the list_of_zones convention in fare_rules.txt
    '''
    
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
    '''
    Returns a list of zones using list_of_stops and the stop_zone look up, df_stops_zones
    '''

    df = pd.DataFrame(np.asarray(list_of_stops),index=None,columns=['NODE_ID'])
    df = df.merge(df_stops_zones, 'left', left_on = ["NODE_ID"], right_on = ["ID"])
    zone_list = df['ZoneID'].tolist()
    
    return zone_list
    

def populate_fare_rule(zone_pairs, df_fare_rules, emme_transit_line, df_fares):
    '''
    Updates dataframe on instance of Fare_Rules with all possible rules for a given route
    '''

    for pair in zone_pairs:
        origin = pair[0]
        destination = pair[1]
        print emme_transit_line.id
        print origin, destination
        # .data3 refers to operator
        row = df_fares.loc[(df_fares.operator == emme_transit_line.data3) 
                           & (df_fares.origin_zone == origin) & (df_fares.destination_zone == destination)]
    
        fare_id = row['fare_id'].iloc[0]
        #fare_id = get_fare_id(emme_transit_line.data3, origin, destination)
        print fare_id
        df_fare_rules.loc[len(df_fare_rules)] = [fare_id, emme_transit_line.id, origin, destination, 0]

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

def generate_unique_id(seq):
    """
    Generator that yields a number from a passed in sequence
    """
    
    for x in seq:
        yield x
  
def dec_mins_to_HHMMSS(time_in_decimal_minutes):
    """ 
    Convertes Decimal minutes to HHMMSS
    """
    return time.strftime("%H:%M:%S", time.gmtime(time_in_decimal_minutes * 60))

def get_transit_line_shape(transit_line):
    """
    Returns a list of dictionaries that hold the records for shape.txt for an individual transit line. 
    Coordinates (for PSRC) are stored in state plane so this includes a call to the reproject_to_wgs84 
    function.  
    """
    x = 1
    shape_list = []
    for segment in transit_line.segments():
        # Get all vertices except for the last one (JNode):
        for coord in segment.link.shape[:-1]:
            # Remember, X=long and Y=lat
            wgs84tuple = reproject_to_wgs84(coord[0], coord[1])
            shape_record = [transit_line.shape_id, wgs84tuple[1], wgs84tuple[0], x]
            shape_list.append(dict(zip(Shapes.columns, shape_record)))
            x = x + 1
    
            # Get the JNode of the last link
    coord = segment.link.shape[-1] 
    wgs84tuple = reproject_to_wgs84(coord[0], coord[1])
    shape_record = [transit_line.shape_id, wgs84tuple[1], wgs84tuple[0], x]
    #shape_record = [transit_line.shape_id, coord[1], coord[0], x]
    shape_list.append(dict(zip(Shapes.columns, shape_record)))
    return shape_list

def schedule_route(start_time, end_time, transit_line, trip_id_generator, stop_times_list, trips_list, network_dictionary):
    '''
    Determines all the departure times for a given route, for a given time window and then builds a schedule using stop to stop travel times. 
    Creates a record for each trip and all stop_times for each trip, which are stored in dictionaries and appended to stops_times_list and trips_list.
    '''
 
    # Get first stop departure times. Assuming all first trips leave at start time for the moment. Will implment randomized departure times later. 
    random_start_time = get_pseudo_random_departure_time(start_time, transit_line.headway)
    print random_start_time
    first_stop_departure_times = range(int(random_start_time), end_time, int(transit_line.headway))

    for first_departure in first_stop_departure_times:
       
       # Create a record for trips (GTFS File)
       trip_id = trip_id_generator.next()
       
       # To Do: need a route_id attribute- using transit_line.id for now
       # Using 1 for service_id
       trips_record = [transit_line.id, 1, trip_id, transit_line.shape_id]
       trips_list.append(dict(zip(Trips.columns, trips_record)))

       departure_time = first_departure
       #print departure_time
       order = 1
       for segment in transit_line.segments():
           last_segment_number = max(enumerate(transit_line.segments()))[1].number
           tod = highway_assignment_tod[int(departure_time)/60]
           # Get segment time in decmial minutes
           segment_time = calc_transit_time(segment.link.i_node.id, segment.link.j_node.id, tod, segment.transit_time_func, network_dictionary)
           
           # A one segment line (ferry):
           if segment.number == 0 and last_segment_number == 0:
                
                stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time), dec_mins_to_HHMMSS(departure_time), 
                                     int(segment.i_node.id), order]
                stop_times_list.append(dict(zip(StopTimes.columns, stop_times_record)))
                
                stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time + segment_time), 
                                     dec_mins_to_HHMMSS(departure_time + segment_time), int(segment.j_node.id), order + 1]
                stop_times_list.append(dict(zip(StopTimes.columns, stop_times_record)))
                
           # First Stop:
           elif segment.number == 0:
                stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time), 
                                     dec_mins_to_HHMMSS(departure_time), int(segment.i_node.id), order]
                stop_times_list.append(dict(zip(StopTimes.columns, stop_times_record)))
                
                # Update departure time for next stop
                departure_time =  departure_time + segment_time
                order = order + 1
           
           elif segment.number == last_segment_number:
            # Last stop, need time of last segment
                # Check to see if there is a stop on the I-node:
                if segment.allow_alightings:
                    stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time), 
                                        dec_mins_to_HHMMSS(departure_time + DWELL_TIME), int(segment.i_node.id), order]
                    stop_times_list.append(dict(zip(StopTimes.columns, stop_times_record)))
                    order = order + 1
                
                # Add final stop, update segment time
                departure_time = departure_time + segment_time + DWELL_TIME
                stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time), 
                                     dec_mins_to_HHMMSS(departure_time), int(segment.j_node.id), order]
                stop_times_list.append(dict(zip(StopTimes.columns, stop_times_record)))
                
           
           else:
                if segment.allow_alightings:
                    # Its a stop
                    stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time), 
                                         dec_mins_to_HHMMSS(departure_time + DWELL_TIME), int(segment.i_node.id), order]
                    stop_times_list.append(dict(zip(StopTimes.columns, stop_times_record)))
                    departure_time = departure_time + segment_time + DWELL_TIME
                    order = order + 1
                else:
                    # Not a stop, add time for this link
                    departure_time = departure_time + segment_time

def calc_transit_time(link_i, link_j, tod, ttf, network_dictionary):
    '''
    Returns the transit time for a passed in segment in decimal minutes using the same factors we use for static assignment. ttf is a transit network input and is based
    on facility type and when the last stop was made.
    '''
    
    network = network_dictionary[tod]
    
    link = network.link(link_i, link_j)
    
    # Check to see if link exists:
    if not link:
        print "no link"
        # Get it from fall back dict:
        new_tod = fall_back_dict[tod]
        network = network_dictionary[new_tod]
        link = network.link(link_i, link_j)
    
    # Factors below would be stored in a config file. 
    # Bus Only, assume max speed
    if ttf == 4:
        transit_time = link.length * (60 / link.data2)
    
    # Rail time is stored in data2
    elif ttf == 5:
        transit_time = link.data2

    # Weave links- do not get a time
    elif link.data2 == 0:
        transit_time = 0
    
    # Local
    elif ttf == 11:
        if link.auto_time <= 0:
            transit_time = 1.037034 * (link.length * (60 / link.data2))
        else:
            transit_time = min(1.037034 * link.auto_time, link.length * 12)
    
    # Local, recent stop
    elif ttf == 12:
        if link.auto_time <= 0:
            transit_time = 1.285566 * (link.length * (60 / link.data2))
        else:
            transit_time = min(1.285566 * link.auto_time, link.length * 12)
    
    # Facility type is highway and last stop is greater than 2640 feet behind
    elif ttf == 13:
        if link.auto_time <= 0:
            transit_time = 1.265774 * (link.length * (60 / link.data2))
        else:
            transit_time = min(1.265774 * link.auto_time, link.length * 12)
    
    # Last stop is greater than 7920 feet behind
    elif ttf == 14:
        if link.auto_time <= 0:
            transit_time = 1.00584 * (link.length * (60 / link.data2))
        else:
            transit_time = 1.00584 * link.auto_time

    else:
        raise ValueError('Transit ID ' + str(transit_segment.line) + ' and segment number ' + str(transit_segment.number) + 'does not have a valid TTF')
    
    if transit_time < 0:
        # Speed's of 0 are allowed on weave links, but let's make sure there are no negative values. 
        raise ValueError('Transit ID ' + str(transit_segment.line) + ' and segment number ' + str(transit_segment.number) + 'has a speed lower than 0')
    
    return transit_time