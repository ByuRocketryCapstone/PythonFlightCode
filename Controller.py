

class Controller:
    def __init__(self, pVal:float, iVal:float, dVal:float):
        self.kp = pVal
        self.ki = iVal
        self.kd = dVal