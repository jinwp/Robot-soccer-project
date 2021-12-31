import numpy as np
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel
import time
import random

from mlagents_envs.environment import UnityEnvironment
channel = EngineConfigurationChannel()
env     = UnityEnvironment(file_name = "CoE202", side_channels = [channel])
channel.set_configuration_parameters(time_scale = 1, width = 600, height = 400)

env.reset()
behaviour_name_1 = list(env.behavior_specs)[0]

behaviour_name_2 = list(env.behavior_specs)[1]

#print('b_n',env.brains)
decision_steps_p, _ = env.get_steps(behaviour_name_1)

decision_steps_b, _ = env.get_steps(behaviour_name_2)

cur_obs_b = decision_steps_b.obs[0][0,:]
empty_list=[]

purple = behaviour_name_1
blue = behaviour_name_2

def sensor_front_sig(data):
    player=[]
    sensor_data=[]
    for sensor in range(33):
        player.append(data[8*sensor:(8*sensor)+8])
    
    for stack in range(3):
        sensor_data.append(player[11*stack:(11*stack)+11])

    return sensor_data

def sensor_back_sig(data):
    player=[]
    sensor_data=[]
    for sensor in range(9):
        player.append(data[8*sensor:(8*sensor)+8])
    
    for stack in range(3):
        sensor_data.append(player[3*stack:(3*stack)+3])

    return sensor_data

signal_blue_front_s = sensor_front_sig(decision_steps_b.obs[0][0,:])
signal_blue_back_s = sensor_back_sig(decision_steps_b.obs[1][0,:])
signal_blue_front_d = sensor_front_sig(decision_steps_b.obs[0][1,:])
signal_blue_back_d = sensor_back_sig(decision_steps_b.obs[1][1,:])
signal_purple_front_s = sensor_front_sig(decision_steps_p.obs[0][0,:])
signal_purple_back_s = sensor_back_sig(decision_steps_p.obs[1][0,:])
signal_purple_front_d = sensor_front_sig(decision_steps_p.obs[0][1,:])
signal_purple_back_d = sensor_back_sig(decision_steps_p.obs[1][1,:])

class Goalie():
    def __init__(self, behavior):
        self.behavior = behavior

class Attacker():
    def __init__(self, behavior, bearing):
        self.behavior = behavior
        self.bearing = bearing

    def updateBearing(self, direction):
        #When counter clockwise, direction is 1. When clockwise, direction is 2.
        #After doing a turn-related function, make sure to update the bearing by doing something like bluestriker.updateBearing(1 or 2).
        if (direction == 1):
            self.bearing = self.bearing + 10
            if (self.bearing > 360):
                self.bearing = self.bearing%360
        elif (direction == 2):
            self.bearing = self.bearing - 10
            if (self.bearing < 0):
                self.bearing = self.bearing%360

# Blue    = [Goalie(behaviour_name_2), Attacker(behaviour_name_2, 0)]
# Purple    = [Goalie(behaviour_name_1), Attacker(behaviour_name_1, 0)]
purple_striker = Attacker(behaviour_name_1,0)

#--------------------------------------------------------------------------------------------------------------------------------------
# defender class

# (0,0,0) = (random.randint(0,3), random.randint(0,3), random.randint(0,3))

def front_sensor(signal_front, object_kind):
    lsd = []
    for sensor in range(11):
        if signal_front[0][sensor][object_kind] == 1:
            lsd.append(sensor)
    return lsd
    
