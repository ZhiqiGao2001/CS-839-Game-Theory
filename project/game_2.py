import random

# New Protocol for Deep Space Mission

PROTOCOL_COMMUNICATION = '''
Message Format:
[CMD_CODE] [Optional: Extended Parameters]

CMD_CODES and Guidelines:

- SCAN: Scan a celestial object  
   Usage: "SCAN:<OBJECT_TYPE> [COORDINATES]"  
   • OBJECT_TYPE must be one of: PLANET, ASTEROID, COMET, STAR

- LAND: Initiate landing sequence  
   Usage: "LAND:<SURFACE_TYPE>|<COORDINATES>"  
   • SURFACE_TYPE must be one of: ROCKY, SANDY, ICY

- SAMPLE: Collect sample from surface  
   Usage: "SAMPLE:<MATERIAL_TYPE>|<UNITS>|<COORDINATES>"  
   • MATERIAL_TYPE must be one of: ROCK, ICE, DUST, GAS

- COMM: Send communication to mission control  
   Usage: "COMM:<STATUS>|<BASE_COORDINATES>"  
   • STATUS can be: SUCCESS, CRITICAL, NEED_SUPPORT
'''

ACTION_TEMPLATE = {
    "ACTION": "",
    # Choose one of: "SCAN", "LAND", "SAMPLE", "COMM". If the message is unclear or specifies an impossible action, use "REPEAT".
    "TARGET": {
        "COORDINATE": "",  # Provide a coordinate tuple in the form "(x, y)".
        "OBJECT": "",      # Provide the object or classification (e.g., PLANET, ASTEROID) if applicable.
    },
    "MATERIAL_DETAIL": {
        "MATERIAL_TYPE": "",  # For SAMPLE commands, must be one of: ROCK, ICE, DUST, GAS. Otherwise, leave as an empty string.
        "VALUE": -1,          # Provide an integer value (e.g., sample quantity); use -1 if not applicable.
    },
    "SURFACE_TYPE": ""  # For LAND commands, must be one of: ROCKY, SANDY, ICY. Otherwise, leave as an empty string.
}

ACTION_REQUIREMENT = '''
Your response must follow this exact structure:

- "ACTION": 
  • Choose one of the following: "SCAN", "LAND", "SAMPLE", "COMM". 
  • If the message is unclear (e.g., missing essential information like coordinates) or specifies an impossible action (e.g., a negative quantity), respond with "REPEAT", and put all other fields as default.

- "TARGET": 
  • "COORDINATE": Provide a coordinate tuple in the form "(x, y)" that indicates the target location. If not applicable, leave it as an empty string ''.
  • "OBJECT": OBJECT_TYPE must be one of: PLANET, ASTEROID, COMET, STAR. If this information is not applicable, leave it as an empty string ''.

- "MATERIAL_DETAIL": 
  • "MATERIAL_TYPE": For SAMPLE commands, include the material type (must be one of: ROCK, ICE, DUST, GAS). For other actions, leave it as an empty string ''.
  • "VALUE": Provide an integer value associated with the material detail (for example, the sample quantity). If this value is not applicable, use -1.

- "SURFACE_TYPE": 
  • For LAND commands, provide the surface type (must be one of: ROCKY, SANDY, ICY). For other actions, leave it as an empty string ''.

For any field that does not apply to the current action, leave it as an empty string '' or -1 where indicated.
'''

default_system_message = f'''
Welcome to the deep space mission! You'll receive messages from mission control and must decide your next action. 
Your response must strictly adhere to the following action template:
ACTION_TEMPLATE = {ACTION_TEMPLATE}, with requirement: {ACTION_REQUIREMENT}
Ensure that every response you generate conforms exactly to this template.
'''

protocol_system_message = f'''
Welcome to the deep space mission! You'll receive messages following the protocol format below:
{PROTOCOL_COMMUNICATION}
Your response must strictly adhere to the following action template:
ACTION_TEMPLATE = {ACTION_TEMPLATE}, with requirement: {ACTION_REQUIREMENT}
Ensure that every response you generate conforms exactly to this template.
'''


