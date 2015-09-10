__copyright__ = "Copyright 2015 Contributing Entities"
__license__   = """
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import os
import pandas as pd

#from .Logger import FastTripsLogger

class TransitRoute(object):
    """
    Route class. Read/write attributes for a specific transit route.
    """
    
    def __init__(self, TransitRoutes, shape_id):
        """
        Constructor from instance of TransitRoutes and a valid shape_id to retrieve record 
        from TransitRoutes.DataFrame.
        """

        self.transit_route_record = TransitRoutes.data_frame.loc[(TransitRoutes.data_frame.shape_id == shape_id)]
        if len(self.transit_route_record) == 0:
            raise ValueError('shape_id not found in TransitRoutes')
        self.operator = int(self.transit_route_record.iloc[0]['operator'])
        self.shape_id = shape_id
        self.route_id = shape_id
        self.mode = self.transit_route_record.iloc[0]['mode']
        self.headway = self.transit_route_record.iloc[0]['headway']

   

        