from Logger import Logger
from MainSM import mainStateMachine
from SensorControl1 import SensorControl
from MotorControl import MotorControl
from SensorData import SensorData
import time
import os
import math
from enum import Enum
import board
import digitalio
import adafruit_rgbled

# constants

# choose log file name, making sure that it doesn't overwrite an existing file
fileNum = 1
LOG_FILE_NAME = "/home/rocketcs/LogFiles/currLog"+str(fileNum)+".txt"
while os.path.isfile(LOG_FILE_NAME):
    fileNum += 1
    LOG_FILE_NAME = "/home/rocketcs/LogFiles/currLog"+str(fileNum)+".txt"

# reference trajectory file information
REF_FOLDER = "/home/rocketcs/RefData/"
INDEX_FILE = "index.txt"
REF_HEADER_SIZE = 5

# PID controller gains obtained from simulation software
KP = 13.2434
KI = 1.6473
KD = 0.0926

MAX_PADDLE_ANGLE = 65 #* (math.pi/180)
CONTROLLER_HEIGHT_THRESHOLD = 40    # meters, used for selecting reference trajectory in PID controller
START_TIME = time.time() # bootup time when code starts running
CUTOFF_TIME = 0 # time at main engine cutoff

TICK_RATE = 1/100   # tick rate of 100 Hz
lastTick = 0

# declaration of state machine objects
mainSM = mainStateMachine()
sensorControl = SensorControl()
motorControl = MotorControl()

# declaration of logger object
logger = Logger(LOG_FILE_NAME)

# list of sensor data objects
dataListSize = 32
dataList = []
for i in range(dataListSize):
    dataList.append(SensorData(0,0,0,0,0))

# levels of log messages
class loglv(Enum):
    FLIGHT = 1
    TEST = 2

LOG_LEVEL = loglv.TEST


# Pin the Red LED is connected to
RED_LED = digitalio.DigitalInOut(board.D26)
RED_LED.direction = digitalio.Direction.OUTPUT

# Pin the Green LED is connected to
GREEN_LED = digitalio.DigitalInOut(board.D21)
GREEN_LED.direction = digitalio.Direction.OUTPUT

# Pin the Blue LED is connected to
BLUE_LED = digitalio.DigitalInOut(board.D20)
BLUE_LED.direction = digitalio.Direction.OUTPUT


