import requests
import requests.exceptions
from pathlib import Path
from json import JSONDecodeError
import logging
from time import sleep
from dateutil.parser import isoparse

logging.basicConfig(
    level=logging.INFO
)

STOPS = [
    "490006220N",
    "490006220S",
]



def get_bus_data(stop_number):
    arrivals = []

    url = f"https://api.tfl.gov.uk/StopPoint/{stop_number}/Arrivals"

    resp = requests.get(url)
    data = resp.json()
    for row in data:
        expected_arrival = isoparse(row['expectedArrival'])
        timestamp = isoparse(row["timestamp"])
        time_to_arrival = round((expected_arrival - timestamp).seconds / 60)

        station_name = row['stationName']
        line_name = row['lineName']
        destination_name = row['destinationName']
        towards = row['towards']

        arrivals.append([line_name, station_name, destination_name, towards, expected_arrival.strftime("%H:%M%p"), time_to_arrival])

    arrivals.sort(key=lambda x: x[5])

    return arrivals


def format_arrival(data):
    bus_info = data[0]
    line_name, station_name, destination_name, towards, arrival_time, time_to_arrival = bus_info
    return f"{line_name} to {destination_name} via {towards} - {time_to_arrival}m"

if __name__ == "__main__":
    bus_stop = "490006220S"


    while True:
        try:
            for bus_stop in STOPS:
                data = get_bus_data(bus_stop)
                print(format_arrival(data))
        except requests.exceptions.ConnectionError:
            logging.exception("Error connecting to API")
        except TimeoutError:
            logging.exception("API didn't return any data in a reasonable time")
        except requests.exceptions.ReadTimeout:
            logging.exception("API didn't return any data in a reasonable time")
        except JSONDecodeError:
            logging.exception("Bad data returned by API")

        sleep(120)