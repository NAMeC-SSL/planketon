from manager import Manager
from plankton_client import Client,Command, KICK
from sys import argv
from math import atan2,cos, sin
import numpy as np


def ccw( A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect
def intersect( A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

def rotateVector(v, theta):
    rot = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])   
    return np.dot(rot, v)

class ExampleManager(Manager):
    def step(self):
        nearestId = 0
        nearestDist = 100
        for i in range(6):
            if not self.allie(i):continue
            self.initEnv(i)

            #get nearset robot to ball
            d = self.distToBall(i)
            if d < nearestDist:
                nearestId = i
                nearestDist = d

            #reset velo and angle
            self.control(self.allie(i), forward_velocity=0.0, left_velocity=0.0, angular_velocity=0.0)
        id = nearestId

        toTarget = self.goalTarget(id) - self.ball
        toTarget = -(normalize(toTarget)*0.1) #0.1 = dist to ball
        shootingPos = toTarget + self.ball
        
        kick = self.wantToKick(id)
        self.go_to(self.allie(id), x=shootingPos[0], y=shootingPos[1], orientation=self.angleTo(self.allie(id).position, self.ball), kick=kick, power=10, dribble=0)

    def allie(self, id):
        return self.robots['allies'][id]

    def wantToKick(self, id):
        targetDir = rotateVector(np.array([1, 0]), self.allie(id).orientation)

        goalX = np.array([-self.allie(id).side * self.field['length']/2, self.field['goal_width']/2.4])
        goalY = np.array([-self.allie(id).side * self.field['length']/2, -self.field['goal_width']/2.4])

        inGoal = intersect(self.allie(id).position, self.allie(id).position + targetDir * 10, goalX, goalY)
        print(inGoal, self.distToBall(id) < 0.11)
        return KICK.STRAIGHT_KICK if (self.distToBall(id) < 0.11 and inGoal) else KICK.NO_KICK

    def distToBall(self, id):
        return np.linalg.norm(self.allie(id).position - self.ball)

    def goalTarget(self, id):
        x = -self.allie(id).side * self.field['length']/2
        y = 0
        print(np.array([x,y]))
        return np.array([x,y])

    def initEnv(self, id):
        if not hasattr(self.allie(id), "side"):
            self.allie(id).side = 1 if self.allie(id).position[0] > 0 else -1
            self.allie(id).role = ''
    
    def angleTo(self, p1, p2):
        v = p1 - p2
        return atan2(-v[1], -v[0])


if __name__ == "__main__":
    is_yellow = len(argv) > 1 and argv[1] == '-y'
    with Client(is_yellow) as client:
        manager = ExampleManager(client=client)
        manager.run()
