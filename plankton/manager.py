import signal
from abc import abstractmethod
from typing import Dict

import numpy as np

import constants
from plankton_client import Client, Robot, KICK, Command

def angle_wrap(alpha):
    return (alpha + np.pi) % (2 * np.pi) - np.pi

def frame(x, y=0, orientation=0):
    if type(x) is tuple:
        x, y, orientation = x

    cos, sin = np.cos(orientation), np.sin(orientation)

    return np.array([[cos, -sin, x], [sin, cos, y], [0, 0, 1]])

def frame_inv(frame):
    frame_inv = np.eye(3)
    R = frame[:2, :2]
    frame_inv[:2, :2] = R.T
    frame_inv[:2, 2] = -R.T @ frame[:2, 2]
    return frame_inv


def robot_frame(robot : Robot):
    pos = robot.position
    return frame(pos[0], pos[1], robot.orientation)


class Manager:
    def __init__(self, client: Client):
        self.client = client
        self.running = True
        
        teams = ["allies", "enemies"]

        self.robots: [str, Dict[int, Robot]] = {
            "allies": [Robot(robot_id, self) for robot_id in range(constants.max_robots)],
            "enemies": [Robot(robot_id, self) for robot_id in range(constants.max_robots)]
        }

        for (team, number) in [(team, number) for team in teams for number in range(constants.max_robots)]:
            self.__dict__["%s%d" % (team, number)] = self.robots[team][number]

        self.ball = None
        self.field = None

        signal.signal(signal.SIGINT, handler=self.handler)

    def handler(self, _signum, _frame):
        self.running = False
        self.stop()

    @abstractmethod
    def step(self):
        pass

    def stop(self):
        self.client.commands.clear()
        self.client.send()

    def update_ball(self, data):
        if data["ball"] is not None:
            if self.ball is None:
                self.ball = np.array(data["ball"])
            else:
                self.ball[0] = data["ball"][0]
                self.ball[1] = data["ball"][1]

    def update_robots(self, str_team: str, data):
        for number, robot in enumerate(data[str_team]):
            if robot is None:
                continue
            if "robot" in robot:
                self.robots[str_team][number].position = np.array(robot["robot"]["position"])
                self.robots[str_team][number].orientation = np.array(robot["robot"]["orientation"])

    def update_data(self, data):
        if "ball" in data:
            self.update_ball(data)

        if "allies" in data:
            self.update_robots("allies", data)

        if "enemies" in data:
            self.update_robots("enemies", data)

        if "field" in data:
            self.field = data["field"]

    def run(self):
        while self.running:
            self.client.commands.clear()
            data = self.client.recv_data()
            if data is None:
                continue
            self.update_data(data)
            self.step()
            self.client.send()

    def go_to(self, robot: Robot, x: float, y: float, orientation: float, charge=False, dribble=0.0, kick=KICK.NO_KICK) -> bool:
        p = 3

        Ti = frame_inv(robot_frame(robot))
        target_in_robot = Ti @ np.array([x, y, 1])

        e = np.array([target_in_robot[0], target_in_robot[1], angle_wrap(orientation - robot.orientation)])

        arrived = np.linalg.norm(e) < 0.05
        order = np.array([p, p, 1.5]) * e

        self.client.commands.append(
            Command(id=robot.id, forward_velocity=order[0], left_velocity=order[1], angular_velocity=order[2], kick=kick, charge=charge, dribbler=dribble)
        )

        return arrived

    def control(self, robot: Robot, forward_velocity=0.0, left_velocity=0.0, angular_velocity=0.0,
                kick=KICK.NO_KICK, charge=False, dribbler=0.0):
        self.client.commands.append(Command(robot.id, forward_velocity, left_velocity, angular_velocity,
                                            kick, charge, dribbler))
