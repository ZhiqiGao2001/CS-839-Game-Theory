import random

PROTOCOL_COMMUNICATION = '''
Message Format:
[CMD_CODE] [Optional: Extended Parameters]

CMD_CODES and Guidelines:

- GTHR: Gather Resources  
   Usage: "GTHR:<RESOURCE_TYPE> [UNITS]"  
   • RESOURCE_TYPE must be one of: WOOD, STONE, FOOD, WEAPON

- EXPL: Explore Unknown Areas  
   Usage: "EXPL:<AREA_NAME>|<COORDINATES>"  
   • AREA_NAME is mandatory unless explicit coordinates are provided  
   • COORDINATES can be provided as (x,y)

- SEND: Dispatch Resources to Ally  
   Usage: "SEND:<RESOURCE_TYPE>|<UNITS>|<DESTINATION>"  
   • DESTINATION must be specified as a coordinate tuple, e.g., (x,y)

- MOVE: Relocate the Unit  
   Usage: "MOVE:<COORDINATES>"  
   • COORDINATES can be (x,y)
'''

ACTION_TEMPLATE = {
    "ACTION": "",  # Select one of: "MOVE", "COLLECT", "EXPLORE", "SEND". If the message is unclear or specifies an impossible action (e.g., a negative resource quantity), use "REPEAT".
    "LOCATION": {
        "COORDINATE": "",  # provide a coordinate tuple in the form "(x, y)".
        "AREA": "",  # Specify the AREA classification.
    },
    "RESOURCE": {
        "TYPE": "",  # Indicate the resource type.
        "QUANTITY": 1,  # Provide an integer value representing the resource quantity; use -1 if not applicable.
    }
}
ACTION_REQUIREMENT = '''
For action, Select one of: "MOVE", "COLLECT", "EXPLORE", "SEND". If the message is unclear (e.g. move without a given coordinate) or specifies an impossible action (e.g., a negative resource quantity), use "REPEAT".
For coordinate, Provide a coordinate tuple in the form "(x, y)", for area, only provide the number.
For quantity of resource required for the task, Provide an integer value representing the resource quantity; use -1 if not applicable.
RESOURCE_TYPE must be one of: WOOD, STONE, FOOD, WEAPON.
For irrelevant field, leave it blank as '', do not write anything
'''

default_system_message = f'''
Welcome to the cooperative game! You'll receive messages from your teammate and must decide your next action. 
Your response must strictly adhere to the following action template:
ACTION_TEMPLATE = {ACTION_TEMPLATE}, with requirement: {ACTION_REQUIREMENT}
Ensure that every response you generate conforms exactly to this template.
'''

protocol_system_message = f'''
Welcome to the cooperative game! You'll receive messages from your teammate and must decide your next action. 
All incoming messages will follow the protocol format: {PROTOCOL_COMMUNICATION}
Your response must strictly adhere to the following action template:
ACTION_TEMPLATE = {ACTION_TEMPLATE}, with requirement: {ACTION_REQUIREMENT}
Ensure that every response you generate conforms exactly to this template.
'''


def gather_message(structured=True):
    quantity = random.randint(1, 100)  # Randomly generate a quantity between 1 and 100
    array_item = ["WOOD", "STONE", "FOOD", "WEAPON"]
    resource_type = random.choice(array_item)  # Randomly select a resource type

    if structured:
        # Example of a structured protocol message (according to PROTOCOL_COMMUNICATION)
        message = f"GTHR:{resource_type} {quantity}"
    else:
        # Example of a natural language message using a template
        possible_messages = [
            f"Collect {quantity} units of {resource_type}.",
            f"Please gather {quantity} {resource_type}.",
            f"Get {quantity} {resource_type}",
        ]
        message = random.choice(possible_messages)

    # The corresponding response dictionary, following ACTION_TEMPLATE
    correct_response = {
        "ACTION": "COLLECT",  # Mapped from the protocol's GTHR command
        "LOCATION": {
            "COORDINATE": "",  # Gathering resources may not require a location
            "AREA": "",  # Specify the AREA classification.
        },
        "RESOURCE": {
            "TYPE": resource_type,
            "QUANTITY": quantity
        }
    }

    return message, correct_response