def detect_leftright(detected_sensor_list):
    if len(detected_sensor_list) == 0:
        pass
    elif detected_sensor_list[0] == 0 and signal_blue_front_s[0][0][7] > 0.1:
        env.set_actions(blue,np.array([(0,0,0),(0,0,0)]))
        env.step()
    else:
        if detected_sensor_list[-1] % 2 == 0: # even number
            for i in range(2):
                env.set_actions(blue,np.array([(0,2,0),(0,2,0)])) # left
                env.step()
            if signal_blue_front_s[0][2][0] == 1:
                if signal_blue_front_s[0][2][7] < 0.2:
                    for i in range(3):
                        env.set_actions(blue,np.array([(1,0,0),(1,0,0)]))
                        env.step()
                    for i in range(3):
                        env.set_actions(blue,np.array([(2,0,0),(2,0,0)]))
                        env.step()
            elif signal_blue_front_d[0][2][0] == 1:
                if signal_blue_front_d[0][2][7] < 0.1:
                    for i in range(3):
                        env.set_actions(blue,np.array([(1,0,0),(1,0,0)]))
                        env.step()
                    for i in range(3):
                        env.set_actions(blue,np.array([(2,0,0),(2,0,0)]))
                        env.step()
        else:
            for i in range(2):
                env.set_actions(blue,np.array([(0,1,0),(0,1,0)])) # right
                env.step()
            if signal_blue_front_s[0][1][0] == 1:
                if signal_blue_front_s[0][1][7] < 0.2:
                    for i in range(2):
                        env.set_actions(blue,np.array([(1,0,0),(1,0,0)]))
                        env.step()
                    for i in range(2):
                        env.set_actions(blue,np.array([(2,0,0),(2,0,0)]))
                        env.step()
            elif signal_blue_front_d[0][1][0] == 1:
                if signal_blue_front_d[0][1][7] < 0.1:
                    for i in range(2):
                        env.set_actions(blue,np.array([(1,0,0),(1,0,0)]))
                        env.step()
                    for i in range(2):
                        env.set_actions(blue,np.array([(2,0,0),(2,0,0)]))
                        env.step()
    

def move_to_center(signal_blue_back_d, signal_blue_front_d, signal_blue_front_s, signal_blue_back_s):
    if signal_blue_back_d[0][1][1] == 1 and signal_blue_back_d[0][2][1] == 1:
        # print("success")
        ranges = signal_blue_back_d[0][1][7] - signal_blue_back_d[0][2][7]
        if ranges < 0:
            env.set_actions(blue,np.array([(0,1,0),(0,1,0)])) # right
            env.step()
        elif ranges > 0:
            env.set_actions(blue,np.array([(0,2,0),(0,2,0)])) # left
            env.step()
    elif signal_blue_back_d[0][1][3] == 1 and signal_blue_back_d[0][2][1] == 1:
        env.set_actions(blue,np.array([(0,1,0),(0,1,0)])) # right
        env.step()
    elif signal_blue_back_d[0][1][1] == 1 and signal_blue_back_d[0][2][3] == 1:
        env.set_actions(blue,np.array([(0,2,0),(0,2,0)])) # left
        env.step()
    else:
        if signal_blue_front_d[0][10][3] == 1 and signal_blue_front_d[0][9][3] == 1:
            if signal_blue_front_d[0][10][7] < signal_blue_front_d[0][9][7]:
                env.set_actions(blue,np.array([(0,1,0),(0,1,0)])) # right
                env.step()
            else:
                env.set_actions(blue,np.array([(0,2,0),(0,2,0)])) # left
                env.step()
        elif signal_blue_front_d[0][8][3] == 1 and signal_blue_front_d[0][7][3] == 1:
            if signal_blue_front_d[0][8][7] < signal_blue_front_d[0][7][7]:
                env.set_actions(blue,np.array([(0,1,0),(0,1,0)])) # right
                env.step()
            else:
                env.set_actions(blue,np.array([(0,2,0),(0,2,0)])) # left
                env.step()
        elif signal_blue_front_d[0][6][3] == 1 and signal_blue_front_d[0][5][3] == 1:
            if signal_blue_front_d[0][6][7] < signal_blue_front_d[0][5][7]:
                env.set_actions(blue,np.array([(0,1,0),(0,1,0)])) # right
                env.step()
            else:
                env.set_actions(blue,np.array([(0,2,0),(0,2,0)])) # left
                env.step()
        else:
            print("too many objects on the way, move to the center function is not possible to run")
            env.set_actions(blue,np.array([(0,random.randint(1,3),0),(0,random.randint(1,3),0)])) # stop
            env.step()


