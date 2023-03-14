import time
import globals as glb

class Logger:
    def __init__(self, filename:str):
        self.logFile = open(filename, "w")
        self.logBuffer = ""
    
    def queueLog(self, msg:str, log_level:int):
        #if (log_level > glb.LOG_LEVEL): return
        if (not(msg[-1] == '\n')): msg = msg + "\n"
        # self.logBuffer += ("{:.3f}".format(time.time() - glb.START_TIME) + ": " + msg)
        self.logBuffer += ("{:.3f}".format(glb.dataList[-1].t) + ": " + msg) #FIXME: remove this line when done testing and use above line
    
    def logTick(self):
        self.logFile.write(self.logBuffer)
        self.logBuffer = ""


