import os
import sys
import codecs
import json
import re
import copy
import datetime

from typing import Dict, Tuple, Any,List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
import asyncio

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
        

from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC  Jan 24, 2024  Stand-alone connection manager (Was internal to fast_ws_v1)
        
"""
    Websocket manager
    (assumes case_id tracking)
      ^so, could generalize further
      - also, removed ASSUME_SEND_WS_TO_ALL_CASE_ID_CONNECTION

"""


class ConnectionManager:
    # Manage WebSocket connections, keep track of active connections
    # **dev version (stand alone manager now at: _____)
    def __init__(self):
        self.active_connections: Dict[Tuple[str, str], WebSocket] = {}
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, case_id: str, session_id: str):
        async with self.lock:
            await websocket.accept()
            self.active_connections[(case_id, session_id)] = websocket
            logging.info(f"[ws] connect from client: {(case_id, session_id)}")


    async def send_message(self, message: str, case_id: str, session_id: str):
        count_sent = 0
        async with self.lock:
            connections_copy = self.active_connections.copy()

        for key, connection in connections_copy.items():
            if key[0] == case_id:
                try:
                    await connection.send_text(message)
                    count_sent += 1
                except Exception as e:
                    logging.error(f"Error sending message: {e}")

        logging.info(f"[ws] sent msg to {count_sent} connections at case_id: {case_id}")


    async def disconnect(self, case_id: str, session_id: str):
        async with self.lock:
            connection = self.active_connections.pop((case_id, session_id), None)
            if connection:
                try:
                    await connection.close()
                except Exception as e:
                    logging.error(f"Error closing connection: {e}")

    def get_connections(self):
        # Return a shallow copy for safe iteration
        return self.active_connections.copy()

    async def get_connection(self, case_id: str, session_id: str):
        async with self.lock:
            return self.active_connections.get((case_id, session_id))


    async def connection_exists(self, case_id: str) -> bool:
        async with self.lock:
            return any(key[0] == case_id for key in self.active_connections)


def dev1():
    return


if __name__ == "__main__":
    dev1()


"""

"""
