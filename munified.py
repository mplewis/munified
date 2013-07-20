#!/usr/bin/python

import requests
from bs4 import BeautifulSoup

TRANSIT_AGENCY = 'sf-muni'
STOPS = [
    {'route_id': '33', 'distance_in_mins': 3,  'stop_id': '3327', 'direction': 'inbound',  'desc': '33 Inbound to the Richmond District'},
    {'route_id': '33', 'distance_in_mins': 3,  'stop_id': '3328', 'direction': 'outbound', 'desc': '33 Outbound to General Hospital'},
    {'route_id': 'F',  'distance_in_mins': 10, 'stop_id': '3311', 'direction': 'outbound', 'desc': 'F Outbound to Fisherman\'s Wharf'},
    {'route_id': 'KT', 'distance_in_mins': 10, 'stop_id': '5728', 'direction': 'inbound',  'desc': 'T Inbound to Sunnydale & Bayshore'},
    {'route_id': 'L',  'distance_in_mins': 10, 'stop_id': '5728', 'direction': 'inbound',  'desc': 'L Inbound to Embarcadero Station'},
    {'route_id': 'M',  'distance_in_mins': 10, 'stop_id': '5728', 'direction': 'inbound',  'desc': 'M Inbound to Embarcadero Station'},
    {'route_id': 'KT', 'distance_in_mins': 10, 'stop_id': '6991', 'direction': 'outbound', 'desc': 'K Outbound to Balboa Park'},
    {'route_id': 'L',  'distance_in_mins': 10, 'stop_id': '6991', 'direction': 'outbound', 'desc': 'L Outbound to SF Zoo'},
    {'route_id': 'M',  'distance_in_mins': 10, 'stop_id': '6991', 'direction': 'outbound', 'desc': 'M Outbound to Balboa Park'}
]

class StatusCodeError(requests.exceptions.RequestException):
    pass

def retrieve_stop(stops, route_id, stop_id):
    for stop in stops:
        if stop['route_id'] == route_id and stop['stop_id'] == stop_id:
            return stop
    raise KeyError

def fetch_predictions(stops):
    trains = []
    url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=predictionsForMultiStops&a=%s' % TRANSIT_AGENCY
    for stop in stops:
        stop_url = '&stops=%s|%s' % (stop['route_id'], stop['stop_id'])
        url += stop_url
    result = requests.get(url)
    if result.status_code != 200:
        raise StatusCodeError
    xml = result.content
    parser = BeautifulSoup(xml)
    route_predictions = parser.find('body').find_all('predictions')
    all_predictions_data = []
    for prediction_set in route_predictions:
        route_id = prediction_set.get('routetag')
        stop_id = prediction_set.get('stoptag')
        next_departures_xml = prediction_set.find_all('prediction')
        all_departure_mins = []
        for departure_xml in next_departures_xml:
            all_departure_mins.append(int(departure_xml.get('minutes')))
        all_predictions_data.append({'route_id': route_id,
                                     'stop_id': stop_id,
                                     'next_departures': all_departure_mins})
    return all_predictions_data

def merge_predictions(stops, predictions):
    merged_stops = []
    for prediction in predictions:
        try:
            relevant_stop = retrieve_stop(STOPS, prediction['route_id'], prediction['stop_id']).copy()
        except KeyError:
            continue
        time_to_walk = relevant_stop['distance_in_mins']
        possible_departure_times = []
        for departure_time in prediction['next_departures']:
            departure_time_diff = departure_time - time_to_walk
            if departure_time_diff >= 0:
                possible_departure_times.append(departure_time_diff)
        relevant_stop['possible_departure_times'] = possible_departure_times
        merged_stops.append(relevant_stop)
    return merged_stops

if __name__ == '__main__':
    from pprint import pprint
    predictions = fetch_predictions(STOPS)
    stops_with_predictions = merge_predictions(STOPS, predictions)
    pprint(stops_with_predictions)