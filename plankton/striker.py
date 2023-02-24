from builtins import classmethod

import numpy as np

from field_observer import FieldObserver
import utils
from manager import Manager
from goalkeeper import determine_goal_area
from plankton_client import Robot, KICK


class Striker:
    # Determines how much the angle difference should be to consider
    # that robot is "behind" a given position
    DEG_DIFF_GO_BEHIND = 100
    # Multiplies the vector
    MULT_GO_BEHIND = 2
    # Maximum difference of degrees of offset to consider that we're aiming towards the target
    DEG_DIFF_TARGET_ALIGN = 10
    # Minimum distance for the robot to consider shooting instead of running towards the ball
    SHOOT_MIN_DIST_FROM_BALL = 0.29
    # If distance from ball is inferior to k, we consider that we currently have the ball
    DIST_HAS_BALL = 0.095
    # Maximum degree of difference between wanted shoot position and real position
    DEG_DIFF_FOR_PLACEMENT = 15
    # Multiplier for the vector that determines where to shoot the ball to score
    # The higher it is, the closer to the center of the goal area the target will be
    # (a value too high might make it go outside the goal area, so watch out)
    GOAL_TARGET_MULTIPLIER = 0.8
    # Multiplies the normalized vector determining how far should we be from
    # the ball before commencing run & shoot sequences
    DIST_PLACEMENT_BEHIND_BALL_MULTIPLIER = 1  # TODO: doesn't work, fix for negative coordinates vector

    def __init__(self, manager: Manager, robot: Robot):
        self.__manager: Manager = manager
        self.__robot = robot

    def __compute_preshoot_pos(self, target: np.array, ball: np.array) -> np.array:
        """
        Compute the position in (x, y) to where the robot should position itself
        to be just in front of the ball, aiming towards a certain position.
        """
        # Vector from target (where the ball should go) towards ball
        target_to_ball: np.array = ball - target

        # Normalize the vector
        target_to_ball = utils.normalize_vec(target_to_ball)

        # Change the vector's origin to start from the ball
        position_pre_shoot: np.array = ball + target_to_ball * Striker.DIST_PLACEMENT_BEHIND_BALL_MULTIPLIER
        position_pre_shoot_angle = utils.angle_towards(self.__robot.position, ball)
        return np.array([position_pre_shoot[0], position_pre_shoot[1], position_pre_shoot_angle])

    def __determine_shoot_target_to_goal(self, enemy_goal_posts: np.ndarray[np.ndarray], enemy_gk: Robot) -> np.ndarray:
        """
        Computes a point towards which the ball should go

        Parameters :
            goal_posts | Coordinates of left and right enemy goal posts
            enemy_robs | List of ClientRobot objects representing the enemy positions

        Returns :
            A 2-dimensional np array, the coordinates of the target to aim towards
        """

        # Find which post the enemy goalkeeper is farthest from
        wanted_post: np.array = enemy_goal_posts[0]
        if np.linalg.norm(enemy_goal_posts[0] - enemy_gk.position) >= np.linalg.norm(enemy_goal_posts[1] - enemy_gk.position):
            wanted_post: np.array = enemy_goal_posts[1]

        gk_posts_mid: np.array = (enemy_goal_posts[0] + enemy_goal_posts[1]) / 2

        # Apply a small offset to the wanted post
        # # TODO: another offset to put the target inside the goal posts
        vec_post_to_mid: np.array = gk_posts_mid - wanted_post
        vec_post_to_mid = utils.normalize_vec(vec_post_to_mid)

        target: np.array = wanted_post + vec_post_to_mid * Striker.GOAL_TARGET_MULTIPLIER
        print(target)
        return target

    def step(self, field: dict, is_blue_x_positive: bool, enemy_gk: Robot):
        ball: np.array = self.__manager.ball

        # Compute target
        # -- Note : I put our team's GK for testing here, replace with 'not is_blue_x_positive' on real settings
        enemy_gk_score_area: dict[str, np.ndarray] = determine_goal_area(field, is_blue_x_positive)

        # Determine the goal posts of the enemy
        # -- Putting top right and bottom right wouldn't work if we switch sides
        # -- but eh, it's precise enough anyway
        enemy_gk_posts = np.array([enemy_gk_score_area["top_right"]] + [enemy_gk_score_area["bottom_right"]])

        target: np.ndarray = self.__determine_shoot_target_to_goal(enemy_gk_posts, enemy_gk)

        # Compute pos to go to behind ball to aim towards target
        pre_shoot_pos: np.array = self.__compute_preshoot_pos(target=target, ball=ball)

        # Core of the decision between moving to shoot pos, and going for a shoot
        # True if vec angle from robot to ball is approximately equal to vec angle from ball to target

        angle_ball_to_target = utils.angle_towards(src=ball, dst=target)
        angle_robpos_to_ball = utils.angle_towards(self.__robot.position, ball)
        angle_diff_shoot_pos: float = np.rad2deg(abs(angle_ball_to_target - angle_robpos_to_ball))

        prepared_to_shoot = angle_diff_shoot_pos <= Striker.DEG_DIFF_FOR_PLACEMENT

        # Decision taker for the Striker
        if not prepared_to_shoot:
            if angle_diff_shoot_pos >= Striker.DEG_DIFF_GO_BEHIND:
                # Move pre-shoot pos a little further to allow going behind ball
                far_behind_ball = pre_shoot_pos * Striker.DIST_PLACEMENT_BEHIND_BALL_MULTIPLIER
                print(f"{pre_shoot_pos} | {far_behind_ball}")
                print("[STRIKER - GO BEHIND BALL] Getting behind ball")
                self.__manager.go_to(self.__robot, *far_behind_ball)

            else:
                print("[STRIKER - CLOSE PLACEMENT] Placing")
                self.__manager.go_to(self.__robot, *pre_shoot_pos)

        else:
            # If we're close to the ball
            close_to_ball = np.linalg.norm(ball - self.__robot.position) < Striker.SHOOT_MIN_DIST_FROM_BALL
            if close_to_ball:

                has_ball = np.linalg.norm(ball - self.__robot.position) < Striker.DIST_HAS_BALL
                # If we can consider that we possess the ball
                if has_ball:
                    aim_angle_accurate = \
                        abs(abs(utils.angle_towards(src=self.__robot.position, dst=target)) - abs(self.__robot.orientation)) < np.deg2rad(Striker.DEG_DIFF_TARGET_ALIGN)

                    small_vec_forward = utils.normalize_vec(target - self.__robot.position) * 0.4

                    # If we're not correctly aiming towards the target (+- a certain delta)
                    if not aim_angle_accurate:
                        print("[STRIKER - ALIGN] Aligning angle towards target")
                        self.__manager.go_to(self.__robot, *self.__robot.position,
                                             utils.angle_towards(src=self.__robot.position, dst=target))
                    # Otherwise we shoot
                    else:
                        print("[STRIKER - KICK] Kicking ball")
                        # TODO: wrap kick around an async timer to not trigger multiple kicks over a second
                        self.__manager.go_to(self.__robot, *(self.__robot.position + small_vec_forward),
                                             utils.angle_towards(src=self.__robot.position, dst=target),
                                             charge=True, kick=KICK.STRAIGHT_KICK   , power=5)
                # Otherwise, go grab the ball
                else:
                    print("[STRIKER - GRAB] Grabbing ball")
                    self.__manager.go_to(self.__robot, *ball, utils.angle_towards(src=self.__robot.position, dst=ball),
                                         charge=True, dribble=2)

            # Otherwise run towards ball
            else:
                print("[STRIKER - RUSHING] Going towards the ball")
                self.__manager.go_to(self.__robot, *ball, utils.angle_towards(src=self.__robot.position, dst=ball))
