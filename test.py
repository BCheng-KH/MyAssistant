# import speech_recognition as sr
# import json

# print(sr.Microphone.list_microphone_names())

# print(json.loads(""))

import time, datetime, json, googlemaps, os, calendar
print(calendar.day_name[datetime.datetime.now().weekday()])
# from dotenv import load_dotenv
# load_dotenv(override=True)
# now = datetime.datetime.now() + datetime.timedelta(hours=4.7)
# gmaps = googlemaps.Client(key=os.environ["GOOGLE_MAPS_API_KEY"])
# # directions_result = gmaps.directions("xxx",
# #                                      "xxx",
# #                                      mode="transit",
# #                                      departure_time=now,
# #                                      transit_mode="bus")
# # print(json.dumps(directions_result, indent=4))

# def next_bus_to_campus(departure = datetime.datetime.now()):
#     directions_result = gmaps.directions("xxx",
#                                      "xxx",
#                                      mode="transit",
#                                      departure_time=departure,
#                                      transit_mode="bus")
#     bus_step = [step for step in directions_result[0]["legs"][0]["steps"] if step["travel_mode"] == "TRANSIT"]
#     bus_departure_time = bus_step[0]["transit_details"]["arrival_time"]["text"]
#     bus_line = bus_step[0]["transit_details"]["line"]["short_name"]
#     overall_departure_time = directions_result[0]["legs"][0]["departure_time"]["text"]
#     return overall_departure_time, bus_departure_time, bus_line
# print(next_bus_to_campus(now), now)

