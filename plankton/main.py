from manager import Manager
from plankton_client import Client,Command
from sys import argv
from basic_avoid import basic_avoid
class ExampleManager(Manager):
    def step(self):
        basic_avoid.step(self)


if __name__ == "__main__":
    is_yellow = len(argv) > 1 and argv[1] == '-y'
    with Client(is_yellow) as client:
        manager = ExampleManager(client=client)
        manager.run()
