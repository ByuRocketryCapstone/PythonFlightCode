
class SensorData:
    # def __init__(self):
    #     self.h = 0
    #     self.V = 0
    #     self.a = 0
    #     self.theta = 0
    #     self.t = 0
    
    def __init__(self, height:float, velocity:float, accel:float, angle:float, time:float):
        self.h = height
        self.V = velocity
        self.a = accel
        self.theta = angle
        self.t = time
    
    def __str__(self):
        return "t: " + str(self.t) + ", h: " + str(self.h) + ", V: " \
            + str(self.V) + ", a: " + str(self.a) + ", theta: " + str(self.theta)