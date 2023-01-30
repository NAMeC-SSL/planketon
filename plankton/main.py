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
    roles = {"goal": [], "defender": [], "attacker": []}
    def allie(self, id):
        """ 
            Get the robot obj with ID
        """
        return self.robots['allies'][id]

    def step(self):
        """
            Main loop
        """
        self.initEnv()

        self.attack()
        self.goal()
        self.defende()

        # for id in self.order:
        #     if self.allie(id).position is None:continue # check if bot exist
        #     match self.allie(id).role:
        #         case 'goal':
        #             self.goal(id)
        #         case 'defender':
        #             self.defende(id)
        #         case 'attacker': self.attack(id)

    def closestAttacker(self):
        minId = -1
        minDist = 100
        for attackerId in self.roles['attacker']:
            d = self.distToBall(attackerId)
            if d < minDist:
                minId = attackerId
                minDist = d
        return minId

    def attack(self):
        id = self.closestAttacker()
        if id == -1:return
        if self.distToBall(id) < 0.11 :self.allie(id).status = 'dribbling'
        else:self.allie(id).status = ''
        match self.allie(id).status:
            case 'dribbling':
                self.dribbling(id)
            case '': 
                self.goToBall(id)

    def defende(self):
        for i in range(len(self.roles['defender'])):
            id = self.roles['defender'][i]
            w=self.field['width'] 
            r = w/ len(self.roles['defender'])
            (-w/2)+r*i
            (-w/2)+r*(i+1)

            y = min(max(self.ball[1], (-w/2)+r*i), (-w/2)+r*(i+1))
            self.go_to(self.allie(id),x=self.allie(id).side, y=y, orientation=self.angleTo(self.allie(id).position, self.ball))
       
    def goal(self):
        if len(self.roles['goal']) == 0:return
        id = self.roles['goal'][0]
        if self.allie(id).position[1] > 0:
            self.go_to(self.allie(id),x=self.allie(id).side*(self.field['length']+0.1), y=min(self.ball[1], self.field['goal_width']/2), orientation=self.angleTo(self.allie(id).position, self.ball))
        else :
            self.go_to(self.allie(id),x=self.allie(id).side* (self.field['length']+0.1), y=max(self.ball[1], -self.field['goal_width']/2), orientation=self.angleTo(self.allie(id).position, self.ball))
       
        # if (abs(( bot.side* constants.field_length/2) - client.ball[0]) < constants.robot_tag_size + 0.1):
        #     bot.goto((client.ball[0],client.ball[1],o))
        #     bot.kick()

    def dribbling(self, id):      
        kick = self.wantToKick(id)
        self.go_to(self.allie(id),x=self.allie(id).position[0],y=self.allie(id).position[1], orientation=self.angleTo(self.allie(id).position, self.ball), kick=kick, power=3, dribble=1)

    def goToBall(self, id):
        toTarget = self.goalTarget(id) - self.ball
        toTarget = -(normalize(toTarget)*0.1) # 0.1 = dist to ball
        shootingPos = toTarget + self.ball
        self.go_to(self.allie(id), x=shootingPos[0], y=shootingPos[1], orientation=self.angleTo(self.allie(id).position, self.ball))    

    def wantToKick(self, id):
        targetDir = rotateVector(np.array([1, 0]), self.allie(id).orientation)

        goalX = np.array([-self.allie(id).side * self.field['length']/2, self.field['goal_width']/2.4])
        goalY = np.array([-self.allie(id).side * self.field['length']/2, -self.field['goal_width']/2.4])

        inGoal = intersect(self.allie(id).position, self.allie(id).position + targetDir * 10, goalX, goalY)

        return KICK.STRAIGHT_KICK if (self.distToBall(id) < 0.11 and inGoal) else KICK.NO_KICK

    def distToBall(self, id):
        return np.linalg.norm(self.allie(id).position - self.ball)

    def goalTarget(self, id):
        x = -self.allie(id).side * self.field['length']/2
        y = 0
        return np.array([x,y])

    def initEnv(self):
        """
            Give roles
        """
        if not hasattr(self, "order"): self.order = self.getBotOrder()

        for i in range(len(self.order)):
            id = self.order[i]
            if not hasattr(self.allie(id), "side"): self.allie(id).side = 1 if self.allie(id).position[0] > 0 else -1
            if not hasattr(self.allie(id), "role"): 
                if i == 0: 
                    self.roles['goal'].append(id)
                    self.allie(id).role = 'goal'
                elif i == len(self.order) - 1 or i == len(self.order) - 2: 
                    self.roles['attacker'].append(id)
                    self.allie(id).role = 'attacker'
                    if self.distToBall(id) < 0.11 :self.allie(id).status = 'dribbling'
                    else:self.allie(id).status = ''
                else: 
                    self.roles['defender'].append(id)
                    self.allie(id).role = 'defender'
            if not hasattr(self.allie(id), "status"): self.allie(id).status = ''
            # self.control(self.allie(i), forward_velocity=0.0, left_velocity=0.0, angular_velocity=0.0)

    
    def getBotOrder(self):
        """
            Return a list of the bot id order (from the nearest of the end the field)
        """
        order=[]
        for i in range(6):
            if self.allie(i).position is None:continue
            pos = 0
            while pos<len(order) and (abs(self.allie(i).position[0])) < (abs(self.robots['allies'][order[pos]].position[0])):
                pos+=1
            order.insert(pos, i)
        return order

    def angleTo(self, p1, p2):
        v = p1 - p2
        return atan2(-v[1], -v[0])

if __name__ == "__main__":
    is_yellow = len(argv) > 1 and argv[1] == '-y'
    with Client(is_yellow) as client:
        manager = ExampleManager(client=client)
        manager.run()
