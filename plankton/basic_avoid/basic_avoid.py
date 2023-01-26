import numpy as np

from .basic_avoid_consts import danger_circle_radius
from .basic_avoid_types import Circle
from .basic_avoid_utils import angle_towards, compute_intersections, compute_waypoint
from manager import Manager
from plankton_client import Robot

global ally, enemy, crab_minion


def declare_robots(manager: Manager):
    global ally, enemy, crab_minion
    ally = manager.robots["allies"][0]
    enemy = manager.robots["allies"][1]
    crab_minion = manager.robots["allies"][2]


def ally_goto_and_avoid(manager: Manager, robot: Robot, dst: np.array, avoid):
    """
    Send a goto command to the 'ally' robot by avoiding the enemy robot, which will compute
    extra waypoints to go to if necessary
    """

    # Save the source position of the robot
    src = robot.position

    # Get the danger circle of the enemy
    dgr_circle = Circle(
        avoid.position,
        danger_circle_radius
    )

    _, is_circle_crossed = compute_intersections(circle=dgr_circle, line=(src, dst))
    if not is_circle_crossed or np.linalg.norm(src - dst) < np.linalg.norm(avoid.position - dst):
        print("Direct run")
        manager.go_to(robot, dst[0], dst[1], 0.)
    else:
        print("Going to waypoint")
        waypoint = compute_waypoint(circle=dgr_circle, line=(src, dst))

        # Go to waypoint
        manager.go_to(robot, waypoint[0], waypoint[1], 0.)


def step(manager: Manager):
    declare_robots(manager)
    ally_goto_and_avoid(manager, robot=ally, dst=crab_minion.position, avoid=enemy)