def find_its_place(signal_blue_back_d, signal_blue_front_d, signal_blue_front_s, signal_blue_back_s):
    if signal_blue_back_d[0][0][1] == 1 and 0.15 > signal_blue_back_d[0][0][7] > 0.079: #0.079828
        lst = front_sensor(signal_blue_front_d, 0)
        lit = front_sensor(signal_blue_front_s, 0)

        if len(lst) == 0:
            move_to_center(signal_blue_back_d, signal_blue_front_d, signal_blue_front_s, signal_blue_back_s)
            print("move to center")
        if len(lit) != 0:
            if len(lit) == 0:
                pass
            elif lit[0] == 0 and signal_blue_front_s[0][0][7] > 0.1:
                env.set_actions(blue,np.array([(0,0,0),(0,0,0)]))
                env.step()
            else:
                if lit[-1] % 2 == 0: # even number
                    for i in range(2):
                        env.set_actions(blue,np.array([(0,2,0),(0,2,0)])) # left
                        env.step()
                    if signal_blue_front_s[0][2][0] == 1:
                        if signal_blue_front_s[0][2][7] < 0.2:
                            for i in range(3):
                                env.set_actions(blue,np.array([(1,0,0),(1,0,0)]))
                                env.step()
                            for i in range(3):
                                env.set_actions(blue,np.array([(2,0,0),(2,0,0)]))
                                env.step()
                    elif signal_blue_front_d[0][2][0] == 1:
                        if signal_blue_front_d[0][2][7] < 0.1:
                            for i in range(3):
                                env.set_actions(blue,np.array([(1,0,0),(1,0,0)]))
                                env.step()
                            for i in range(3):
                                env.set_actions(blue,np.array([(2,0,0),(2,0,0)]))
                                env.step()
                else:
                    for i in range(2):
                        env.set_actions(blue,np.array([(0,1,0),(0,1,0)])) # right
                        env.step()
                    if signal_blue_front_s[0][1][0] == 1:
                        if signal_blue_front_s[0][1][7] < 0.2:
                            for i in range(2):
                                env.set_actions(blue,np.array([(1,0,0),(1,0,0)]))
                                env.step()
                            for i in range(2):
                                env.set_actions(blue,np.array([(2,0,0),(2,0,0)]))
                                env.step()
                    elif signal_blue_front_d[0][1][0] == 1:
                        if signal_blue_front_d[0][1][7] < 0.1:
                            for i in range(2):
                                env.set_actions(blue,np.array([(1,0,0),(1,0,0)]))
                                env.step()
                            for i in range(2):
                                env.set_actions(blue,np.array([(2,0,0),(2,0,0)]))
                                env.step()
        else:
            if len(lst) == 0:
                pass
            elif lst[0] == 0 and signal_blue_front_s[0][0][7] > 0.1:
                env.set_actions(blue,np.array([(0,0,0),(0,0,0)]))
                env.step()
            else:
                if lst[-1] % 2 == 0: # even number
                    for i in range(2):
                        env.set_actions(blue,np.array([(0,2,0),(0,2,0)])) # left
                        env.step()
                    if signal_blue_front_s[0][2][0] == 1:
                        if signal_blue_front_s[0][2][7] < 0.2:
                            for i in range(3):
                                env.set_actions(blue,np.array([(1,0,0),(1,0,0)]))
                                env.step()
                            for i in range(3):
                                env.set_actions(blue,np.array([(2,0,0),(2,0,0)]))
                                env.step()
                    elif signal_blue_front_d[0][2][0] == 1:
                        if signal_blue_front_d[0][2][7] < 0.1:
                            for i in range(3):
                                env.set_actions(blue,np.array([(1,0,0),(1,0,0)]))
                                env.step()
                            for i in range(3):
                                env.set_actions(blue,np.array([(2,0,0),(2,0,0)]))
                                env.step()
                else:
                    for i in range(2):
                        env.set_actions(blue,np.array([(0,1,0),(0,1,0)])) # right
                        env.step()
                    if signal_blue_front_s[0][1][0] == 1:
                        if signal_blue_front_s[0][1][7] < 0.2:
                            for i in range(2):
                                env.set_actions(blue,np.array([(1,0,0),(1,0,0)]))
                                env.step()
                            for i in range(2):
                                env.set_actions(blue,np.array([(2,0,0),(2,0,0)]))
                                env.step()
                    elif signal_blue_front_d[0][1][0] == 1:
                        if signal_blue_front_d[0][1][7] < 0.1:
                            for i in range(2):
                                env.set_actions(blue,np.array([(1,0,0),(1,0,0)]))
                                env.step()
                            for i in range(2):
                                env.set_actions(blue,np.array([(2,0,0),(2,0,0)]))
                                env.step()
            print("ball detected")
    
    # 등치기
    elif signal_blue_back_d[0][0][1] == 1 and signal_blue_back_d[0][0][7] >= 0.15:
        print("out of bound")
        for i in range(2):
            env.set_actions(blue,np.array([(0,0,0),(2,0,0)]))
            env.step()
        if signal_blue_back_d[0][0][7] < 0.001:
            env.set_actions(blue,np.array([(0,0,0),(1,0,0)]))
            env.step()
        elif signal_blue_back_d[0][0][7] > 0.001:
            for i in range(2):
                env.set_actions(blue,np.array([(0,0,0),(2,0,0)]))
                env.step()
            env.set_actions(blue,np.array([(0,0,0),(1,0,0)]))
            env.step()
    
    else:
        move_to_center(signal_blue_back_d, signal_blue_front_d, signal_blue_front_s, signal_blue_back_s)
        print(signal_blue_back_d[0]) # sensor 0, 1, 2 -> wall

    # def escape_from_side():
    #     if signal_purple_back_d[0][0][3] == 1:
    
