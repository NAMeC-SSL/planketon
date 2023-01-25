import errno
import fcntl
import os
import sys
import json
from enum import Enum
import socket
from typing import Optional

import numpy as np

import constants


class KICK(Enum):
    NO_KICK = 0
    STRAIGHT_KICK = 1
    CHIP_KICK = 2


class Command:
    def __init__(self, id=0, forward_velocity=0.0, left_velocity=0.0, angular_velocity=0.0,
                 kick=KICK.NO_KICK, power=0.5, charge=False, dribbler=0.0):
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
            self.power = power

    def toJson(self):
        if self.kick.value == KICK.STRAIGHT_KICK:
            return {
                "Command": {
                    "id": self.id,
                    "forward_velocity": self.forward_velocity,
                    "left_velocity": self.left_velocity,
                    "angular_velocity": self.angular_velocity,
                    "charge": self.charge,
                    "kick": {"StraightKick": {"power": self.power}},
                    "dribbler": self.dribbler
                }
            }
        elif self.kick.value == KICK.CHIP_KICK:
            return {
                "Command": {
                    "id": self.id,
                    "forward_velocity": self.forward_velocity,
                    "left_velocity": self.left_velocity,
                    "angular_velocity": self.angular_velocity,
                    "charge": self.charge,
                    "kick": {"ChipKick": {"power": self.power}},
                    "dribbler": self.dribbler
                }
            }
        return {
            "Command": {
                "id": self.id,
                "forward_velocity": self.forward_velocity,
                "left_velocity": self.left_velocity,
                "angular_velocity": self.angular_velocity,
                "charge": self.charge,
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
        self.data_port = constants.yellow_data_port if is_yellow else constants.blue_data_port
        self.send_port = constants.yellow_send_port if is_yellow else constants.blue_send_port

        self.running = True

        # Receive socket
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_socket.bind(('0.0.0.0', self.data_port))
        fcntl.fcntl(self.recv_socket, fcntl.F_SETFL, os.O_NONBLOCK)

        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_socket.connect((self.host, self.send_port))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def send(self):
        data = []
        for command in self.commands:
            data.append(command.toJson())
        data_send = json.dumps(data)
        print(data_send)
        self.send_socket.sendall(data_send.encode())

    def recv_data(self):
        try:
            return json.loads(self.recv_socket.recv(4096))
        except socket.error as e:
            err = e.args[0]
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                return None
            else:
                print(e)
                sys.exit(1)
