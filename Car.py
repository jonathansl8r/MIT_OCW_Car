import lib601.sm as sm
import time
import pigpio
import threading
import Queue
from motor import motor
from sonar import ranger

class Car(sm.SM, threading.Thread):

    def __init__(self, pi, motor_left, motor_right, sonar, queue):
        self.m_left = motor_left
        self.m_right = motor_right
        self.sonar = sonar
        self.pi = pi
        self.queue = queue
        threading.Thread.__init__(self)

    def parallel_test(self): #Five second test to verify usdist_sensor callback is working
        x = []
        threads = []
        counter = 0
        to = time.time()
        started = False
        end = 50
        while len(x) < end:

            #Check if there is a thread and if there is any data in the queue.
            if not started:
                started = True
                thread_car = threading.Thread(target=self.sonar.read)
                thread_car.setDaemon(False)
                thread_car.start()
                threads += [thread_car]
            else:
                if not thread_car.isAlive() and self.queue.empty():
                    thread_car = threading.Thread(target=self.sonar.read)
                    thread_car.setDaemon(False)
                    thread_car.start()
                    threads += [thread_car]

            #Check if the queue is empty. Get data if it is not. Will not create another thread if queue is not empty
            if not self.queue.empty():
                x.append(self.queue.get(True, 1))
                self.queue.task_done()
            else:
                counter = counter + 1

        print "Total Time run: " + str(time.time() - to)
        out = 0

        for i in threads: #Join all of the dead threads left over.
            if not i.isAlive():
                i.join()
            else:
                print "Thread " + str(i) + "IS ALIVE!!!!!!!!!!"

        return (counter, x)

    def cleanup(self):

        self.m_left.speed(0)
        self.m_right.speed(0)
        print "Motors turned off"

        while not self.queue.empty(): #Empty the queue and let queue know tasks are done.
            self.queue.get()
            self.queue.task_done()
            print "Task removed from queue"

        if self.queue.empty(): #Join queue if it is empty
            self.queue.join()
            print "Queue joined"
        else:
            print "Queue not emptied. Can not join."

        self.sonar.cancel()
        print "Sonar Cancelled"

        self.pi.stop()
        print "pigpio connection stopped"

def par_test():

    print "Number of active threads before starting: " + str(threading.activeCount())
    print "Active threads before starting: " + str(threading.enumerate())

    pi = pigpio.pi()
    queue = Queue.Queue()

    sonar = ranger(pi=pi, trigger=17, echo=27, queue=queue)
    motor_left = motor(pi=pi, forward_pin=19, back_pin=26)
    car = Car(pi=pi, motor_left=motor_left, motor_right=motor_left, sonar=sonar, queue=queue)

    result = car.parallel_test()

    print "Counts: " + str(result[0])
    print "Reading: " + str(result[1])

    car.cleanup()

if __name__ == '__main__':
    pass