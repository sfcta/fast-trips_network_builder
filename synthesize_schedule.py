import sys
import os 
import inro.emme.matrix as ematrix
import inro.emme.database.matrix
import inro.emme.database.emmebank as _eb
import numpy as np
from classes.TransitRoutes import *
from classes.StopSequence import *
from gtfs_classes.FareRules import *
from classes.TransitRoute import *
from classes.RouteStopSequence import *
from gtfs_classes.StopTimesGTFS import *
from gtfs_classes.TripsGTFS import *
from emme_functions.emme_network_functions import *
import itertools
from itertools import groupby
from itertools import chain
from collections import defaultdict
import collections
import time 



transit_network_tod =  {'am' : ('6to7', '7to8', '8to9'), 'md' : ('9to10', '10to14', '14to15')} 

start_end_time_dict = {'am' : {'start_time' : 300, 'end_time' : 540}, 'md' : {'start_time' : 540, 'end_time' : 900}}

highway_assignment_tod = {'am' : {5: '6to7', 6: '6to7', 7: '7to8', 8: '8to9', 9: '8to9', 10: '8to9'}, 'md' : {9: '9to10', 10: '10to14', 11: 
               '10to14', 12: '10to14', 13: '10to14', 14: '14to15', 15: '14to15', 16: '14to15'}}

banks_path = 'R:/SoundCast/releases/TransportationFutures2010/Banks/'



def generate_trip_id(seq):
    for x in seq:
        yield x
  
def dec_mins_to_HHMMSS(time_in_decimal_minutes):
    """ Convertes Decimal minutes to HHMMSS"""
    return time.strftime("%H:%M:%S", time.gmtime(time_in_decimal_minutes * 60))
    
        
def schedule_route(start_time, end_time, StopSequence, TransitRoute, trip_id_generator, transit_network_tod, stop_times_list, trips_list):
    
    # Get first stop departure times. Assuming all first trips leave at start time for the moment. 
    first_stop_departure_times = range(start_time, end_time, int(TransitRoute.headway))

    # Fields for stop_times and trips. Only including required fields for now. 
    stop_times_fields = ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence']
    trips_fields = ['route_id', 'service_id', 'trip_id'] 
    
    # Get the stop sequence for the current route:
    route_stop_seq = RouteStopSequence(StopSequence, TransitRoute.shape_id)
   
    for first_departure in first_stop_departure_times:
       # Create a record for trips (GTFS File)
       trip_id = trip_id_generator.next()
       # To Do: figure out service_id
       trips_record = [TransitRoute.route_id, 0, trip_id]
       trips_list.append(dict(zip(trips_fields, trips_record)))

       departure_time = first_departure
       for row in route_stop_seq.data_frame.iterrows():
           # Get the time period by passing in hour to highway_assignment_tod dict:
           
           if row[1]['order'] == 1:
               # First departure/stop- arrival and departure are the same
               stop_times_record = [trip_id, dec_mins_to_HHMMSS(departure_time), dec_mins_to_HHMMSS(departure_time), row[1]['stop_id'], row[1]['order']]
               stop_times_list.append(dict(zip(stop_times_fields, stop_times_record)))
           else:
               # Get the right time period to get stop to stop travel time:
               tp = highway_assignment_tod[transit_network_tod][int(departure_time)/60]
               # Arrival time is the departure time of the last stop + plus travel time
               arrival_time = departure_time + row[1][tp]
               # Add a dwell time for now
               departure_time = arrival_time + .25
               # Create the record for this stop_times row
               stop_times_record = [trip_id, dec_mins_to_HHMMSS(arrival_time), dec_mins_to_HHMMSS(departure_time), row[1]['stop_id'], row[1]['order']]
               stop_times_list.append(dict(zip(stop_times_fields, stop_times_record)))
               
    return stop_times_list, trips_list
      
               
transit_routes_dict = {}
stop_seq_dict = {}
stop_times_list = []
trips_list = []
id_generator = generate_trip_id(range(1,999999))

for transit_network_tod, travel_tps in transit_network_tod.iteritems():
    # For PSRC, we use the same 'am' transit/roadway networks for 6to7, 7to8, 8to9 auto assignments. We use a 'md' network for 9-10, 10-14, 14-15.  
    # We are going to store stop sequence for all routes for each time period in the following list
    stop_seq_by_tp = []
    for time_period in travel_tps:
        with _eb.Emmebank(banks_path + time_period + '/emmebank') as emmebank:
            current_scenario = emmebank.scenario(1002)
            network = current_scenario.get_network()
            stop_seq_by_tp.append(get_emme_stop_sequence2(network, time_period))
    list_of_route_attributes = get_emme_troutes(network)
    transit_routes = TransitRoutes(list_of_route_attributes)
    #transit_routes_dict[transit_network_tod] = transit_routes
    # We now have a list of lists where each nested list contains dictionaries that are rows of stops for each route
    # for a particular time period. These all share the same transit network but travel times are different. 
    # Below we merge these into one list of dictionaries that have speed for each time period:
    #from this:
    #   [[{
            
    result = defaultdict(dict)
    
    row_list = []

    for c_dict in chain.from_iterable(stop_seq_by_tp):
        result[c_dict["id"]].update(c_dict)

    for k, v in result.iteritems():
        row_list.append(v)

    columns = row_list[0].keys()
    stop_sequence = StopSequence(row_list, columns)
    #stop_seq_dict[transit_network_tod] = stop_sequence

    for route in transit_routes.data_frame.iterrows():
        transit_route = TransitRoute(transit_routes, route[1]['shape_id'])
        start_time = start_end_time_dict[transit_network_tod]['start_time']
        end_time = start_end_time_dict[transit_network_tod]['end_time']
        schedule_route(start_time, end_time, stop_sequence, transit_route, id_generator, transit_network_tod, stop_times_list, trips_list)


stop_times = StopTimesGTFS(stop_times_list)
trips = TripsGTFS(trips_list)

#transit_route = TransitRoute(transit_routes_dict['am'], '0001')
#x = schedule_route(360, 540, stop_seq_dict['am'], transit_route, id_generator, transit_network_tod)
#fields = ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence']
#df = pd.DataFrame(x, columns = fields)