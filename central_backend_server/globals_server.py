# This file contains the global state of the server's logic.
# This is global state because it is shared across multiple files in the project.
# They can therefore be used in any file in the project.

import json
import asyncio

_connected_clients = set()
_connected_client_roles = dict()

async def broadcast_message(json_dict: dict):
    if _connected_clients:
        # Convert the message to JSON
        message = json.dumps(json_dict)
        await asyncio.gather(*(ws.send(message) for ws in _connected_clients))
        # The broadcast function does not work until the function that
        # calls `broadcast_message` yields. Idk why. So we use the loop.

def add_client(websocket):
    _connected_clients.add(websocket)

def remove_client(websocket):
    _connected_clients.remove(websocket)

def remove_client_role(websocket):
    _connected_client_roles.pop(websocket, None)

def set_client_role(websocket, role):
    _connected_client_roles[websocket] = role

def has_a_client_role(websocket):
    return websocket in _connected_client_roles

def get_client_role(websocket):
    return _connected_client_roles[websocket]

def is_furhat_connected():
    return "furhat" in _connected_client_roles.values()