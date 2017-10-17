import lib601.sm as sm
import time
import os
import pigpio

class usdist(sm.SM):

    startState = 'waiting'
    def __init__(self, pi, trigger_pin, echo_pin):
        self.trigger = trigger_pin
        self.echo = echo_pin
        self.pi = pi
        self.pi.set_mode(self.trigger, pigpio.OUTPUT)
        self.pi.set_mode(self.echo, pigpio.INPUT)
        self.alpha = .02
        self.primed = False

    def pulse(self):
        self.pi.gpio_trigger(self.trigger, 10, 1) #pulse trigger pin high for 10 microseconds

    def read(self):
        t_read = time.time()
        waitflag = False
        readflag = False
        self.echoFeedback = False
        while self.pi.read(self.echo) == False: #This is a blocking function... Need to make this a callback...
            waitflag  = True
            to = time.time()
            if to - t_read > .028:
                break

        while self.pi.read(self.echo) == True: #This is a blocking function... Need to make this a callback...
            readflag = True
            t = time.time()
            if t - t_read > .028:
                break

        if waitflag == True and readflag == True:
            self.echoFeedback = True
            return [to, t]
        else:
            self.echoFeedback = False
            return [None, None]

    def Distance(self, inp):
        (to, t) = inp
        dt = t - to
        data = round(17150*51/56*dt, 2) #speed of sound * Empirical Correction Factor * Change in time
        if self.primed:
            return self.lowpass(data)
        else:
            self.do = data
            self.primed = True
            return data

    def lowpass(self, data):
        filtered_data = data*self.alpha + self.do*(1-self.alpha)
        self.do = filtered_data
        return filtered_data

    def generateOutput(self, state):
        if state == 'pulsing':
            self.pulse()
            return 'pulse'
        elif state == 'reading':
            self.time = self.read()
            return self.time
        elif state == 'calculating':
            return self.Distance(self.time)

    def getNextValues(self, state, inp):
        startReading = inp
        if state == 'waiting' and startReading:
            nextState = 'pulsing' #if signalled to start reading, start reading
        elif state ==  'pulsing':
            nextState = 'reading' #after pulsing, try to read
        elif state == 'reading' and self.echoFeedback:
            nextState = 'calculating' #If feedback received, calculate distance
        elif state == 'reading' and not self.echoFeedback:
            nextState = 'pulsing' #If no reading from sensor, try again.
        elif state == 'calculating':
            nextState = 'waiting' #Machine to wait for next input.
        else:
            nextState = state
        return (nextState, self.generateOutput(nextState))

def runDist(w, time_to_run):
    trigger = 2
    echo = 3
    pi = pigpio.pi()
    sm = usdist(pi, trigger, echo)
    sm.start()
    t = time.localtime()

    if w == False:
        to = time.time()
        pi = pigpio.pi()
        while time.time() - to < time_to_run:
            x = sm.step((1, pi.read(echo)))
            if type(x) == float:
                print x
        pi.stop()

    elif w == True:
        time_stamp = str(t[0]) + str(int(time.time()))
        directory = os.path.dirname(os.path.realpath('US_sm.py')) + '/Data/US_sm/'
        fname = directory + time_stamp + '.csv'
        print time_stamp
        pi = pigpio.pi()
        if not os.path.exists(directory):
            os.makedirs(directory)
        f = open(fname, 'w')
        to = time.time()
        while time.time() - to < time_to_run:
            x = sm.step((1, pi.read(echo)))
            if type(x) is float:
                data = str(time.time())+', '+str(x)+'\n'
                f.write(data)
        f.close()
        pi.stop()

def oneDist(count):
    trigger = 2
    echo = 3
    pi = pigpio.pi()
    sm = usdist(pi, trigger, echo)
    sm.start()
    x = None
    y = []
    counter = 0
    t0 = time.time()
    while counter < count:
        x = sm.step((1, pi.read(echo)))
        if type(x) == float:
            y.append(x)
            counter = counter + 1
    print time.time() - t0
    print x
    print sum(y)/len(y)