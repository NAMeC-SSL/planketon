from typing import Callable

import numpy as np

from plankton_client import Robot


def angle_towards(src: np.array, dst: np.array) -> float:
    """
    Returns the angle in radian from one point towards another one point
    """
    return np.arctan2(
        dst[1] - src[1],
        dst[0] - src[0],
    )


def traj_function(a: np.array, b: np.array, general_form=False) -> Callable[[float, [float]], float]:
    """
    Computes the lambda function describing a straight line
    trajectory from point a to point b
    Returns :
        A lambda function representing the slope-intercept
        equation form, as y = m * x + p
    Optional parameter : general_form
        Set to True to return the general form of the equation lambda function.
    """
    m: float = -1

    # Can't create a vertical line function
    # Approximating it using a very low slope coefficient when both x coordinates are close
    # TODO: create a test case for this approximation
    if np.isclose(b[0] - a[0], [0.], rtol=0.1).all():
        m = 0.000001
    else:
        m = (b[1] - a[1]) / (b[0] - a[0])

    # Use point a to solve the ordinate of the origin of the function
    # Because y = m*x + p ; y - m*x = p
    p: float = a[1] - m * a[0]
    if general_form:
        return lambda x, y: m * x + p - y
    return lambda x: m * x + p


def point_in_rectangle(point: np.array, rectangle: dict[str, np.ndarray]):
    return \
        rectangle["bottom_left"][0] <= point[0] and rectangle["bottom_left"][1] <= point[1] and \
        rectangle["bottom_right"][0] >= point[0] and rectangle["bottom_right"][1] <= point[1] and \
        rectangle["top_right"][0] >= point[0] and rectangle["top_right"][1] >= point[1] and \
        rectangle["top_left"][0] <= point[0] and rectangle["top_left"][1] >= point[1]


def closest_to_target(robots: list[Robot], target: np.array) -> Robot:
    """
    Return the point that is the closest to the given destination point
    """
    if len(robots) == 1:
        return robots[0]

    points = [r.position for r in robots]

    # the None coalescing op is required to avoid subtracting to None
    # replaces None with absurdly far coordinates
    dist_to_target = lambda xy: np.linalg.norm(target - (xy if xy is not None else np.array([-100, -100])))
    distances_map = list(map(dist_to_target, points))
    index_min_dist = min(range(len(distances_map)), key=distances_map.__getitem__)
    return robots[index_min_dist]