#--------------------------------------------------------------------------------------------------------------------------------------

def Kick(attacker_frontsig):
    for sensors in range(11):
        if attacker_frontsig[0][sensors][0] == 0.2: 
            env.set_actions(behaviour_name_1, np.array([(2,0,0),(0,0,0)]))
            env.step()
            env.set_actions(behaviour_name_1, np.array([(1,0,0),(0,0,0)]))
            env.step()
        else:
            pass


def FallBack(attacker_backsig, attacker_frontsig, behaviour_name_1): 
    while attacker_backsig[0][0][4] > 1 or attacker_backsig[0][1][4] > 1 or attacker_backsig[0][2][4] > 1: 
        for sensors in range(11):
            if attacker_frontsig[0][sensors][0] > 1: 
                env.set_actions(behaviour_name_1, np.array([(2,0,0),(0,0,0)]))
                env.step()
            else:
                pass


def RunForward(attacker_frontsig, behaviour_name_1):
    #given the condition that Goalie has the ball
    while True:
        for sensors in range(11): 
            if attacker_frontsig[0][sensors][2] > 1: 
                env.set_actions(behaviour_name_1, np.array([(1,0,0),(0,0,0)]))
            else:
                pass


def ManMark(attacker_backsig, attacker_frontsig, behaviour_name_1): 
    #when agent on our side
    while attacker_backsig[0][0][5] < 1 or attacker_backsig[0][1][5] < 1 or attacker_backsig[0][2][5] < 1: 
        for sensors in range(0,11,2):
            if attacker_frontsig[0][sensors][5] < 1: 
                env.set_actions(behaviour_name_1, np.array([(0,2,0),(0,0,0)]))
                env.step()
            else:
                pass
        for sensors in range(1,11,2):
            if attacker_frontsig[0][sensors][5] <1: 
                env.set_actions(behaviour_name_1, np.array([(0,1,0),(0,0,0)]))
                env.step()
            else:
                pass



#base function 1
#this function is made with the assumption in mind that the defender has the role of a goalie, where it does not go too far off from our team's goalpost.
#return true if the striker is close to our side of the field, and return false if the striker is far from our side of field.
#the input parameter goalies_signal is the array of sensor values from the goalie unit.
def fieldDistance(goalies_signal):
    for i in range(7):
        if (goalies_signal[0][i][4] == 1 and goalies_signal[0][i][7] > 0.5):
            return False
    return True