def scan_message(structured=True):
    # Randomly select an object type and generate coordinates
    object_types = ["PLANET", "ASTEROID", "COMET", "STAR"]
    object_type = random.choice(object_types)
    coordinate = f"({random.randint(0, 100)}, {random.randint(0, 100)})"

    if structured:
        message = f"SCAN:{object_type} {coordinate}"
    else:
        possible_messages = [
            f"Please scan the {object_type} located at {coordinate}.",
            f"Initiate scan on {object_type} near {coordinate}.",
            f"Scan {object_type} at {coordinate}.",
            f"Could you check out that {object_type} around {coordinate}?",
            f"I need a scan on something that looks like a {object_type} at {coordinate}.",
            f"Run a scan on coordinates {coordinate} for any sign of a {object_type}."
        ]
        message = random.choice(possible_messages)

    correct_response = {
        "ACTION": "SCAN",
        "TARGET": {
            "COORDINATE": coordinate,
            "OBJECT": object_type,
        },
        "MATERIAL_DETAIL": {
            "MATERIAL_TYPE": "",  # Not applicable for SCAN
            "VALUE": -1         # Not applicable for SCAN
        },
        "SURFACE_TYPE": ""       # Not applicable for SCAN
    }

    return message, correct_response


def land_message(structured=True):
    # Randomly select a surface type and generate landing coordinates
    surface_types = ["ROCKY", "SANDY", "ICY"]
    surface_type = random.choice(surface_types)
    coordinate = f"({random.randint(0, 100)}, {random.randint(0, 100)})"

    if structured:
        message = f"LAND:{surface_type}|{coordinate}"
    else:
        possible_messages = [
            f"Prepare to land on a {surface_type} surface at {coordinate}.",
            f"Initiate landing sequence on {surface_type} terrain, coordinate {coordinate}.",
            f"Land at {coordinate} on a {surface_type} area.",
            f"Set course for a {surface_type} landing near {coordinate}.",
            f"Attempt descent onto {surface_type} ground at {coordinate}.",
            f"Touch down on {coordinate} where the surface is {surface_type}."
        ]
        message = random.choice(possible_messages)

    correct_response = {
        "ACTION": "LAND",
        "TARGET": {
            "COORDINATE": coordinate,
            "OBJECT": ""
        },
        "MATERIAL_DETAIL": {
            "MATERIAL_TYPE": "",  # Not applicable for LAND
            "VALUE": -1          # Not applicable for LAND
        },
        "SURFACE_TYPE": surface_type  # Provided for LAND command
    }

    return message, correct_response


def sample_message(structured=True):
    # Randomly select a material type (must be one of: ROCK, ICE, DUST, GAS) and quantity for the sample
    material_types = ["ROCK", "ICE", "DUST", "GAS"]
    material_type = random.choice(material_types)
    quantity = random.randint(1, 50)
    coordinate = f"({random.randint(0, 100)}, {random.randint(0, 100)})"

    if structured:
        message = f"SAMPLE:{material_type}|{quantity}|{coordinate}"
    else:
        possible_messages = [
            f"We need {quantity} units of {material_type} from {coordinate}.",
            f"Sample {material_type} at {coordinate} in quantity {quantity}.",
            f"Request {quantity} {material_type} samples from {coordinate}.",
            f"Collect some {material_type} around {coordinate}—about {quantity} units, I guess.",
            f"Could you get me roughly {quantity} units of {material_type} from near {coordinate}?",
            f"Check {coordinate} for {material_type} samples, probably {quantity} of them."
        ]
        message = random.choice(possible_messages)

    correct_response = {
        "ACTION": "SAMPLE",
        "TARGET": {
            "COORDINATE": coordinate,
            "OBJECT": ""
        },
        "MATERIAL_DETAIL": {
            "MATERIAL_TYPE": material_type,  # For SAMPLE, must be one of: ROCK, ICE, DUST, GAS.
            "VALUE": quantity                # Sample quantity
        },
        "SURFACE_TYPE": ""                   # Not applicable for SAMPLE
    }

    return message, correct_response


