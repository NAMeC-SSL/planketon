import numpy as np


class Circle:
    """
    Circle class
    Note that the 'center' attribute should be of type Point
    I don't enforce this, but please do it
    """
    def __init__(self, center: np.array, r: float):
        self.center: np.array = center
        self.r: float = r
