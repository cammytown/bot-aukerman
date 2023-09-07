"""
Bot Aukerman server module.

This module contains the Server class, which is responsible for receiving
requests/data from other processes, processing them in the context of a
Performance, and sending back a response.
"""

from typing import Optional
import simpleaudio as sa
import zmq
import time

from .performance import Performance

#@TODO move to separate package?
class Server:
    socket: zmq.Socket
    performance: Performance

    # Currently playing audio object
    # active_play_obj: Optional[sa.PlayObject] = None

    def __init__(self):
        # Init ZMQ socket
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")

    def start(self):
        # Init Performance
        self.performance = Performance()
        self.performance.initialize_tts()
        self.performance.initialize_stt()

        print("bot-aukerman server started")

        while(True):
            time.sleep(0.2)

            # Get any socket data (requests from other processes):
            try:
                message = self.socket.recv_json(flags=zmq.NOBLOCK)
                assert isinstance(message, dict)
                self.receive_message(message)
            except zmq.ZMQError as e:
                if e.errno == zmq.EAGAIN:
                    pass
            else:
                #  Send reply back to client
                reply = { "errors": None }
                self.socket.send_json(reply)

    def receive_message(self, message: dict):
        print("server received message: ", message)

        match message["type"]:
            case "observe_user_input":
                self.observe_user_input(message["user_input"])

            case "request_dialogue":
                self.request_dialogue(message["character_idx"])

            case "interrupt":
                self.interrupt()

    # def stop(self):
    #     pass

    # def restart(self):
    #     pass

    def observe_user_input(self, user_input: str):
        self.performance.interrupt()
        # self.active_play_obj = self.performance.perform_dialogue(user_input)

    def request_dialogue(self, character_idx: str):
        self.performance.generate_dialogue(character_idx = character_idx)
    
    # def interrupt(self):
    #     if(self.active_play_obj):
    #         self.active_play_obj.stop()
