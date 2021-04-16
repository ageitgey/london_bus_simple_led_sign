import requests
import requests.exceptions
from json import JSONDecodeError
import logging
from time import sleep
from dateutil.parser import isoparse
from samplebase import SampleBase
from rgbmatrix import graphics
import time


class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)

    def run(self):
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.font = graphics.Font()
        self.font.LoadFont("london_bus.bdf")

        pos = self.offscreen_canvas.width

        while True:
            try:
                all_busses = []
                for bus_stop in STOPS:
                    arrivals = get_bus_data(bus_stop)
                    print(arrivals)
                    all_busses += arrivals
                    
                next_line = 1
                for tick in range(23):
                    self.offscreen_canvas.Clear()
                    all_busses.sort(key=lambda x: x[-1])
                                            
                    if len(arrivals) > 0:
                        formatted_text = format_arrival(0, arrivals[0])
                        self.draw_text(formatted_text, 0)

                    if next_line < len(arrivals):
                        formatted_text = format_arrival(0, arrivals[next_line])
                        self.draw_text(formatted_text, 1)

                    if len(all_busses) == 0:
                        self.draw_text("No service", 0)

                    if next_line + 1 >= len(arrivals):
                        next_line = 1
                    else:
                        next_line += 1

                    self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
                    time.sleep(2)

            except requests.exceptions.ConnectionError:
                logging.exception("Error connecting to API")
            except TimeoutError:
                logging.exception("API didn't return any data in a reasonable time")
            except requests.exceptions.ReadTimeout:
                logging.exception("API didn't return any data in a reasonable time")
            except JSONDecodeError:
                logging.exception("Bad data returned by API")


    def draw_text(self, text, line):
        textColor = graphics.Color(255, 155, 0)
        graphics.DrawText(self.offscreen_canvas, self.font, 0, 7 + (8 * line), textColor, text)




logging.basicConfig(
    level=logging.INFO
)

STOPS = [
    "490006220N",
    "490006220S",
    # "490000248G",
    # "490013511C",

]



def get_bus_data(stop_number):
    arrivals = []

    url = f"https://api.tfl.gov.uk/StopPoint/{stop_number}/Arrivals"

    resp = requests.get(url)
    data = resp.json()
    for row in data:
        print(row)
        expected_arrival = isoparse(row['expectedArrival'])
        timestamp = isoparse(row["timestamp"].split(".")[0] + "Z")
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

    full_destination = f"{destination_name} via {towards}"

    if time_to_arrival > 1:
        arrival_remaining = f"{time_to_arrival}m".rjust(3)
    else:
        arrival_remaining = f"due".rjust(3)

    destination_name = destination_name[0:8]
    return f"{line_name.rjust(3)} {destination_name.ljust(8)} {arrival_remaining}"

if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
        

