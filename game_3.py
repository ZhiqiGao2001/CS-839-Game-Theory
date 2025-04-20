import random

# A Minecraft-themed cooperative protocol similar in structure to game_1.py citeturn0file0
PROTOCOL_COMMUNICATION = '''
Message Format:
[CMD_CODE] [Optional: Extended Parameters]

CMD_CODES and Guidelines:

- MINE: Mine Resources  
   Usage: "MINE:<RESOURCE_TYPE> [UNITS]"  
   • RESOURCE_TYPE must be one of: COAL, IRON, GOLD, DIAMOND

- CRAFT: Craft Items  
   Usage: "CRAFT:<ITEM_NAME>|<QUANTITY>"  
   • ITEM_NAME examples: PICKAXE, SWORD, AXE, CHEST, FURNACE

- BLD: Build Structures  
   Usage: "BLD:<STRUCTURE_NAME>|<COORDINATES>"  
   • STRUCTURE_NAME examples: HOUSE, BRIDGE, FARM, WALL

- EXPL: Explore Biome  
   Usage: "EXPL:<BIOME_NAME>|<COORDINATES>"  
   • BIOME_NAME must be one of: FOREST, DESERT, PLAINS, MOUNTAIN, CAVE
'''

ACTION_TEMPLATE = {
    "ACTION": "",  # Select one of: "MOVE", "COLLECT", "EXPLORE", "MINE", "CRAFT", "BUILD", "REPEAT"
    "LOCATION": {
        "COORDINATE": "",  # provide a coordinate tuple in the form "(x, y)"
        "AREA": "",        # For EXPLURE, the biome name; otherwise blank
    },
    "RESOURCE": {
        "TYPE": "",        # The resource or item involved
        "QUANTITY": 1,       # Quantity for mining/crafting; -1 if not applicable
    },
    "STRUCTURE": "",  # The structure name for building; blank otherwise
}

ACTION_REQUIREMENT = '''
For ACTION, select one of: "MINE", "CRAFT", "BLD", "EXPL", "REPEAT". If the message is unclear or specifies an impossible action (e.g., a negative resource quantity), use "REPEAT".
For COORDINATE, provide a tuple in the form "(x, y)", leaving it blank if not applicable.
For AREA, specify the biome name when EXPL; leave blank otherwise.
For RESOURCE.TYPE, indicate resource/item; for RESOURCE.QUANTITY, an integer or -1 if not applicable.
For STRUCTURE, specify the structure name when BLD; leave blank otherwise.
'''

default_system_message = f'''
Welcome to the Minecraft-themed cooperative game! You'll receive messages from your teammate and must decide your next action.
Your response must strictly adhere to the following action template:
ACTION_TEMPLATE = {ACTION_TEMPLATE}, with requirement: {ACTION_REQUIREMENT}
Ensure that every response you generate conforms exactly to this template.
'''

protocol_system_message = f'''
Welcome to the Minecraft-themed cooperative game! You'll receive messages from your teammate and must decide your next action.
All incoming messages will follow the protocol format: {PROTOCOL_COMMUNICATION}
Your response must strictly adhere to the following action template:
ACTION_TEMPLATE = {ACTION_TEMPLATE}, with requirement: {ACTION_REQUIREMENT}
Ensure that every response you generate conforms exactly to this template.
'''


def mine_message(structured=True):
    quantity = random.randint(1, 64)
    resource = random.choice(["COAL", "IRON", "GOLD", "DIAMOND", "WOOD"])
    if structured:
        message = f"MINE:{resource} {quantity}"
    else:
        templates = [
            f"Mine {quantity} units of {resource}.",
            f"Please mine {quantity} {resource}.",
            f"Get {quantity} {resource} from the veins.",
        ]
        message = random.choice(templates)

    correct_response = {
        "ACTION": "MINE",
        "LOCATION": {"COORDINATE": "", "AREA": ""},
        "RESOURCE": {"TYPE": resource, "QUANTITY": quantity},
        "STRUCTURE": ""
    }
    return message, correct_response


def craft_message(structured=True):
    qty = random.randint(1, 10)
    item = random.choice(["PICKAXE", "SWORD", "AXE", "CHEST", "FURNACE"])
    if structured:
        message = f"CRAFT:{item}|{qty}"
    else:
        templates = [
            f"Craft {qty} {item}(s).",
            f"I need {qty} {item}.",
            f"Please make {qty} {item}.",
        ]
        message = random.choice(templates)

    correct_response = {
        "ACTION": "CRAFT",
        "LOCATION": {"COORDINATE": "", "AREA": ""},
        "RESOURCE": {"TYPE": item, "QUANTITY": qty},
        "STRUCTURE": ""
    }
    return message, correct_response


def build_message(structured=True):
    struct = random.choice(["HOUSE", "BRIDGE", "FARM", "WALL"])
    coord = f"({random.randint(0, 100)}, {random.randint(0, 100)})"
    if structured:
        message = f"BLD:{struct}|{coord}"
    else:
        templates = [
            f"Build a {struct} at {coord}.",
            f"Construct {struct} on {coord}.",
            f"Please build {struct} at {coord}.",
        ]
        message = random.choice(templates)

    correct_response = {
        "ACTION": "BLD",
        "LOCATION": {"COORDINATE": coord, "AREA": ""},
        "RESOURCE": {"TYPE": "", "QUANTITY": -1},
        "STRUCTURE": struct
    }
    return message, correct_response


def explore_message(structured=True):
    biome = random.choice(["FOREST", "DESERT", "PLAINS", "MOUNTAIN", "CAVE"])
    coord = f"({random.randint(0, 100)}, {random.randint(0, 100)})"
    if structured:
        message = f"EXPL:{biome}|{coord}"
    else:
        templates = [
            f"Explore the {biome} at {coord}.",
            f"Investigate {biome} region {coord}.",
            f"Check out the {biome} around {coord}.",
        ]
        message = random.choice(templates)

    correct_response = {
        "ACTION": "EXPL",
        "LOCATION": {"COORDINATE": coord, "AREA": biome},
        "RESOURCE": {"TYPE": "", "QUANTITY": -1},
        "STRUCTURE": ""
    }
    return message, correct_response


def bad_message(structured=True):
    # Generate malformed or ambiguous commands
    choices = [
        "MINE", "MINE | COAL|ten", "CRAFT:WOOD", "BLD: house", "EXPL:|()",
        "Gather wood", "Make random sword", "Go there"
    ]
    message = random.choice(choices)
    correct_response = {
        "ACTION": "REPEAT",
        "LOCATION": {"COORDINATE": "", "AREA": ""},
        "RESOURCE": {"TYPE": "", "QUANTITY": -1},
        "STRUCTURE": ""
    }
    return message, correct_response


def random_message(structured=True):
    funcs = [mine_message, craft_message, build_message, explore_message, bad_message]
    func = random.choice(funcs)
    msg, correct = func(structured)
    mtype = func.__name__.replace('_message', '')
    return (msg, correct), mtype


