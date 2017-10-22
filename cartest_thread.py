import lib601.sm as sm
import time
import pigpio
import threading
import Queue
from motor import motor
from sonar_thread import ranger

#https://stackoverflow.com/questions/15729498/how-to-start-and-stop-thread
#https://stackoverflow.com/questions/18018033/how-to-stop-a-looping-thread-in-python

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
        threading.Thread.__init__(self)
        thread_car = threading.Thread(target=self.sonar.read)
        thread_car.setDaemon(False)
        print "Number of active threads: " + str(threading.activeCount())
        while len(x) < 50:
            #Check if there is a thread and if there is any data in the queue.
            if not thread_car.isAlive() and queue.empty():
                if not started:
                    started = True
                    thread_car = threading.Thread(target=self.sonar.run)
                    thread_car.setDaemon(False)
                    thread_car.start()
                    threads += [thread_car]
                    print "Thread created."
                else:
                    pass
                    thread_car = threading.Thread(target=self.sonar.run)
                    thread_car.setDaemon(False)
                    thread_car.start()
                    threads += [thread_car]
            else:
                pass

            #Check if the queue is empty. Get data if it is not. Will not create another thread if queue is not empty
            if not queue.empty():
                print "Emptying Queue."
                x.append(queue.get(True, 1))
                queue.task_done()
                print "Queue emptied."
            else:
                counter = counter + 1

        kill_pill.notify() #Notify thread that it needs to go to "dead state"
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
                print "Main Thread: " + str(residual) + "identified"
            else:
                to = time.time()
                if residual.isAlive():
                    print str(residual) + " is alive...!!!!!"
                    print str(residual) + " is Daemon? " + str(residual.isDaemon())
                elif not residual.isAlive():
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
    resume_condition = threading.Condition()
    kill_pill = threading.Condition()
    sonar = ranger(pi=pi, trigger=17, echo=27, queue=queue, condition=resume_condition, kill_pill=kill_pill)
    motor_left = motor(pi=pi, forward_pin=19, back_pin=26)
    car = Car(pi=pi, motor_left=motor_left, motor_right=motor_left, sonar=sonar)
    result = car.parallel_test(queue, kill_pill)
    print "Counts: " + str(result[0])
    print "Reading: " + str(result[1])
    sonar.cancel()

if __name__ == '__main__':
    par_test()