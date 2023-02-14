from manager import Manager
from field_observer import FieldObserver
from goalkeeper import GoalKeeper
from striker import Striker
from plankton_client import Client
from sys import argv


class ExampleManager(Manager):

    def __init__(self, c: Client):
        super().__init__(c)
        self.__field_observer = FieldObserver()
        self.__goalkeeper = GoalKeeper(self, self.robots["allies"][0], self.field, self.blue_on_positive_half)
        self.__striker = Striker(self, self.robots["allies"][4])

    def step(self):
        self.__field_observer.step(self.ball, self.robots, self.field, self.blue_on_positive_half)
        self.__goalkeeper.step(self.__field_observer.get_data())
        self.__striker.step(self.field, self.blue_on_positive_half, self.__field_observer.get_data()["goalkeepers"]["allies"])


if __name__ == "__main__":
    is_yellow = len(argv) > 1 and argv[1] == '-y'
    with Client(is_yellow) as client:
        manager = ExampleManager(c=client)
        manager.run()
