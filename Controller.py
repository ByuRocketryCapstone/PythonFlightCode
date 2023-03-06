import globals as glb

class Controller:
    def __init__(self, pVal:float, iVal:float, dVal:float):
        self.kp = pVal
        self.ki = iVal
        self.kd = dVal

        self.ref_alpha = 0
        self.cmd_alpha = 0

    def calcAngle(self,currTime,currHeight,currVelocity,currAccel):
        error_h = currHeight - refHeight
        error_v = currVelocity - refVelocity
        error_a = currAccel - refAccel

        #Actual PID Magic

        self.cmd_alpha = self.ref_alpha + (error_v * self.kp) + (error_h * self.ki) - (error_a * self.kd)

        #Trigger band antiwindup scheme (trying to improve robustnesss)
        if (abs(error_v) > refVelocity(currTime) * .15):
            self.cmd_alpha = self.ref_alpha + (error_v * self.kp) - (error_a * self.kd)
        
        if (abs(error_v) <= refVelocity(currTime) * .15): 
            self.cmd_alpha = self.ref_alpha + (error_v * self.kp) + (error_h * self.ki) - (error_a * self.kd) 


        #This is our saturation limits so we dont break things cause that would cause mucho problems
        if (self.cmd_alpha >= 70 * (glb.pi/180)): 
                self.cmd_alpha = 70 * (glb.pi/180)
        if (self.cmd_alpha <= 0): 
            self.cmd_alpha = 0
        else: 
            self.cmd_alpha = self.cmd_alpha

        return self.cmd_alpha
    