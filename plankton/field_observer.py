import numpy as np


class FieldObserver:

    def __init__(self):
        self.__ball_history: np.ndarray = np.array([0., 0.], ndmin=2)
        self.__ball_traj_m_p: tuple[float, float] = (0, 0)
        self.__ball_moving: bool = False

    def __update(self, ball: tuple[float, float]):
        if len(self.__ball_history) >= 40:
            self.__ball_history = np.delete(self.__ball_history, 0, axis=0)
        self.__ball_history = np.append(self.__ball_history, np.array(ball, ndmin=2), axis=0)

    def __check_ball_moving(self):
        self.__ball_moving = (np.std(self.__ball_history, axis=0) > 0.1).any()  # TODO: affine this number
        # print(self.__ball_moving)
        # print(np.std(self.__ball_history, axis=0))

    def __compute_ball_traj(self):
        m, p = reversed(np.polynomial.polynomial.polyfit(
            [ball[0] for ball in self.__ball_history],
            [ball[1] for ball in self.__ball_history],
            1
        ))
        self.__ball_traj_m_p = m, p

    def get_data(self):
        return {
            "ball_traj__m_p": self.__ball_traj_m_p,
            "ball_history": self.__ball_history,
            "ball_moving": self.__ball_moving
        }

    def step(self, ball: tuple[float, float]):
        self.__update(ball)
        self.__check_ball_moving()
        self.__compute_ball_traj()
