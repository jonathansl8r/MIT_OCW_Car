import time

class encoder():

    def __init__(self, pi, signal_pin, queue):
        self.pi = pi
        self.signal_pin = signal_pin

        if not queue == None:
            self.queue = queue
        else:
            self.queue = None

    def velocity(self, t): #Outputs encoder trips / time "t" -- (use a constant to get real velocity)
        to = time.time()
        flag0 = self.pi.read(self.signal_pin)
        x = 0

        while time.time() - to < t:
            flag = self.pi.read(self.signal_pin)
            if not flag == flag0:
                x = x + 1
                flag0 = flag
            else:
                pass

        tf = time.time()
        dx_dt = x/(tf - to)

        if not self.queue == None:
            self.queue.put(dx_dt)
        else:
            return dx_dt

    def distance(self, t): #Outputs encoder trips -- (use a constant to get real distance)
        to = time.time()
        flag0 = self.pi.read(self.signal_pin)
        x = 0

        while time.time() - to < t:
            flag = self.pi.read(self.signal_pin)
            if not flag == flag0:
                x = x + 1
                flag0 = flag
            else:
                pass

        if not self.queue == None:
            self.queue.put(x)
        else:
            return x

    def speed_switch(self, t): #Returns True if encoder trips before time "t" and False if encoder does not trip before time "t"
        to = time.time()
        flag0 = self.pi.read(self.signal_pin)

        while time.time() - to < t:
            flag = self.pi.read(self.signal_pin)
            if not flag == flag0:
                if not self.queue == None:
                    self.queue.put(True)
                else:
                    return True

        if not self.queue == None:
            self.queue.put(False)
        else:
            return False

if __name__ == '__main__':
    pass