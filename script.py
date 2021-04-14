import requests
import requests.exceptions
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
    "490000248G",
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


def format_arrival(i, bus_info):
    line_name, station_name, destination_name, towards, arrival_time, time_to_arrival = bus_info

    if  time_to_arrival > 1:
        arrival_remaining = f"{time_to_arrival}m".rjust(3)
    else:
        arrival_remaining = f"due".rjust(3)

    destination_name = towards[0:8]
    return f"{line_name.rjust(3)} {destination_name.ljust(8)} {arrival_remaining}"

# 16 x 2

if __name__ == "__main__":
    while True:
        try:
            all_busses = []
            for bus_stop in STOPS:
                arrivals = get_bus_data(bus_stop)
                if len(arrivals) > 0:
                    all_busses.append(arrivals[0])
                if len(arrivals) > 1:
                    all_busses.append(arrivals[1])
            for i, arrival in enumerate(all_busses):
                print(format_arrival(i + 1, arrival))
        except requests.exceptions.ConnectionError:
            logging.exception("Error connecting to API")
        except TimeoutError:
            logging.exception("API didn't return any data in a reasonable time")
        except requests.exceptions.ReadTimeout:
            logging.exception("API didn't return any data in a reasonable time")
        except JSONDecodeError:
            logging.exception("Bad data returned by API")

        sleep(60)