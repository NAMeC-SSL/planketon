import numpy as np
from scipy.optimize import fsolve as scipy_fsolve
from .basic_avoid_types import Point, Circle
from typing import Callable


def traj_function(a: Point, b: Point, general_form=False) -> Callable[[float, [float]], float]:
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
    if np.isclose([b.y - a.y], [0.]):
        m = 1
    else:
        m = (b.y - a.y) / (b.x - a.x)

    # Use point a to solve the ordinate of the origin of the function
    # Because y = m*x + p ; y - m*x = p
    p: float = a.y - m * a.x
    if general_form:
        return lambda x, y: m*x + p - y
    return lambda x: m*x + p


def circle_gen_eq(center: Point, r: float) -> Callable[[float, float], float]:
    """
    Returns the general form of the equation of a circle
    Tip : general form is an equation equal to  0
    """
    return lambda x, y: np.power(x - center.x, 2) + np.power(y - center.y, 2) - np.power(r, 2)


def angle_towards(src: Point, dst: Point) -> float:
    """
    Returns the angle in radian from one point towards another one point
    """
    return np.arctan2(
        dst.y - src.y,
        dst.x - src.x
    )


def compute_intersections(circle: Circle, line: tuple[Point, Point]) -> tuple[np.ndarray, bool]:
    """
    Using a circle and the source and two distinct points of a line, computes
    the number of crossing points between the circle and the line.

    To do this, it computes and uses the general equation of the given circle : (x - h)² + (y - k)² - r² = 0
    and the general form of the affine function : m*x + p - y = 0

    The order of given points in the 'line' argument is important :
        First is source point
        Second is destination point
    """

    # Compute straight line trajectory
    # Important : set general_form to True to make it compliant with scipy.optimize.fsolve
    line_fc = traj_function(line[0], line[1], general_form=True)

    # Compute circle trajectory
    circle_fc = circle_gen_eq(circle.center, circle.r)

    # Use scipy.optimize.fsolve to get the intersection point(s)
    # This solves the equation circle_fc = line_fc
    # effectively computing the intersection points
    # The function might not find a proper root. We ask for the full output of the function
    # and only grab the returned roots and a special return value.

    equation = lambda xy: [line_fc(xy[0], xy[1]), circle_fc(xy[0], xy[1])]
    roots, _, retval, _ = scipy_fsolve(equation, np.zeros(2), full_output=True)

    # The variable retval should be set to 1 if correct roots have been found
    solution_found = retval == 1

    return roots, solution_found


def compute_waypoint(circle: Circle, line: tuple[Point, Point], forward_theta_delta=10) -> Point:
    """
    Given a specific danger circle and two source and destination points,
    determines a waypoint to go to avoid said circle.

    The order of given points in the 'line' argument is important :
        First is source point
        Second is destination point
    TODO: change line param to vector
    TODO: refactor this mess, lots of rad->deg and deg->rad conversions everywhere

    This works by determining an orthogonal vector starting at the center of the danger circle
    towards the given line.
        Such is done by drawing a triangle, where the hypotenuse is the source point towards
        the circle center. We know that one angle will be of 90°, so we can calculate the last
        angle towards the line. This will be the angle of the vector

    Using the formula of this newfound vector, we can find the intersection of the vector with the line
    and compute the waypoint towards this intersection

    Note : every angle calculated here is in the range [0, 360]
           np.rad2deg() can output negative values, we cast the result mod 360
    TODO: thoroughly test this function
    """

    # Calculate the angle DSC (dst -> src -> center of circle)
    SC_theta = np.rad2deg(angle_towards(line[0], circle.center)) % 360
    SD_theta = np.rad2deg(angle_towards(line[0], line[1])) % 360
    DSC_angle = abs(SC_theta - SD_theta)  # Could fail if both angles are the same. What to do if this happens ?

    # We now need the angle of the vector that should go towards the line
    # Using the fact that sum of all angles of a triangle is 180, we know one given angle
    # and since we're looking for a right-angled triangle, last angle can be computed
    last_triangle_angle = 180 - DSC_angle - 90

    # Angle needs to be adapted to find the resulting vector
    angle_sign = 1 if (circle.center.x >= line[0].x and circle.center.y >= line[0].y) else -1
    CS_theta = np.rad2deg(angle_towards(circle.center, line[0])) % 360  # Same as SC_theta + np.pi ?

    # Angle from circle center towards line is only the center->src angle plus
    # the computed angle of the triangle
    waypoint_vec_theta = np.deg2rad(CS_theta + (last_triangle_angle * angle_sign))

    # Adding a small delta to the angle to make the waypoint a bit closer to the destination point
    waypoint_vec_theta += np.deg2rad((forward_theta_delta * angle_sign))

    # Using the circle's center point, and the found angle towards the line, we can compute
    # another point that is aligned to the vector
    r: float = 42.  # Arbitrary length, the value itself isn't important, but must be > 1
    aligned_pt: Point = Point(
        circle.center.x + (r * np.cos(waypoint_vec_theta)),  # | Polar to cartesian coordinates conversion
        circle.center.y + (r * np.sin(waypoint_vec_theta))   # | x = r * cos(theta)  and  y = r * sin(theta)
    )

    # Get intersection between calculated vector and danger circle, which is the effective waypoint to attain
    waypoint, _ = compute_intersections(circle=circle, line=(circle.center, aligned_pt))

    # Convert waypoints into Point objects, better style-wise =)
    waypoint = Point(waypoint[0], waypoint[1])

    return waypoint
