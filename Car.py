import lib601.sm as sm
import time
import pigpio
import threading
import Queue
from motor import motor
from sonar import ranger
from encoder import encoder
class Car(sm.SM, threading.Thread):

    def __init__(self, pi, motor_left, motor_right, encoder_left, encoder_right, encoder_left_queue, encoder_right_queue, sonar_left, sonar, sonar_right, sonar_left_queue, sonar_queue, sonar_right_queue):
        self.pi = pi
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.encoder_left = encoder_left
        self.encoder_right = encoder_right
        self.encoder_left_queue = encoder_left_queue
        self.encoder_right_queue = encoder_right_queue
        self.sonar_left = sonar_left
        self.sonar = sonar
        self.sonar_right = sonar_right
        self.sonar_queue = sonar_queue
        self.sonar_left_queue = sonar_left_queue
        self.sonar_right_queue = sonar_right_queue
        self.sonar_threads = []
        self.encoder_threads = []
        threading.Thread.__init__(self)

    def sonar_read(self, sonar): #Method for creating sonar thread and taking a distance reading
        x = []
        started = False
        reading = True
        while reading:
            if not started:
                started = True
                th_sonar = threading.Thread(target=sonar.read)
                th_sonar.setDaemon(False)
                th_sonar.start()
                th_sonar += [th_sonar] #Make a list of all sonar threads created

            elif reading and not self.sonar_queue.empty():
                reading = False #Need to revise so value not removed from queue

    def sonar_cleanup(self):
        for i in self.sonar_threads:
            if not i.isAlive():
                i.join()
            else:
                print "Thread " + str(i) + " is alive."

    def sonar_thread_cleanup(self, threads):
        for i in threads:
            if not i.isAlive():
                i.join()
            else:
                print "Thread " + str(i) + " is alive."

    def encoder_thread_cleanup(self, threads, timer):
        for i in threads:
            if not i.isAlive():
                i.join()
            else:
                print str(i) + " never joined. Waiting " + str(timer) + " seconds to try again."
                time.sleep(timer)
                if i.isAlive():
                    i.join()
                else:
                    print str(i) + " WILL NOT JOIN!"

    def cleanup(self):

        self.motor_left.speed(0)
        self.motor_right.speed(0)
        print "Motors turned off"

        if not self.sonar_left_queue == None:
            while not self.sonar_left_queue.empty():  # Empty the queue and let queue know tasks are done.
                self.sonar_left_queue.get()
                self.sonar_left_queue.task_done()

            if self.sonar_left_queue.empty():  # Join queue if it is empty
                self.sonar_left_queue.join()
                print "Sonar Left Queue joined"
            else:
                print "Sonar Left Queue not emptied. Can not join."

        if not self.sonar_queue == None:
            while not self.sonar_queue.empty(): #Empty the queue and let queue know tasks are done.
                self.sonar_queue.get()
                self.sonar_queue.task_done()

            if self.sonar_queue.empty(): #Join queue if it is empty
                self.sonar_queue.join()
                print "Sonar Queue joined"
            else:
                print "Sonar Queue not emptied. Can not join."

        if not self.sonar_right_queue == None:
            while not self.sonar_right_queue.empty():  # Empty the queue and let queue know tasks are done.
                self.sonar_right_queue.get()
                self.sonar_queue.task_done()

            if self.sonar_right_queue.empty():  # Join queue if it is empty
                self.sonar_right_queue.join()
                print "Sonar Right Queue joined"
            else:
                print "Sonar Right Queue not emptied. Can not join."

        if not self.encoder_left_queue == None:
            while not self.encoder_left_queue.empty():
                self.encoder_left_queue.get()
                self.encoder_left_queue.task_done()

            if self.encoder_left_queue.empty():
                self.encoder_left_queue.join()
                print "Encoder Left Queue joined"
            else:
                print "Encoder Left Queue not emptied. Can not join"

        if not self.encoder_right_queue == None:
            while not self.encoder_right_queue.empty():
                self.encoder_right_queue.get()
                self.encoder_right_queue.task_done()

            if self.encoder_right_queue.empty():
                self.encoder_right_queue.join()
                print "Encoder Right Queue joined"
            else:
                print "Encoder Right Queue not emptied. Can not join"

        if not self.sonar_left == None:
            self.sonar_left.cancel()
            print "Sonar Left Cancelled"

        if not self.sonar == None:
            self.sonar.cancel()
            print "Sonar Cancelled"

        if not self.sonar_right == None:
            self.sonar_right.cancel()
            print "Sonar Right Cancelled"

        self.pi.stop()
        print "pigpio connection stopped"

def par_test(count):

    print "Number of active threads before starting: " + str(threading.activeCount())
    print "Active threads before starting: " + str(threading.enumerate())

    pi = pigpio.pi()
    sonar_queue = Queue.Queue()
    sonar_left_queue = Queue.Queue()
    sonar_right_queue = Queue.Queue()
    sonar_left = ranger(pi=pi, trigger=17, echo=27, queue=sonar_left_queue)
    sonar = ranger(pi=pi, trigger=22, echo=5, queue=sonar_queue)
    sonar_right = ranger(pi=pi, trigger=6, echo=13, queue=sonar_right_queue)

    motor_left = motor(pi=pi, forward_pin=26, back_pin=19)
    motor_right = motor(pi=pi, forward_pin=16, back_pin=20)
    car = Car(pi=pi, motor_left=motor_left, motor_right=motor_right, encoder_left=None, encoder_right=None, encoder_left_queue=None, encoder_right_queue=None, sonar_left=sonar_left, sonar=sonar, sonar_right=sonar_right, sonar_left_queue=sonar_left_queue, sonar_queue=sonar_queue, sonar_right_queue=sonar_right_queue)

    reading = False
    sequence = [True, False, False]
    result = []
    i = 0
    while i < count:
        if not reading:
            if sequence[0]:
                car.sonar_read(sonar_left)
                reading = True
            elif sequence[1]:
                car.sonar_read(sonar)
                reading = True
            elif sequence[2]:
                car.sonar_read(sonar_right)
                reading = True
        elif reading:
            if sequence[0]:
                if sonar_left_queue.empty():
                    pass
                else:
                    result.append(sonar_left_queue.get(True, 1))
                    sonar_left_queue.task_done()


    car.cleanup()

if __name__ == '__main__':
    pass