from builtins import classmethod

import numpy as np

from field_observer import FieldObserver
import utils
from manager import Manager
from plankton_client import Robot, KICK


class Striker:

    def __init__(self, manager: Manager, robot: Robot):
        self.__manager: Manager = manager
        self.__robot = robot

    def __compute_preshoot_pos(self, target: np.array, ball: np.array) -> tuple[float, float, float]:
        """
        Compute the position in (x, y) to where the robot should position itself
        to be just in front of the ball, aiming towards a certain position.
        """
        print(target)
        # Vector from target (where the ball should go) towards ball
        target_to_ball: np.array = ball - target

        # Normalize the vector
        target_to_ball = utils.normalize_vec(target_to_ball)

        # Change the vector's origin to start from the ball
        position_pre_shoot: np.array = ball + target_to_ball
        position_pre_shoot_angle = utils.angle_towards(position_pre_shoot, target)
        return position_pre_shoot[0], position_pre_shoot[1], position_pre_shoot_angle

    def determine_shoot_target_to_goal(self, goal_posts: np.ndarray[np.ndarray], enemy_robs: list[Robot]):
        """
        Computes a point towards which the ball should go

        Parameters :
            goal_posts | Coordinates of left and right enemy goal posts
            enemy_robs | List of ClientRobot objects representing the enemy positions

        Returns :
            A 2-dimensional np array, the coordinates of the target to aim towards
        """
        enemy_gk: Robot = FieldObserver.guess_goal_keeper(enemy_robs, goal_posts)
        wanted_post: np.array = FieldObserver.get_furthest_post_of_gk(enemy_gk, goal_posts)

        # Apply a small offset to the wanted post
        # # TODO: another offset to put the target inside the goal posts
        gk_posts_mid: np.array = (goal_posts[0] + goal_posts[1]) / 2
        vec_post_to_mid: np.array = gk_posts_mid - wanted_post

        vec_post_to_mid = utils.normalize_vec(vec_post_to_mid)

        target = wanted_post + vec_post_to_mid

        return target

    def step(self, target: np.array):
        ball: np.array = self.__manager.ball

        # Compute pos to go to behind ball to aim towards target
        pre_shoot_pos = self.__compute_preshoot_pos(target=target, ball=ball)

        # Core of the decision between moving to shoot pos, and going for a shoot
        # True if vec angle from robot to ball is approximately equal to vec angle from ball to target
        prepared_to_shoot = np.isclose(utils.angle_towards(src=ball, dst=target), utils.angle_towards(self.__robot.position, ball), rtol=np.deg2rad(5))

        if not prepared_to_shoot:
            print("[PRE-SHOOT POS] Placing")
            self.__manager.go_to(self.__robot, *pre_shoot_pos)

        else:
            if np.linalg.norm(ball - self.__robot.position) < 0.15:
                print("Kicking ball")
                # TODO: wrap around an async timer
                self.__manager.go_to(self.__robot, *ball, utils.angle_towards(src=self.__robot.position, dst=target), kick=KICK.STRAIGHT_KICK, charge=True, power=4)
            else:
                # Run towards ball
                print("Going to ball")
                vec_forward_ball = utils.normalize_vec(ball - self.__robot.position)
                self.__manager.go_to(self.__robot, *(ball + vec_forward_ball), utils.angle_towards(src=self.__robot.position, dst=target))
