import signal
import sys
import json
from enum import Enum
from typing import Optional

import numpy as np
import zmq

import constants


class KICK(Enum):
    NO_KICK = 0
    STRAIGHT_KICK = 1
    CHIP_KICK = 2


class Command:
    def __init__(self, id=0, forward_velocity=0.0, left_velocity=0.0, angular_velocity=0.0,
                 kick=KICK.NO_KICK, charge=False, dribbler=0.0):
        self.id = id
        self.forward_velocity = forward_velocity
        self.left_velocity = left_velocity
        self.angular_velocity = angular_velocity
        self.charge = charge
        self.dribbler = dribbler

        if kick.value > KICK.CHIP_KICK.value:
            print("There is an error with the kick int send")
        else:
            self.kick = kick

    def toJson(self):
        return {
            "Command": {
                "id": self.id,
                "forward_velocity": self.forward_velocity,
                "left_velocity": self.left_velocity,
                "angular_velocity": self.angular_velocity,
                "charge": self.charge,
                "kick": self.kick.value,
                "dribbler": self.dribbler
            }
        }


class Robot:
    def __init__(self, robot_id: int, client):
        self.id: int = robot_id
        self.position: Optional[np.ndarray] = None
        self.orientation: Optional[float] = None
        self.client: Client = client

    def commands(self, forward_velocity=0.0, left_velocity=0.0, angular_velocity=0.0,
                 kick=KICK.NO_KICK, charge=False, dribbler=0.0):
        pass

    def __str__(self):
        return f"Robot {self.id} - position: {self.position}, orientation: {self.orientation}"


class Client:
    commands: [Command] = []

    def __init__(self, is_yellow=False):
        self.host = "127.0.0.1"
        self.port = constants.yellow_port if is_yellow else constants.blue_port

        self.running = True

        # Receive socket
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.connect('tcp://127.0.0.1:%d' % self.port)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def send(self):
        data = []
        for command in self.commands:
            data.append(command.toJson())
        print(data)
        data_send = json.dumps({"commands": data})
        self.socket.send(data_send.encode())

    def recv_data(self):
        try:
            return self.socket.recv_json(zmq.DONTWAIT)
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                return None
            else:
                print(e)
                sys.exit(1)
