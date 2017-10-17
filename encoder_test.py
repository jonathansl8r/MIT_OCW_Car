import pigpio
import time
from motor import motor

pi = pigpio.pi()
pi.set_mode(4, pigpio.INPUT)
pi.set_pull_up_down(4, pigpio.PUD_UP)

m = motor(14, 15)
m.speed(0)

def read(duty):
    m.speed(duty)
    to = time.time()
    flag0 = pi.read(4)
    x = 0
    while time.time() - to < 10:
        flag = pi.read(4)
        if not flag == flag0:
            x = x + 1
            flag0 = flag
        else:
            pass

    print("Hall Effects: ")
    print (x)
    m.speed(0)

def pread(duty):
    m.speed(duty)
    while True:
        time.sleep(.25)
        print(pi.read(4))

    m.speed(0)

def timer(duty):
    m.speed(duty)
    time.sleep(5)
    to = time.time()
    flag0 = pi.read(4)
    x = 0
    while x < 10:
        flag = pi.read(4)
        if not flag == flag0:
            x = x + 1
            flag0 = flag
        else:
            pass
    t = time.time()
    print (t-to)
    m.speed(0)