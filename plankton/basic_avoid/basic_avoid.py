import numpy as np

from .basic_avoid_consts import danger_circle_radius
from .basic_avoid_types import Circle
from .basic_avoid_utils import angle_towards, compute_intersections, compute_waypoint, danger_circle, distance
from manager import Manager
from plankton_client import Robot

global ally, enemy, crab_minion


def declare_robots(manager: Manager):
    global ally, enemy, crab_minion
    ally = manager.robots["allies"][0]
    enemy = manager.robots["allies"][1]
    crab_minion = manager.robots["allies"][2]


def goto_avoid(manager: Manager, robot: Robot, dst: np.array, avoid_list: list[Robot]):
    """
    Send a goto command to the 'ally' robot by avoiding the enemy robot, which will compute
    extra waypoints to go to if necessary
    """

    # Save the source position of the robot
    src = robot.position
    waypoints = []

    # Compute waypoints to avoid each robot in the avoid list
    for enn in avoid_list:
        dgr_circle = danger_circle(enn)
        _, is_circle_crossed = compute_intersections(circle=dgr_circle, line=(src, dst))

        if is_circle_crossed:
            if np.linalg.norm(dst - src) > np.linalg.norm(enn.position - src):
                print(f"enn pos : {enn.position}")
                print(f"enn dist : {np.linalg.norm(enn.position - src)}")
                print(f"dst dist : {np.linalg.norm(dst - src)}")
                waypoints.append(compute_waypoint(circle=dgr_circle, line=(src, dst)))
                print(f"waypoints : {waypoints}")

    # If there are waypoints to go to
    if len(waypoints) > 0:
        # Get all distances from source point to each waypoint
        dist_to_robot = lambda xy: distance(src, xy)
        wp_dists = list(map(dist_to_robot, waypoints))
        # And only grab closest waypoint to go to
        index_min_dst = min(range(len(wp_dists)), key=wp_dists.__getitem__)
        wp = waypoints[index_min_dst]

        print("going to waypoint")
        print(f"real waypoint : {wp}")
        # manager.go_to(robot, wp[0], wp[1], 0.)
    else:
        # Otherwise you go to the destination
        print("straight to dst")
        # manager.go_to(robot, dst[0], dst[1], 0.)


def visualize_circle(manager:Manager, robot: Robot, circle: Circle):
    """
    Moves the enemy robot around the edges of its danger circle
    in grSim. This is pure visualization, but also very slow.
    """
    print("Visualizing danger circle..")
    x_rob, y_rob = robot.position
    radius: float = circle.r
    # Place on 4 edges of circle
    for deg in range(0, 360, 90):
        x = x_rob + (radius * np.sin(np.deg2rad(deg)))
        y = y_rob + (radius * np.cos(np.deg2rad(deg)))
        manager.go_to(robot, x, y, float(angle_towards(np.array([x, y]), np.array([x_rob, y_rob]))))


def step(manager: Manager):
    declare_robots(manager)
    # visualize_circle(manager, manager.robots["enemies"][0], danger_circle(manager.robots["enemies"][0]))

    # roots, inter = compute_intersections(
    #     danger_circle(manager.robots["enemies"][0]),
    #     (manager.robots["allies"][0].position, manager.robots["allies"][2].position)
    # )
    # print(inter)
    goto_avoid(manager, robot=ally, dst=crab_minion.position, avoid_list=manager.robots["enemies"][:6])
