import numpy as np

import utils
from plankton_client import Robot


class FieldObserver:

    def __init__(self):
        self.__ball_history: np.ndarray = np.array([0., 0.], ndmin=2)
        self.__ball_traj_m_p: tuple[float, float] = (0, 0)
        self.__ball_moving: bool = False
        self.__closest_rob_to_ball: Robot = None

    def __update_ball_history(self, ball: tuple[float, float]):
        if len(self.__ball_history) >= 40:
            self.__ball_history = np.delete(self.__ball_history, 0, axis=0)
        self.__ball_history = np.append(self.__ball_history, np.array(ball, ndmin=2), axis=0)

    def __check_ball_moving(self):
        self.__ball_moving = (np.std(self.__ball_history, axis=0) > 0.1).any()  # TODO: affine this number
        # print(self.__ball_moving)
        # print(np.std(self.__ball_history, axis=0))

    def __compute_ball_traj(self):
        m, p = reversed(np.polynomial.polynomial.polyfit(
            [ball[0] for ball in self.__ball_history],
            [ball[1] for ball in self.__ball_history],
            1
        ))
        self.__ball_traj_m_p = m, p

    def __update_closest_robot_to_ball(self, ball: tuple[float, float], robots: list[Robot]):
        self.__closest_rob_to_ball = utils.closest_to_target(robots, target=ball)

    def get_data(self):
        return {
            "ball_traj__m_p": self.__ball_traj_m_p,
            "ball_history": self.__ball_history,
            "ball_moving": self.__ball_moving,
            "first_rob_near_ball": self.__closest_rob_to_ball,
        }

    def step(self, ball: tuple[float, float], robots: list[Robot]):
        self.__update_ball_history(ball)
        self.__check_ball_moving()
        self.__compute_ball_traj()
        self.__update_closest_robot_to_ball(ball, robots)
