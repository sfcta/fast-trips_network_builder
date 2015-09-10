
import inro.emme.matrix as ematrix
import inro.emme.database.matrix
import inro.emme.database.emmebank as _eb



def get_emme_troutes(emme_network):
    route_list = []
    
    for route in emme_network.transit_lines():
        #print 'here'
        #print route.data3
        route_list.append({'shape_id' : route.id, 'route_id' : route.id, 'mode' : route.mode.id, 'vehicle_id' : route.vehicle, 'headway' : route.headway, 'description' : route.description, 'operator' : route.data3})
        #print route.description
    
    return route_list





def get_emme_stop_sequence2(emme_network, time_field_name):
    
    
    record_list = []
   
#loop through the segments of each route
    for route in emme_network.transit_lines():
        time = 0
        order = 1
        
        for segment in route.segments():
            last_segment_number = max(enumerate(route.segments()))[1].number
            segment_time = calc_transit_time(segment)
            # a one segment line (ferry):
            fields = ['id', 'shape_id', 'route_id', 'order', 'stop_id', time_field_name]
            if segment.number == 0 and last_segment_number == 0:
                id = str(route.id) + "_" + str(order)
                record = [id, route.id, route.id, order, int(segment.i_node.id), 0]
                record_list.append(dict(zip(fields, record)))
                order = order + 1
                id = str(route.id) + "_" + str(order)
                record = [id, route.id, route.id, order, int(segment.j_node.id), segment_time]
                record_list.append(dict(zip(fields, record)))
                
            elif segment.number == 0:
                id = str(route.id) + "_" + str(order)
                record = [id, route.id, route.id, order, int(segment.i_node.id), 0]
                record_list.append(dict(zip(fields, record)))
                time =  time + segment_time
                order = order + 1

            elif segment.number == last_segment_number:
            #last stop, need time of last segment
                time = time + segment_time
                id = str(route.id) + "_" + str(order)
                record = [id, route.id, route.id, order, int(segment.j_node.id), time]
                record_list.append(dict(zip(fields, record)))

            else:
                if segment.allow_alightings:
                    #Its a stop
                    id = str(route.id) + "_" + str(order)
                    record = [id, route.id, route.id, order, int(segment.i_node.id), time]
                    record_list.append(dict(zip(fields, record)))
                    time =  segment_time
                    order = order + 1
                else:
                    #not a stop
                    time =  time + segment_time

    return record_list


def calc_transit_time(transit_segment):
    '''Returns the transit time for a passed in segment using the same factors we use for static assignment. The key here is that we are not
       including dwell time. Dwell time will be added when creating the actual schedule- the difference between arrival time and departure time
       in stop_times is where dwell time is handled. '''
    
    if transit_segment.transit_time_func == 4:
        transit_time = transit_segment.link.length * (60 / transit_segment.link.data2)
    
    elif transit_segment.transit_time_func == 5:
        transit_time = transit_segment.link.data2

    # Weave links- do not get a time
    elif transit_segment.link.data2 == 0:
        transit_time = 0
    
    elif transit_segment.transit_time_func == 11:
        if transit_segment.link.auto_time <= 0:
            print transit_segment.link.auto_time
            transit_time = 1.037034 * (transit_segment.link.length * (60 / transit_segment.link.data2))
        else:
            transit_time = min(1.037034 * transit_segment.link.auto_time, transit_segment.link.length * 12)

    elif transit_segment.transit_time_func == 12:
        if transit_segment.link.auto_time <= 0:
            transit_time = 1.285566 * (transit_segment.link.length * (60 / transit_segment.link.data2))
        else:
            transit_time = min(1.285566 * transit_segment.link.auto_time, transit_segment.link.length * 12)

    elif transit_segment.transit_time_func == 13:
        if transit_segment.link.auto_time <= 0:
            transit_time = 1.265774 * (transit_segment.link.length * (60 / transit_segment.link.data2))
        else:
            transit_time = min(1.265774 * transit_segment.link.auto_time, transit_segment.link.length * 12)

    elif transit_segment.transit_time_func == 14:
        if transit_segment.link.auto_time <= 0:
            transit_time = 1.00584 * (transit_segment.link.length * (60 / transit_segment.link.data2))
        else:
            transit_time = 1.00584 * transit_segment.link.auto_time

    elif transit_segment.transit_time_func == 15:
        if transit_segment.link.auto_time <= 0:
            transit_time = 1.037034 * (transit_segment.link.length * (60 / transit_segment.link.data2))
        else:
            transit_time = min(1.037034 * transit_segment.link.auto_time, transit_segment.link.length * 12)

    elif transit_segment.transit_time_func == 16:
        if transit_segment.link.auto_time <= 0:
            transit_time = 1.0928 * (transit_segment.link.length * (60 / transit_segment.link.data2))
        else:
            transit_time = min(1.0928 * transit_segment.link.auto_time, transit_segment.link.length * 12)

    else:
        raise ValueError('Transit ID ' + str(transit_segment.line) + ' and segment number ' + str(transit_segment.number) + 'does not have a valid TTF')
    
    
    if transit_time < 0:
        print transit_segment.transit_time_func
        print transit_segment.link.length
        print transit_segment.link.auto_time
        print transit_segment.link.auto_volume
        print transit_segment.transit_time
        raise ValueError('Transit ID ' + str(transit_segment.line) + ' and segment number ' + str(transit_segment.number) + 'has a speed 0 or lower')
    
    return transit_time



   

      

    
   