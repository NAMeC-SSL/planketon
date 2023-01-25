class Point:
    """
    Point class
    Is there much to say about it ?
    """
    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    def __getitem__(self, item):
        match item:
            case 0:
                return self.x
            case 1:
                return self.y
            case _:
                raise IndexError


class Circle:
    """
    Circle class
    Note that the 'center' attribute should be of type Point
    I don't enforce this, but please do it
    """
    def __init__(self, center: Point, r: float):
        self.center: Point = center
        self.r: float = r
