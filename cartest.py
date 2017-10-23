import lib601.sm as sm
import time
import pigpio
import threading
import Queue
from motor import motor
from sonar import ranger

class Car(sm.SM, threading.Thread):

    def __init__(self, pi, motor_left, motor_right, sonar):
        self.m_left = motor_left
        self.m_right = motor_right
        self.sonar = sonar
        self.pi = pi
        threading.Thread.__init__(self)

    def parallel_test(self, queue, kill_pill): #Five second test to verify usdist_sensor callback is working
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
                print "Thread created."
            else:
                if not thread_car.isAlive() and queue.empty():
                    thread_car = threading.Thread(target=self.sonar.read)
                    thread_car.setDaemon(False)
                    thread_car.start()
                    threads += [thread_car]

            #Check if the queue is empty. Get data if it is not. Will not create another thread if queue is not empty
            if not queue.empty():
                print "Emptying Queue."
                x.append(queue.get(True, 1))
                queue.task_done()
                print "Queue emptied."
                #print "Sending kill pill to thread"
                #kill_pill.set()
            else:
                counter = counter + 1

        print "Total Time run: " + str(time.time() - to)
        print "Final Number of Active Threads: " + str(threading.activeCount())
        print "Running Threads: " + str(threading.enumerate())
        out = 0

        print "Joining queue."
        queue.join()
        print "Queue joined."
        print "Joining threads"
        for i in threads:
            if not i.isAlive():
                i.join()
            else:
                print "Thread " + str(i) + "isAlive"
        print "Threads joined."

        for residual in threading.enumerate():
            if out == 0:
                print "Main Thread: " + str(residual) + " identified"
            else:
                to = time.time()
                if not residual.isAlive():
                    print "Joining: " + str(residual)
                    residual.join()
                    print str(residual) + " Joined"
            out += 1
        return (counter, x)

def par_test():

    print "Number of active threads before starting: " + str(threading.activeCount())
    print "Active threads before starting: " + str(threading.enumerate())

    pi = pigpio.pi()
    queue = Queue.Queue()
    kill_pill = threading.Event()

    sonar = ranger(pi=pi, trigger=17, echo=27, queue=queue, kill_pill=kill_pill)
    motor_left = motor(pi=pi, forward_pin=19, back_pin=26)
    car = Car(pi=pi, motor_left=motor_left, motor_right=motor_left, sonar=sonar)

    result = car.parallel_test(queue, kill_pill)

    print "Counts: " + str(result[0])
    print "Reading: " + str(result[1])

    while not queue.empty:
        queue.get()
        queue.task_done()
        print "Item removed from queue!"
    print "Queue joining..."
    queue.join()
    print "Queue joined."

    sonar.cancel()
    pi.stop()
    print "Active threads after cleanup: " + str(threading.enumerate())

if __name__ == '__main__':
    pass