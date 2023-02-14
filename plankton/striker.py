from builtins import classmethod

import numpy as np

from field_observer import FieldObserver
import utils
from manager import Manager
from goalkeeper import determine_goal_area
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

    def __determine_shoot_target_to_goal(self, enemy_goal_posts: np.ndarray[np.ndarray], enemy_gk: Robot):
        """
        Computes a point towards which the ball should go

        Parameters :
            goal_posts | Coordinates of left and right enemy goal posts
            enemy_robs | List of ClientRobot objects representing the enemy positions

        Returns :
            A 2-dimensional np array, the coordinates of the target to aim towards
        """

        # Find which post the enemy goalkeeper is farthest to
        wanted_post: np.array = enemy_goal_posts[0]
        if np.linalg.norm(enemy_goal_posts[0] - enemy_gk.position) >= np.linalg.norm(enemy_goal_posts[1] - enemy_gk.position):
            wanted_post: np.array = enemy_goal_posts[1]

        # Apply a small offset to the wanted post
        # # TODO: another offset to put the target inside the goal posts
        gk_posts_mid: np.array = (enemy_goal_posts[0] + enemy_goal_posts[1]) / 2
        vec_post_to_mid: np.array = gk_posts_mid - wanted_post
        vec_post_to_mid = utils.normalize_vec(vec_post_to_mid)

        target = wanted_post + vec_post_to_mid * 1.5

        return target

    def step(self, field: dict, is_blue_x_positive: bool, enemy_gk: Robot):

        # Compute target
        # -- Note : I put our team's GK for testing here, replace with 'not is_blue_x_positive' on real settings
        enemy_gk_score_area: dict[str, np.ndarray] = determine_goal_area(field, is_blue_x_positive)

        # Determine the goal posts of the enemy
        # -- Putting top right and bottom right wouldn't work if we switch sides
        # -- but eh, it's precise enough anyway
        enemy_gk_posts = np.array([enemy_gk_score_area["top_right"]] + [enemy_gk_score_area["bottom_right"]])
        target: np.ndarray = self.__determine_shoot_target_to_goal(enemy_gk_posts, enemy_gk)

        ball: np.array = self.__manager.ball

        # Compute pos to go to behind ball to aim towards target
        pre_shoot_pos = self.__compute_preshoot_pos(target=target, ball=ball)

        # Core of the decision between moving to shoot pos, and going for a shoot
        # True if vec angle from robot to ball is approximately equal to vec angle from ball to target
        prepared_to_shoot = np.isclose(utils.angle_towards(src=ball, dst=target), utils.angle_towards(self.__robot.position, ball), rtol=np.deg2rad(15))

        if not prepared_to_shoot:
            print("[PRE-SHOOT POS] Placing")
            self.__manager.go_to(self.__robot, *pre_shoot_pos)

        else:
            if np.linalg.norm(ball - self.__robot.position) < 0.15:
                print("Kicking ball")
                # TODO: wrap around an async timer to not trigger multiple kicks over a second
                self.__manager.go_to(self.__robot, *ball, utils.angle_towards(src=self.__robot.position, dst=target), kick=KICK.STRAIGHT_KICK, charge=True, dribble=2, power=4)
            else:
                # Run towards ball
                print("Going to ball")
                vec_forward_ball = utils.normalize_vec(ball - self.__robot.position)
                self.__manager.go_to(self.__robot, *(ball + vec_forward_ball), utils.angle_towards(src=self.__robot.position, dst=target))
