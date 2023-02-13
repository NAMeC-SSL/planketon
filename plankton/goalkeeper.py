from typing import Callable

import numpy as np
import scipy as scipy

import utils
from manager import Manager
from plankton_client import Robot


def determine_goal_area(field: dict, x_positive: bool) -> dict[str, ]:
    """
    Returns the goal scoring area
    :param field: The field we're playing on
    :param x_positive: True if the team is on the x positive side
    :return: Top left, bottom left, bottom right, top right and center (closest to field center) of the goal scoring area
    """
    if x_positive:
        return {
            "top_left":     np.array([field["length"] / 2                      ,  field["goal_width"] / 2]),
            "bottom_left":  np.array([field["length"] / 2                      , -field["goal_width"] / 2]),
            "bottom_right": np.array([field["length"] / 2 + field["goal_depth"], -field["goal_width"] / 2]),
            "top_right":    np.array([field["length"] / 2 + field["goal_depth"],  field["goal_width"] / 2]),
            "center":       np.array([field["length"] / 2                      , 0.])
        }
    else:
        return {
            "top_left":     np.array([-field["length"] / 2 - field["goal_depth"],  field["goal_width"] / 2]),
            "bottom_left":  np.array([-field["length"] / 2 - field["goal_depth"], -field["goal_width"] / 2]),
            "bottom_right": np.array([-field["length"] / 2                      , -field["goal_width"] / 2]),
            "top_right":    np.array([-field["length"] / 2                      ,  field["goal_width"] / 2]),
            "center":       np.array([-field["length"] / 2                      , 0.])
        }


class GoalKeeper:

    def __init__(self, manager: Manager, rob: Robot, field: dict, on_positive_half: bool):
        self.__manager: Manager = manager
        self.__robot: Robot = rob
        self.__GK_SCORE_AREA: dict = determine_goal_area(field, on_positive_half)
        self.__on_positive_half: bool = on_positive_half
        if on_positive_half:
            self.__CENTER_LINE: Callable[[float, float], float] = \
                utils.traj_function(self.__GK_SCORE_AREA["top_left"], self.__GK_SCORE_AREA["bottom_left"], general_form=True)
        else:
            self.__CENTER_LINE: Callable[[float, float], float] = utils.traj_function(self.__GK_SCORE_AREA["top_right"],
                                                                self.__GK_SCORE_AREA["bottom_right"], general_form=True)

    def __intercept_ball_coordinates(self, ball_traj_params: tuple[float, float]) -> tuple[tuple[float, float], bool]:
        # TODO: try intersect between two lines
        # ball_traj: Callable[[float, float], float] = lambda x, y: ball_traj_params[0] * x + ball_traj_params[1] - y
        # equation = lambda xy: [self.__CENTER_LINE(*xy), ball_traj(*xy)]
        # intersect_point, _, retval, _ = scipy.optimize.fsolve(equation, np.array([-10, -10]), full_output=True)

        ball_traj = lambda x: ball_traj_params[0] * x + ball_traj_params[1]
        gk_posts_center = self.__GK_SCORE_AREA["center"][0]
        target = np.array([gk_posts_center, ball_traj(gk_posts_center)])
        offset = [0.09, 0.] if self.__on_positive_half else [-0.09, 0.]
        print(target + offset)
        # print(target)

        return tuple(target), utils.point_in_rectangle(target + offset, self.__GK_SCORE_AREA)

    def __limit_to_goalarea(self, x: float, y: float) -> tuple[float, float]:
        new_x, new_y = x, y

        if self.__on_positive_half:
            max_x, max_y = self.__GK_SCORE_AREA["top_left"]
            min_x, min_y = self.__GK_SCORE_AREA["bottom_left"]
        else:
            max_x, max_y = self.__GK_SCORE_AREA["top_right"]
            min_x, min_y = self.__GK_SCORE_AREA["bottom_right"]

        # Limit movement if it tries to move too far from its defined area, by going to the closest limit
        if not min_x <= x <= max_x:
            new_x = min_x if abs(x-min_x) < abs(x-max_x) else max_x
        if not min_y <= y <= max_y:
            new_y = min_y if abs(y-min_y) < abs(y-max_y) else max_y

        return new_x, new_y

    def step(self, ball_data: dict):
        if ball_data["ball_moving"]:
            block_ball_coords, need_intercept = self.__intercept_ball_coordinates(ball_data["ball_traj__m_p"])
            if need_intercept:
                print(f"Before limiter {block_ball_coords}")
                block_ball_coords = self.__limit_to_goalarea(*block_ball_coords)
                print(f"After limiter {block_ball_coords}")
                self.__manager.go_to(
                    self.__robot,
                    x=block_ball_coords[0],
                    y=block_ball_coords[1],
                    orientation=utils.angle_towards(self.__robot.position, ball_data["ball_history"][-1])
                )
            else:
                print(f"No interception required, going to {self.__GK_SCORE_AREA['center']}")
                self.__manager.go_to(
                    self.__robot,
                    x=self.__GK_SCORE_AREA["center"][0],
                    y=self.__GK_SCORE_AREA["center"][1],
                    orientation=utils.angle_towards(self.__robot.position, ball_data["ball_history"][-1])
                )
        else:
            print(f"Not moving, going to {self.__GK_SCORE_AREA['center']}")
            self.__manager.go_to(
                self.__robot,
                x=self.__GK_SCORE_AREA["center"][0],
                y=self.__GK_SCORE_AREA["center"][1],
                orientation=utils.angle_towards(self.__robot.position, ball_data["ball_history"][-1])
            )