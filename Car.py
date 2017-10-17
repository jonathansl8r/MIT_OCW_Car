import lib601.sm as sm
import time
import os
import pigpio
#from usdist import usdist
from motor import motor
from sonar import ranger
import threading
import Queue

class Car(sm.SM, threading.Thread):

    def __init__(self, pi, motor_left, motor_right, sonar):
        self.m_left = motor_left
        self.m_right = motor_right
        self.sonar = sonar
        self.pi = pi
        threading.Thread.__init__(self)
        #super(Car, self).__init__() #Not sure about this... MRO subclass sm.SM first?

    def parallel_test(self): #Five second test to verify usdist_sensor callback is working
        x = []
        counter = 0
        self.m_left.speed(200)
        time.sleep(.5)
        self.sonar.read()
        time.sleep(.5)
        to = time.time()
        while counter < 500:
            x.append(self.sonar.read())
            new_speed = 125*x[len(x)-1]/500
            if new_speed < 50:
                new_speed = 0
            self.m_left.speed(new_speed)
            counter = counter + 1
            time.sleep(.05)

        print time.time() - to
        self.m_left.speed(0)
        return (counter, x)

    def motor_test(self):
        pass

def par_test():
    pi = pigpio.pi()
    #queue = Queue.Queue()
    sonar = ranger(pi=pi, trigger=17, echo=27, queue=None)
    motor_left = motor(pi=pi, forward_pin=19, back_pin=26)
    car = Car(pi=pi, motor_left=motor_left, motor_right=motor_left, sonar=sonar)
    result = car.parallel_test()
    print "Counts: " + str(result[0])
    print "Reading: " + str(result[1])