def comm_message(structured=True):
    # Randomly select a communication status and generate base coordinates
    statuses = ["SUCCESS", "CRITICAL", "NEED_SUPPORT"]
    status = random.choice(statuses)
    base_coordinate = f"({random.randint(0, 100)}, {random.randint(0, 100)})"

    if structured:
        message = f"COMM:{status}|{base_coordinate}"
    else:
        possible_messages = [
            f"Send update: {status} at base coordinates {base_coordinate}.",
            f"Communication to mission control: {status}, located at {base_coordinate}.",
            f"Status report: {status} from {base_coordinate}.",
            f"Message HQ that we're at {base_coordinate} with a status of {status}.",
            f"Notify mission control: {status} at {base_coordinate}.",
            f"Relay {status} from our position at {base_coordinate}."
        ]
        message = random.choice(possible_messages)

    correct_response = {
        "ACTION": "COMM",
        "TARGET": {
            "COORDINATE": base_coordinate,
            "OBJECT": ""
        },
        "MATERIAL_DETAIL": {
            "MATERIAL_TYPE": "",  # Not applicable for COMM
            "VALUE": -1          # Not applicable for COMM
        },
        "SURFACE_TYPE": ""       # Not applicable for COMM
    }

    return message, correct_response


def bad_message(structured=True):
    # Generate malformed or unclear messages
    random_coordinate = f"({random.randint(0, 100)}, {random.randint(0, 100)})"
    random_quantity = random.randint(-10, 10)  # Might be negative
    if structured:
        possible_messages = [
            "SCAN",
            f"LAND |{random_coordinate}",  # LAND command with no valid surface type
            "SAMPLE:| |",  # SAMPLE command missing material type, quantity, and coordinate
            f"COMM: |{random_coordinate}",  # COMM command missing status
            f"SAMPLE:METAL|{random_quantity}|{random_coordinate}",  # SAMPLE with an invalid material type 'METAL'
            f"LAND:UNKNOWN|{random_coordinate}"  # LAND with an unknown surface type            f"COMM: |{random_coordinate}",
            f"ASDHDKJK",
            f"LAND|||SCAM"
        ]
        message = random.choice(possible_messages)
    else:
        possible_messages = [
            "Scans",
            f"Land on {random_coordinate}",
            f"Communication missing status at {random_coordinate}.",
            f"Request to collect {-abs(random_quantity)} units of GAS.",          # Corresponds to "SAMPLE:| |" / negative quantity error
            f"Send a communication from {random_coordinate}.",                     # Corresponds to "COMM: |{random_coordinate}"
            f"Request metal sample with {random_quantity} units at {random_coordinate}.",  # Corresponds to SAMPLE:METAL...
            f"Maybe sample something near {random_coordinate}?",
            "What is our status?",
            f"Land and scan {random_coordinate}"
        ]
        message = random.choice(possible_messages)

    correct_response = {
        "ACTION": "REPEAT",
        "TARGET": {
            "COORDINATE": "",
            "OBJECT": ""
        },
        "MATERIAL_DETAIL": {
            "MATERIAL_TYPE": "",
            "VALUE": -1
        },
        "SURFACE_TYPE": ""
    }

    return message, correct_response


def random_message(structured=True):
    message_type = random.choice(["scan", "land", "sample", "comm", "bad"])
    if message_type == "scan":
        return scan_message(structured), message_type
    elif message_type == "land":
        return land_message(structured), message_type
    elif message_type == "sample":
        return sample_message(structured), message_type
    elif message_type == "comm":
        return comm_message(structured), message_type
    else:
        return bad_message(structured), message_type


# Example usage:
if __name__ == "__main__":
    # Generate a random unstructured message and its corresponding expected response
    (msg, response), msg_type = random_message(structured=False)
    print("Generated Message:", msg)
    print("Expected Response:", response)
