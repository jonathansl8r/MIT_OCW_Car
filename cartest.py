import lib601.sm as sm
import time
import os
import pigpio
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
        #self.thread_car = threading.Thread(target=self.sonar.read)
        #self.thread_car.setDaemon(True)
        #super(Car, self).__init__() #Not sure about this... MRO subclass sm.SM first?

    def parallel_test(self, queue): #Five second test to verify usdist_sensor callback is working
        x = []
        counter = 0
        to = time.time()
        started = False
        print "Number of active threads before starting: " + str(threading.activeCount())
        thread_car = threading.Thread(target=self.sonar.read)
        thread_car.setDaemon(True)
        print "Number of active threads: " + str(threading.activeCount())
        while len(x) < 50:
            #Check if there is a thread and if there is any data in the queue.
            if not thread_car.isAlive() and queue.empty():
                if not started:
                    started = True
                else:
                    thread_car = threading.Thread(target=self.sonar.read)
                    thread_car.setDaemon(True)
                    thread_car.start()
            else:
                pass

            #Check if the queue is empty. Get data if it is not. Will not create another thread if queue is not empty
            if not queue.empty():
                x.append(queue.get(True, 1))
            else:
                pass
            counter = counter + 1

        print "Final Number of Active Threads: " + str(threading.activeCount())
        print "Total Time run: " + str(time.time() - to)
        thread_car.join()
        return (counter, x)

def par_test():
    pi = pigpio.pi()
    queue = Queue.Queue()
    sonar = ranger(pi=pi, trigger=17, echo=27, queue=queue)
    motor_left = motor(pi=pi, forward_pin=19, back_pin=26)
    car = Car(pi=pi, motor_left=motor_left, motor_right=motor_left, sonar=sonar)
    result = car.parallel_test(queue)
    print "Counts: " + str(result[0])
    print "Reading: " + str(result[1])
    print "Size of queue: " + str(queue.qsize())
    queue.join()
    print "Queue joined."

if __name__ == '__main__':
    pass