import pigpio

class motor():

    def __init__(self, pi, forward_pin, back_pin):
        self.forward_pin = forward_pin
        self.back_pin = back_pin
        self.pi = pi
        self.pi.set_mode(self.forward_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.back_pin, pigpio.OUTPUT)
        self.pi.write(self.forward_pin, 0)
        self.pi.write(self.back_pin, 0)

    def speed(self, inp):
        if inp == 0:
            self.pi.write(self.back_pin, False)
            self.pi.write(self.forward_pin, False)
        elif inp < 256 and inp > 124:
            self.pi.set_PWM_dutycycle(self.back_pin, 0)
            self.pi.set_PWM_dutycycle(self.forward_pin, inp)
        elif inp > -256 and inp < -124:
            self.pi.set_PWM_dutycycle(self.back_pin, abs(inp))
            self.pi.set_PWM_dutycycle(self.forward_pin, 0)
        elif inp > 255:
            inp = 255
            self.pi.set_PWM_dutycycle(self.back_pin, 0)
            self.pi.set_PWM_dutycycle(self.forward_pin, inp)
        elif inp < 125 and inp > 0:
            inp = 125
            self.pi.write(self.back_pin, False)
            self.pi.write(self.forward_pin, False)
        elif inp < -255:
            inp = 255
            self.pi.set_PWM_dutycycle(self.forward_pin, 0)
            self.pi.set_PWM_dutycycle(self.back_pin, inp)
        elif inp > -125 and inp < 0:
            inp = 125
            self.pi.set_PWM_dutycycle(self.forward_pin, 0)
            self.pi.set_PWM_dutycycle(self.back_pin, inp)

if __name__ == '__main__':
    pass