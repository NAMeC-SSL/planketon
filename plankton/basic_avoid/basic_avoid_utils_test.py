from basic_avoid_types import Point, Circle
from basic_avoid_utils import compute_intersections
import unittest


class BasicAvoidUtilsTest(unittest.TestCase):
    def test_compute_intersections(self):
        """
        Checks if basic_avoid_utils.compute_intersections() works properly
        You can visualize the functions easily by going on https://www.numworks.com/simulator/
        and use the 'Grapher' app on the website !
        """
        # -- Case 1 should fail, line doesn't cross circle --
        # Corresponding functions :
        #   Circle : (x-2)² + (y-3)² - 1 = 0
        #   Line   : 2x+3
        c1 = Circle(Point(2, 3), 1)
        l1_start = Point(-3, -3)
        l1_end = Point(3, 9)

        # Testing
        roots, sol_found = compute_intersections(circle=c1, line=(l1_start, l1_end))
        self.assertFalse(sol_found)

        # -- Case 2 should pass, line crosses circle --
        # Corresponding functions :
        #   Circle : (x-2)² + (y-3)² - 4 = 0
        #   Line   : 2x+3
        c2 = Circle(Point(2, 3), 4)
        l2_start = Point(-3, -3)
        l2_end = Point(3, 9)

        # Testing
        roots, sol_found = compute_intersections(circle=c2, line=(l2_start, l2_end))
        self.assertTrue(sol_found)


if __name__ == '__main__':
    unittest.main()
