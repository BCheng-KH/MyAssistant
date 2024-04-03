import time, datetime, json, googlemaps, os
from dotenv import load_dotenv
load_dotenv(override=True)

gmaps = googlemaps.Client(key=os.environ["GOOGLE_MAPS_API_KEY"])
home=os.environ["HOME_ADDRESS"]
campus=os.environ["CAMPUS_ADDRESS"]

def load_notes():
    with open("Notes.json", "r") as f:
        notes = json.load(f)
    return notes

def save_notes(notes):
    with open("Notes.json", "w") as f:
        json.dump(notes, f)

def add_note(args):
    notes = load_notes()
    notes['last_index'] += 1
    notes['database'][str(notes['last_index'])] = {"name": args["name"], "text": args["text"]}
    save_notes(notes)
    return str(notes['last_index'])

def edit_note(args):
    id = args["id"]
    notes = load_notes()
    if "name" in args:
        notes['database'][str(id)]["name"] = args["name"]
    if "text" in args:
        notes['database'][str(id)]["text"] = args["text"]
    save_notes(notes)

def delete_note(id):
    notes = load_notes()
    del notes['database'][str(id)]
    save_notes(notes)

def next_bus_to_campus(departure=None, arrival=None):
    if departure:
        directions_result = gmaps.directions(campus,
                                     home,
                                     mode="transit",
                                     departure_time=departure,
                                     transit_mode="bus")
    elif arrival:
        directions_result = gmaps.directions(campus,
                                     home,
                                     mode="transit",
                                     arrival_time=arrival,
                                     transit_mode="bus")
    else:
        departure = datetime.datetime.now()
        directions_result = gmaps.directions(campus,
                                        home,
                                        mode="transit",
                                        departure_time=departure,
                                        transit_mode="bus")
    bus_step = [step for step in directions_result[0]["legs"][0]["steps"] if step["travel_mode"] == "TRANSIT"]
    bus_departure_time = bus_step[0]["transit_details"]["arrival_time"]["text"]
    bus_line = bus_step[0]["transit_details"]["line"]["short_name"]
    overall_departure_time = directions_result[0]["legs"][0]["departure_time"]["text"]
    return overall_departure_time, bus_departure_time, bus_line



tools = [
    {
        "type": "function",
        "function": {
            "name": "clear_chat_history",
            "description": "Clears the chat history and resets the conversation. Once this function is called, the chat history will be cleared as soon as all remaining actions are finished. you only need to call this function once.",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "returns the current datetime in ISO format",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_all_notes",
            "description": "Retrieves all exiting notes in the database",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_notes_object",
            "description": "Creates a notes object in the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The title of the note, eg: CISC 365 Test 2",
                    },
                    "text": {
                        "type": "string",
                        "description": "Any additional information regarding the subject of the note",
                    },
                },
                "required": ["name", "text"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_notes_object",
            "description": "Edits a notes object in the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The id of the note you want to edit. These can be retrieved by first viewing existing notes",
                    },
                    "name": {
                        "type": "string",
                        "description": "What the new name of the note should be. The name will remain unchanged if this field is not included",
                    },
                    "text": {
                        "type": "string",
                        "description": "What the new contents of the note should be. The contents will remain unchanged if this field is not included",
                    },
                },
                "required": ["id"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_notes_object",
            "description": "Deletes a notes object from the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The id of the note you want to edit. These can be retrieved by first viewing existing notes",
                    },
                },
                "required": ["id"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_bus_departure_time",
            "description": "Returns details about the next bus between home and campus.",
            "parameters": {
                "type": "object",
                "properties": {
                    "departure_or_arrival": {
                        "type": "string",
                        "enum": ["Departing", "Arriving"],
                        "description": "specifies whether the user wants to depart at the specified time, or arrive at the specified time.",
                    },
                    "datetime": {
                        "type": "string",
                        "description": "datetime object in iso format, defaults to current time if not specified.",
                    },
                },
                "required": ["departure_or_arrival"],
            },
        }
    },
]

restricted_tools = [
    {
        "type": "function",
        "function": {
            "name": "continue_chat",
            "description": "Lets the system know whether you are prompting for a followup response from the user or not, only use when specificly asking the user a question or otherwise expecting the user to follow up immediately",
            "parameters": {
                "type": "object",
                "properties": {
                    "wait_for_followup": {
                        "type": "string",
                        "enum": ["True", "False"],
                        "description": "whether or not expecting a follow up response from the user",
                    },
                },
                "required": ["wait_for_followup"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "speak",
            "description": "reads a text out loud, used to provide an appreviation of the textual output through audio",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "An abbreviation for the regular text response: for example use 'Here is what I learned about turtles' when outputting a paragraph detailing turtles, or use 'turning lights on' when using a function call that turns the lights on.",
                    },
                },
                "required": ["text"],
            },
        }
    },
]



def get_datetime(args):
    return {"role": "system", "content": f'the current datetime is: {datetime.datetime.now().isoformat()}'}

def view_all_notes(args):
    notes = load_notes()
    database = json.dumps(notes)
    return {"role": "system", "content": f'Here is the database of notes objects: {database}'}
def create_notes_object(args):
    id = add_note(args)
    return {"role": "system", "content": f'The note has been added with id: {id}'}
def edit_notes_object(args):
    edit_note(args)
    return {"role": "system", "content": f'The note has been edited'}
def delete_notes_object(args):
    delete_note(args["id"])
    return {"role": "system", "content": f'The note has been deleted'}

def check_bus_departure_time(args):
    try:
        if "datetime" not in args:
            date_time = None
        else:
            date_time = datetime.datetime.fromisoformat(args["datetime"])
        if args["departure_or_arrival"] == "Arriving":
            overall_departure_time, bus_departure_time, bus_line = next_bus_to_campus(arrival = date_time)
        else:
            overall_departure_time, bus_departure_time, bus_line = next_bus_to_campus(departure = date_time)
        return {"role": "system", "content": f'The next bus is number {bus_line}, and will arrive at {bus_departure_time}. The user should leave the house at {overall_departure_time}.'}
    except:
        return {"role": "system", "content": f'no suitable bus line was found.'}





tool_functions = {
    "get_datetime": get_datetime,
    "view_all_notes": view_all_notes,
    "create_notes_object": create_notes_object,
    "edit_notes_object": edit_notes_object,
    "delete_notes_object": delete_notes_object,
    "check_bus_departure_time": check_bus_departure_time,
}

tool_functions

def execute_tool(tool_call):
    function_name = tool_call.function.name
    parameters = json.loads(tool_call.function.arguments)
    if function_name in tool_functions:
        return tool_functions[function_name](parameters)
    else:
        return {"role": "system", "content": f'tool call failed for {function_name}'}

