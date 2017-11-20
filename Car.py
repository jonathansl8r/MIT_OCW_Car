import lib601.sm as sm
import time
import pigpio
import threading
import Queue
from motor import motor
from sonar import ranger
from encoder import encoder
class Car(sm.SM, threading.Thread):

    def __init__(self, pi, motor_left, motor_right, encoder_left, encoder_right, sonar, encoder_queue, sonar_queue):
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.encoder_left = encoder_left
        self.encoder_right = encoder_right
        self.sonar = sonar
        self.pi = pi
        self.sonar_queue = sonar_queue
        self.encoder_queue = encoder_queue
        self.sonar_threads = []
        self.encoder_threads = []
        threading.Thread.__init__(self)

    def sonar_read(self): #Method for creating sonar thread and taking a distance reading
        x = []
        started = False
        reading = True
        while reading:
            if not started:
                started = True
                th_sonar = threading.Thread(target=self.sonar.read)
                th_sonar.setDaemon(False)
                th_sonar.start()
                th_sonar += [th_sonar] #Make a list of all sonar threads created

            elif reading and not self.sonar_queue.empty():
                x.append(self.sonar_queue.get(True, 1))
                self.sonar_queue.task_done()

    def parallel_test(self): #Test to verify usdist_sensor callback is working
        x = []
        y = []
        th_sonars = []
        th_encoders = []
        counter = 0
        to = time.time()
        started = False
        end = 100
        t_enc = 1

        self.motor_left.speed(200)
        self.motor_right.speed(220)  #offset of 20 required to get straight line...

        while len(x) < end:

            if not started: #Check if there is a sonar thread and if there is any data in the queue.
                started = True
                th_sonar = threading.Thread(target=self.sonar.read)
                th_sonar.setDaemon(False)
                th_sonar.start()
                th_sonars += [th_sonar] #Make list of all sonar threads created. Will all be joined.

                th_encoder = threading.Thread(target=self.encoder_left.distance, kwargs={'t': t_enc})
                th_encoder.setDaemon(False)
                th_encoder.start()
                th_encoders += [th_encoder] #Make list of all encoder threads created. Will all be joined.

            else:
                if not th_sonar.isAlive() and self.sonar_queue.empty(): #Make new sonar thread if it is data retrieved from last result
                    th_sonar = threading.Thread(target=self.sonar.read)
                    th_sonar.setDaemon(False)
                    th_sonar.start()
                    th_sonars += [th_sonar]

                if not th_encoder.isAlive() and self.encoder_queue.empty(): #Make new encoder thread if data is retrieved from last result
                    th_encoder = threading.Thread(target=self.encoder_left.distance, kwargs={'t': t_enc})
                    th_encoder.setDaemon(False)
                    th_encoder.start()
                    th_encoders += [th_encoder]  # Make list of all encoder threads created. Will all be joined.

            #Check if the sonar queue is empty. Get data if it is not. Will not create another thread if queue is not empty
            if not self.sonar_queue.empty():
                x.append(self.sonar_queue.get(True, 1))
                self.sonar_queue.task_done()

            if not self.encoder_queue.empty():
                y.append(self.encoder_queue.get(True, 1))
                self.encoder_queue.task_done()

            counter += 1

        print "Total Time run: " + str(time.time() - to)
        out = 0

        self.sonar_thread_cleanup(th_sonars)
        self.encoder_thread_cleanup(th_encoders, t_enc)

        return (counter, x, y)

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

        while not self.sonar_queue.empty(): #Empty the queue and let queue know tasks are done.
            self.sonar_queue.get()
            self.sonar_queue.task_done()

        if self.sonar_queue.empty(): #Join queue if it is empty
            self.sonar_queue.join()
            print "Sonar Queue joined"
        else:
            print "Sonar Queue not emptied. Can not join."

        while not self.encoder_queue.empty():
            self.encoder_queue.get()
            self.encoder_queue.task_done()

        if self.encoder_queue.empty():
            self.encoder_queue.join()
            print "Encoder Queue joined"
        else:
            print "Encoder Queue not emptied. Can not join"

        self.sonar.cancel()
        print "Sonar Cancelled"

        self.pi.stop()
        print "pigpio connection stopped"

def par_test():

    print "Number of active threads before starting: " + str(threading.activeCount())
    print "Active threads before starting: " + str(threading.enumerate())

    pi = pigpio.pi()
    sonar_queue = Queue.Queue()
    encoder_queue = Queue.Queue()

    sonar = ranger(pi=pi, trigger=17, echo=27, queue=sonar_queue)
    enc = encoder(pi=pi, signal_pin=2, queue=encoder_queue)
    motor_left = motor(pi=pi, forward_pin=26, back_pin=19)
    motor_right = motor(pi=pi, forward_pin=16, back_pin=20)
    car = Car(pi=pi, motor_left=motor_left, motor_right=motor_right, encoder_left=enc, encoder_right=enc, sonar=sonar, encoder_queue=encoder_queue, sonar_queue=sonar_queue)

    result = car.parallel_test()

    print "Counts: " + str(result[0])
    print "Sonar Readings: " + str(result[1])
    print "Encoder Readings: " + str(result[2])

    car.cleanup()

if __name__ == '__main__':
    pass