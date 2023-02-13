from typing import Callable

import numpy as np


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
        (rectangle["bottom_left"] <= point).all() and (point <= rectangle["top_left"]).all() \
        and \
        (rectangle["bottom_right"] <= point).all() and (point <= rectangle["top_right"]).all()
