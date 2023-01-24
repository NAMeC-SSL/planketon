from manager import Manager
from plankton_client import Client,Command
from sys import argv
from math import atan2

class ExampleManager(Manager):
    def step(self):
        # self.go_to(self.allies1, x=0.0, y=0.0, orientation=0.0)
        # print("test")
        # self.go_to(self.allies1, x=0.0, y=0.0, orientation=0.0)
        # self.go_to(self.allies1, )
        # self.control(self.allies2, forward_velocity=1.0, left_velocity=0.0, angular_velocity=0.0)
        # self.client.commands.append(Command(id=0, forward_velocity=1.0, angular_velocity=0.0))
        # self.client.commands.append(Command(id=1, forward_velocity=1.0, angular_velocity=1.0))
        # print(self.ball)
        self.go_to(self.allies1, x=0.0, y=0.0, orientation=self.angleTo(self.allies1.position, self.ball))
        
    def angleTo(self, p1, p2):
        v = p1 - p2
        return atan2(-v[1], -v[0])


if __name__ == "__main__":
    is_yellow = len(argv) > 1 and argv[1] == '-y'
    with Client(is_yellow) as client:
        manager = ExampleManager(client=client)
        manager.run()
