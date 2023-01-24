from manager import Manager
from plankton_client import Client,Command
from sys import argv

class ExampleManager(Manager):
    def step(self):
        print("test")
        self.go_to(self.allies1, x=0.0, y=0.0, orientation=0.0)
        # self.go_to(self.allies1, )
        self.control(self.allies2, forward_velocity=1.0, left_velocity=0.0, angular_velocity=0.0)
        # self.client.commands.append(Command(id=0, forward_velocity=1.0, angular_velocity=0.0))
        # self.client.commands.append(Command(id=1, forward_velocity=1.0, angular_velocity=1.0))
        print(self.ball)
        print(self.allies1)


if __name__ == "__main__":
    is_yellow = len(argv) > 1 and argv[1] == '-y'
    with Client(is_yellow) as client:
        manager = ExampleManager(client=client)
        manager.run()