#base function 4
#Created three functions: one to turn to the direction of a specific sensor, one to turn specifically a number of known degrees, and one to turn to a specific known direction.

#used to turn by specific angles, where angles are numbers that are multiples of 10.
#angle is in clockwise direction. That is, turnByAngle(10) will turn the striker 10 degrees in the counter-clockwise direction, and turnByAngle(-10)
#will turn the striker 10 degrees in the clockwise direction.
#This was written assuming that the first tuple is the striker and the second tuple is the defender.
def turnByAngle(behaviour_name, angle, striker):
    if (angle >= 0):
        for i in range(angle//10):
            env.set_actions(behaviour_name, np.array([(0,0,1),(0,0,0)]))
            striker.updateBearing(1)
            env.step()
    elif (angle < 0):
        angle = 0 - angle
        for i in range(angle//10):
            env.set_actions(behaviour_name, np.array([(0,0,2),(0,0,0)]))
            striker.updateBearing(2)
            env.step()

#Turn to the sensor. For example, if you want to turn to where sensor 8 was pointing, use turnBySensor(behaviour_name_1, 8).
#This function is only an approximation, and does not turn exactly to where the sensor was pointing, as turning can happen only in degrees of multiples of 10, but the 
#sensors are separated by 12 degrees.
def turnBySensor(behaviour_name, sensor, striker):
    if (sensor == 1):
        turnByAngle(behaviour_name, -10, striker)
    elif (sensor == 2):
        turnByAngle(behaviour_name, 10, striker)
    elif (sensor == 3):
        turnByAngle(behaviour_name, -20, striker)
    elif (sensor == 4):
        turnByAngle(behaviour_name, 20, striker)
    elif (sensor == 5):
        turnByAngle(behaviour_name, -40, striker)
    elif (sensor == 6):
        turnByAngle(behaviour_name, 40, striker)
    elif (sensor == 7):
        turnByAngle(behaviour_name, -50, striker)
    elif (sensor == 8):
        turnByAngle(behaviour_name, 50, striker)
    elif (sensor == 9):
        turnByAngle(behaviour_name, -60, striker)
    elif (sensor == 10):
        turnByAngle(behaviour_name, 60, striker)

#if you want to turn to a specific bearing. (e.g turnByBearing(behaviour_name_1, 180, bluestriker) will make the blue striker turn and face the blue goal.
def turnByBearing(behaviour_name, bearing, striker):
    bearing = bearing%360
    while (striker.bearing != bearing):
        env.set_actions(behaviour_name, np.array([(0,0,1),(0,0,0)]))
        striker.updateBearing(1)
        env.step()


#Defensive Function 5
#만들긴 했는데 딱히 실용적인 의미가 있을지는 모르겠는 function.
def backDrift(striker_signal, behaviour_name):
    odd_nums = [5,7,9]
    even_nums = [6,8,10]
    #if the ball and our goalpost is both on the right side of attacker
    for i in odd_nums:
        if(striker_signal[0][i][0] == 1):
            for j in odd_nums:
                if(striker_signal[0][j][1] == 1):
                    #move back and to the right
                    env.set_actions(behaviour_name, np.array([(2,1,0),(0,0,0)]))
                    env.step()
    #if the ball and our goalpost is both on the left side of attacker
    for h in even_nums:
        if(striker_signal[0][h][0] == 1):
            for k in even_nums:
                if(striker_signal[0][k][1] == 1):
                    #move back and to the left
                    env.set_actions(behaviour_name, np.array([(2,2,0),(0,0,0)]))
                    env.step()

##Attacker

def turning_while_checked(attacker_frontsig, behaviour_name_1, striker):
    while (attacker_frontsig[0][1][0]==0):
        decision_steps_p, terminal_steps_p = env.get_steps(behaviour_name_1)
        attacker_frontsig = sensor_front_sig(decision_steps_p.obs[0][0,:])
        env.set_actions(behaviour_name_1, np.array([(0,0,2),(0,0,0)]))
        striker.updateBearing(2)
        env.step()
#    if (side[0].Front[0][0][0]==1):
    return 1
#    elif (side[0].Back[0][0][0]==1):
#        return 0

#only use when return value of turning_while_checked == 1
def towards_ball(attacker_frontsig, behaviour_name_1, striker):
    while (attacker_frontsig[0][1][0]==1 and attacker_frontsig[0][1][7] >= 0.1):
        decision_steps_p, terminal_steps_p = env.get_steps(behaviour_name_1)
        attacker_frontsig = sensor_front_sig(decision_steps_p.obs[0][0,:])
        env.set_actions(behaviour_name_1, np.array([(1,0,0),(0,0,0)]))
        env.step()


#Attacker function 1. 먼저 front sensor 나 back sensor 중 어느 것에 enemy 가 감지되는지 보는 함수 만듬. 감지가 되면 그 sensor index를 배출하고, 아니면 return -1.
def front_enemy(attacker_frontsig):
    wrong=0
    for i in range(11):
        if (attacker_frontsig[0][i][5]==1):
            return i
            break
        else:
            wrong=wrong+1
    return -1
    
def back_enemy(attacker_frontsig):
    wrong=0
    for i in range(3):
        if (attacker_frontsig[0][i][5]==1):
            return i
            break
        else:
            wrong=wrong+1
    return -1
    
#실제 attacker 함수        
#only use when return value of towards_ball == 1
def towards_goalpost(attacker_frontsig, behaviour_name_1, striker):
    if (front_enemy(attacker_frontsig) != -1 and front_enemy(attacker_frontsig) < 7): #sensor 7, 8, 9, 10 은 굳이 안돌아도 될듯
        while attacker_frontsig[0][front_enemy(attacker_frontsig)][7]>0.3:
            env.set_actions(behaviour_name_1, np.array([(1,0,0),(0,0,0)]))
            env.step()
        if attacker_frontsig[0][front_enemy(attacker_frontsig)][7]<=0.3:
            if (front_enemy(attacker_frontsig)%2==0): #indicates left sensors
                env.set_actions(behaviour_name_1, np.array([(0,0,2),(0,0,0)]))
                striker.updateBearing(2)
                env.step()
            else:
                env.set_actions(behaviour_name_1, np.array([(0,0,1),(0,0,0)]))
                striker.updateBearing(1)
                env.step()
    elif (back_enemy(attacker_frontsig)!=-1): #적이 뒤에만 있는 경우 
        env.set_actions(behaviour_name_1, np.array([(1,0,0),(0,0,0)]))
        env.step()

def turn_and_kick(attacker_frontsig, behaviour_name_1, striker):
    turnBySensor(behaviour_name_1, 1, striker)
    Kick(attacker_frontsig)
    
def team9(behaviour_name_1, behaviour_name_2):
    decision_steps_p, terminal_steps_p = env.get_steps(behaviour_name_1)
    decision_steps_b, terminal_steps_b = env.get_steps(behaviour_name_2)
    signal_blue_front_s = sensor_front_sig(decision_steps_b.obs[0][0,:])
    signal_blue_back_s = sensor_back_sig(decision_steps_b.obs[1][0,:])
    signal_blue_front_d = sensor_front_sig(decision_steps_b.obs[0][1,:])
    signal_blue_back_d = sensor_back_sig(decision_steps_b.obs[1][1,:])
    signal_purple_front_s = sensor_front_sig(decision_steps_p.obs[0][0,:])
    signal_purple_back_s = sensor_back_sig(decision_steps_p.obs[1][0,:])
    signal_purple_front_d = sensor_front_sig(decision_steps_p.obs[0][1,:])
    signal_purple_back_d = sensor_back_sig(decision_steps_p.obs[1][1,:])

    find_its_place(signal_blue_back_d, signal_blue_front_d, signal_blue_front_s, signal_blue_back_s)
    env.set_actions(behaviour_name_1,np.array([(0,0,0),(0,0,0)]))
    env.step()

while True:
    decision_steps_p, _ = env.get_steps(behaviour_name_1)
    decision_steps_b, _ = env.get_steps(behaviour_name_2)
    team9(behaviour_name_1, behaviour_name_2)
env.close()