import time
import globals as glb

# Class to handle logging information to the log file. Information is queued up to be logged using the queueLog function, where it is stored in
# a text buffer. All messages in the buffer are then written to the log file at once every tick using the logTick function

class Logger:
    def __init__(self, filename:str):
        self.logFile = open(filename, "w")
        self.logBuffer = ""
        
    
    # store a log message in the buffer to be written to the log file
    def queueLog(self, msg:str, log_level:int):
        #if (log_level > glb.LOG_LEVEL): return
        if (not(msg[-1] == '\n')): msg = msg + "\n"
        self.logBuffer += ("{:.3f}".format(time.time() - glb.START_TIME) + ": " + msg)
        
    
    # write all queued log messages to the log file
    def logTick(self):
        self.logFile.write(self.logBuffer)
        self.logBuffer = ""
        

