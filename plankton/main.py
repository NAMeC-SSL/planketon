from manager import Manager
from plankton_client import Client,Command, KICK
from sys import argv
import numpy as np
from utils import *

class ExampleManager(Manager):
    roles = {"offense": [], "goal": [], "defender": [], "attacker": []}
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

        self.offense()
        self.attack()
        self.goal()
        self.defend()

    def closestAttacker(self):
        minId = -1
        minDist = 100
        for attackerId in self.roles['attacker']:
            d = self.distToBall(attackerId)
            if d < minDist:
                minId = attackerId
                minDist = d
        return minId

    def offense(self):
        distToGoal = 1.5
        id = self.roles['offense'][0]
        g = self.goalPos(id)
        v = self.ball - g
        v = normalize(v) * distToGoal + g
        self.go_to(self.allie(id) 
            ,x=v[0]
            ,y=v[1]
            ,orientation=angleTo(self.allie(id).position
            ,self.ball))

    def attack(self):
        id = self.closestAttacker()
        if id == -1:return
        if self.isDribbling(id):self.allie(id).status = 'dribbling'
        else:self.allie(id).status = ''
        match self.allie(id).status:
            case 'dribbling':
                self.dribbling(id)
            case '': 
                self.goToBall(id)

    def defend(self):
        for i in range(len(self.roles['defender'])):
            id = self.roles['defender'][i]
            w=self.field['width'] 
            r = w/ len(self.roles['defender'])
            y = min(max(self.ball[1], (-w/2)+r*i), (-w/2)+r*(i+1))
            self.go_to(self.allie(id),x=self.allie(id).side, y=y, orientation=angleTo(self.allie(id).position, self.ball))
       
    def goal(self):
        if len(self.roles['goal']) == 0:return
        id = self.roles['goal'][0]
        if self.allie(id).position[1] > 0:
            self.go_to(self.allie(id),x=self.allie(id).side*(self.field['length']/2-0.1), y=min(self.ball[1], self.field['goal_width']/2), orientation=angleTo(self.allie(id).position, self.ball))
        else :
            self.go_to(self.allie(id),x=self.allie(id).side*(self.field['length']/2-0.1), y=max(self.ball[1], -self.field['goal_width']/2), orientation=angleTo(self.allie(id).position, self.ball))
       
        # if (abs(( bot.side* constants.field_length/2) - client.ball[0]) < constants.robot_tag_size + 0.1):
        #     bot.goto((client.ball[0],client.ball[1],o))
        #     bot.kick()

    def isDribbling(self, id):
        return self.distToBall(id) < 0.12


    def dribbling(self, id):
        if not self.enemiesOnRoad(self.allie(id).position, self.goalPos(id)):
            kick = self.wantToKick(id)
            print("shoot", kick)
            self.go_to(self.allie(id),x=self.allie(id).position[0],y=self.allie(id).position[1], orientation=angleTo(self.allie(id).position, self.goalPos(id)), kick=kick, power=3, dribble=1)
        else:
            print("to allie", end=" ")
            if self.enemiesOnRoad(self.allie(id).position, self.allie(self.roles["offense"][0]).position):
                attackerPos = self.allie(self.roles["attacker"][otherAttacker]).position
                kick = self.abbleToKick(id, attackerPos)
                print("to other attacker")
                otherAttacker = 1 - self.roles["attacker"].index(id)
                self.go_to(self.allie(id), x=self.allie(id).position[0], y=self.allie(id).position[1],orientation=angleTo(self.allie(id).position, attackerPos), kick=KICK.STRAIGHT_KICK, power=3, dribble=1)
            else:
                kick = self.abbleToKick(id, attackerPos)
                print("to offenser")
                self.go_to(self.allie(id), x=self.allie(id).position[0], y=self.allie(id).position[1],orientation=angleTo(self.allie(id).position, self.allie(self.roles["offense"][0]).position), kick=KICK.STRAIGHT_KICK, power=3, dribble=1)
            #self.roles["attacker"] = []

    def enemiesOnRoad(self, pos1, pos2):
        botInAlignement = False
        for r in self.robots['enemies']:
            if r.position is None: continue
            botInAlignement = botInAlignement or line_intersection(
                r.position, 0.1, pos1, pos2
            ) != None
        return botInAlignement
    

    def goalPos(self, id):  
        return np.array([-self.allie(id).side * self.field['length']/2, 0])

    def goToBall(self, id):
        print("going to ball")
        toTarget = self.goalTarget(id) - self.ball
        toTarget = -(normalize(toTarget)*0.1) # 0.1 = dist to ball
        shootingPos = toTarget + self.ball
        self.go_to(self.allie(id), x=shootingPos[0], y=shootingPos[1], orientation=angleTo(self.allie(id).position, self.ball), power=33, dribble=1 if self.distToBall(id) < 0.2 else 0)    

    def wantToKick(self, id):
        targetDir = rotateVector(np.array([1, 0]), self.allie(id).orientation)
        goalX = np.array([-self.allie(id).side * self.field['length']/2, self.field['goal_width']/2.4])
        goalY = np.array([-self.allie(id).side * self.field['length']/2, -self.field['goal_width']/2.4])

        inGoal = intersect(self.allie(id).position, self.allie(id).position + targetDir * 10, goalX, goalY)

        return KICK.STRAIGHT_KICK if self.isDribbling(id) and inGoal else KICK.NO_KICK

    def abbleToKick(self, id, pos):
        targetDir = rotateVector(np.array([1, 0]), self.allie(id).orientation)

        angle = angleTo(self.ball - self.allie(id).position, pos - self.allie(id).position)

        return KICK.STRAIGHT_KICK if self.isDribbling(id) and (angle < 0.1 and angle > -0.1) else KICK.NO_KICK

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
                elif i == len(self.order) - 1: 
                    self.roles['offense'].append(id)
                    self.allie(id).role = 'offense'
                    self.allie(id).status = ''
                elif i == len(self.order) - 2 or i == len(self.order) - 4: 
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

if __name__ == "__main__":
    is_yellow = len(argv) > 1 and argv[1] == '-y'
    with Client(is_yellow) as client:
        manager = ExampleManager(client=client)
        manager.run()