def send_message(structured=True):
    quantity = random.randint(1, 10)  # Randomly generate a quantity between 1 and 100
    array_item = ["WOOD", "STONE", "FOOD", "WEAPON"]
    resource_type = random.choice(array_item)  # Randomly select a resource type
    destination = f"({random.randint(0, 10)}, {random.randint(0, 10)})"

    if structured:
        # Example of a structured protocol message (according to PROTOCOL_COMMUNICATION)
        message = f"SEND:{resource_type}|{quantity}|{destination}"
    else:
        # Example of a natural language message using a template
        possible_messages = [
            f"Send {quantity} units of {resource_type} to {destination}.",
            f"I want {quantity} {resource_type} at {destination}.",
            f"I need {quantity} {resource_type} at {destination}.",
        ]
        message = random.choice(possible_messages)

    # The corresponding response dictionary, following ACTION_TEMPLATE
    correct_response = {
        "ACTION": "SEND",  # Mapped from the protocol's SEND command
        "LOCATION": {
            "COORDINATE": destination,
            "AREA": "",  # Specify the AREA classification.
        },
        "RESOURCE": {
            "TYPE": resource_type,
            "QUANTITY": quantity
        }
    }
    return message, correct_response


def move_message(structured=True):
    destination = f"({random.randint(0, 10)}, {random.randint(0, 10)})"

    if structured:
        # Example of a structured protocol message (according to PROTOCOL_COMMUNICATION)
        message = f"MOVE:{destination}"
    else:
        # Example of a natural language message using a template
        possible_messages = [
            f"Move to {destination}.",
            f"Relocate to {destination}.",
            f"Go to coordinate {destination}",
        ]
        message = random.choice(possible_messages)

    # The corresponding response dictionary, following ACTION_TEMPLATE
    correct_response = {
        "ACTION": "MOVE",  # Mapped from the protocol's MOVE command
        "LOCATION": {
            "COORDINATE": destination,
            "AREA": "",  # Specify the AREA classification.
        },
        "RESOURCE": {
            "TYPE": "",
            "QUANTITY": -1  # Not applicable for MOVE action
        }
    }

    return message, correct_response


def explore_message(structured=True):
    destination = f"({random.randint(0, 10)}, {random.randint(0, 10)})"
    area_num = random.randint(1, 10)
    area = f"Area {area_num}"

    if structured:
        # Example of a structured protocol message (according to PROTOCOL_COMMUNICATION)
        message = f"EXPL:{area}|{destination}"
    else:
        # Example of a natural language message using a template
        possible_messages = [
            f"Explore {area} at {destination}.",
            f"Investigate {area} at {destination}.",
            f"Check out {area} at {destination}",
        ]
        message = random.choice(possible_messages)
    # The corresponding response dictionary, following ACTION_TEMPLATE

    correct_response = {
        "ACTION": "EXPLORE",  # Mapped from the protocol's EXPL command
        "LOCATION": {
            "COORDINATE": destination,
            "AREA": str(area_num)
        },
        "RESOURCE": {
            "TYPE": "",
            "QUANTITY": -1  # Not applicable for EXPLORE action
        }
    }
    return message, correct_response


def bad_message(structured=True):
    random_destination = f"({random.randint(0, 10)}, {random.randint(0, 10)})"
    random_quantity = random.randint(-10, 10)  # Randomly generate a quantity between -10 and 10
    if structured:
        possible_messages = [
            "MOVE",
            "MOVE |(1,2,3,4)",
            "EXPL forest |||",
            f"EXPL | {random_destination}",
            f"GTHR: {random_destination}",
            f"GTHR: fish {random_quantity}",
            f"GTHR WOOD {-abs(random_quantity)}",
            f"SEND: WOOD | {random_quantity}",
            f'SEND: WOOD | {random_destination}',
        ]
        message = random.choice(possible_messages)
    else:
        # Example of a natural language message using a template
        possible_messages = [
            "Move to me.",
            "Move to (1,2,3,4).",
            f"Collect {-abs(random_quantity)} units of wood.",  # Force a negative quantity
            f"Gather at {random_destination}.",
            f"Please gather {random_quantity} fish"
            f"Send {random_quantity} units of food to me",
            f"Send {random_quantity} units of wood",
            "Explore the forest",
            "Check out this place ",
            "Gather resource",
            "Collect wood"
        ]
        message = random.choice(possible_messages)
    # The corresponding response dictionary, following ACTION_TEMPLATE
    correct_response = {
        "ACTION": "REPEAT",  # Mapped from the protocol's EXPL command
        "LOCATION": {
            "COORDINATE": "",
            "AREA": ""
        },
        "RESOURCE": {
            "TYPE": "",
            "QUANTITY": -1
        }
    }
    return message, correct_response


def random_message(structured=True):
    message_type = random.choice(["gather", "send", "move", "explore", "bad"])
    if message_type == "gather":
        return gather_message(structured),  message_type
    elif message_type == "send":
        return send_message(structured), message_type
    elif message_type == "move":
        return move_message(structured), message_type
    elif message_type == "explore":
        return explore_message(structured), message_type
    else:
        return bad_message(structured), message_type