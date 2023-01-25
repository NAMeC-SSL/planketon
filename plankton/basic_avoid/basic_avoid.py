import numpy as np

from .basic_avoid_consts import danger_circle_radius
from .basic_avoid_types import Point, Circle
from .basic_avoid_utils import angle_towards
from manager import Manager
from plankton_client import Robot

global ally, enemy, crab_minion


def declare_robots(manager: Manager):
    global ally, enemy, crab_minion
    ally = manager.robots["allies"][0]
    enemy = manager.robots["allies"][1]
    crab_minion = manager.robots["allies"][2]


def visualize_circle(manager: Manager, robot: Robot, radius: float):
    """
    Moves the enemy robot around the edges of its danger circle
    in grSim. This is pure visualization, but also very slow.
    """
    print("Visualizing danger circle..")
    x_rob, y_rob = robot.position

    # Place on 4 edges of circle
    for deg in range(0, 360, 90):
        x = x_rob + (radius * np.sin(np.deg2rad(deg)))
        y = y_rob + (radius * np.cos(np.deg2rad(deg)))
        manager.go_to(robot, x, y, float(angle_towards(Point(x, y), Point(x_rob, y_rob))))

    # Back to spawn
    manager.go_to(robot, x_rob, y_rob, 0.)


def ally_goto_and_avoid(manager: Manager, robot: Robot, dst: Point, avoid, atol: float):
    """
    Send a goto command to the 'ally' robot by avoiding the enemy robot, which will compute
    extra waypoints to go to if necessary
    """

    print("Starting 'avoid-like' goto...")

    # Save the source position of the robot
    src = Point(robot.position[0], robot.position[1])

    # Get the danger circle of the enemy
    dgr_circle = Circle(
        Point(avoid.position[0], avoid.position[1]),
        danger_circle_radius
    )

    _, is_circle_crossed = compute_intersections(circle=dgr_circle, line=(src, dst))
    if not is_circle_crossed:
        print("No avoiding necessary, just go to the position")
        manager.go_to(robot, dst.x, dst.y, orientation=0.)
    else:
        waypoint = compute_waypoint(circle=dgr_circle, line=(src, dst))

        # Go to waypoint
        while not np.isclose(
            np.array(*robot.position),
            np.array(*waypoint),
            atol=atol
        ):
            manager.go_to(robot, waypoint.x, waypoint.y, 0.)
        print("     - Waypoint attained")

        # Go to destination
        while not np.isclose(
            np.array(*robot.position),
            np.array(*dst),
            atol=atol
        ):
            manager.go_to(robot, dst.x, dst.y, 0.)
        print("     - Destination attained attained")


def step(manager: Manager):
    declare_robots(manager)
    ally_goto_and_avoid(manager, robot=ally, dst=Point(*crab_minion.position), avoid=enemy, atol=0.1)
    print("finished !")
    exit(0)

