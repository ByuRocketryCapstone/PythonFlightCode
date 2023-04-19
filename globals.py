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

lastTime = time.time()
# constants
fileNum = 1
LOG_FILE_NAME = "/home/rocketcs/LogFiles/currLog"+str(fileNum)+".txt"
while os.path.isfile(LOG_FILE_NAME):
    fileNum += 1
    LOG_FILE_NAME = "/home/rocketcs/LogFiles/currLog"+str(fileNum)+".txt"
    
REF_FOLDER = "RefData/"
INDEX_FILE = "index.txt"
REF_HEADER_SIZE = 5

KP = 13.2434
KI = 1.6473
KD = 0.0926

MAX_PADDLE_ANGLE = 65 #* (math.pi/180)
CONTROLLER_HEIGHT_THRESHOLD = 40    # m
START_TIME = time.time()
CUTOFF_TIME = 0

TICK_RATE = 1/100   # tick rate of 100 Hz
lastTick = 0

printTick = time.time()	# FIXME: temporary tick rate used for testing, remove before flight

mainSM = mainStateMachine()
sensorControl = SensorControl()
motorControl = MotorControl()

logger = Logger(LOG_FILE_NAME)

dataListSize = 32
dataList = []
for i in range(dataListSize):
    dataList.append(SensorData(0,0,0,0,0))
FIR_COEFFS = [0.000092, 0.000755, 0.001520, 0.000815, -0.002630, -0.006567, -0.004950, 0.005873, 0.018819, 0.017050, -0.009810, -0.046123, -0.050667, 0.013104, 0.138275, 0.265262, 0.318940, 0.265262, 0.138275, 0.013104, -0.050667, -0.046123, -0.009810, 0.017050, 0.018819, 0.005873, -0.004950, -0.006567, -0.002630, 0.000815, 0.001520, 0.000755, 0.000092]
# for i in range(dataListSize):
#     FIR_COEFFS.append(1/(2**(i+1)))
# FIR_COEFFS.append(1/(2**(dataListSize)))
# FIR_COEFFS.pop(0)
# FIR_COEFFS.reverse()

class loglv(Enum):
    FLIGHT = 1
    TEST = 2

LOG_LEVEL = loglv.TEST

# FIXME: flags for the first test flight, remove for full system
ignition_flag = False
coasting_flag = False

# Pin the Red LED is connected to
RED_LED = digitalio.DigitalInOut(board.D26)
RED_LED.direction = digitalio.Direction.OUTPUT

# Pin the Green LED is connected to
GREEN_LED = digitalio.DigitalInOut(board.D21)
GREEN_LED.direction = digitalio.Direction.OUTPUT

# Pin the Blue LED is connected to
BLUE_LED = digitalio.DigitalInOut(board.D20)
BLUE_LED.direction = digitalio.Direction.OUTPUT

# Create a RGB LED object
#led = adafruit_rgbled.RGBLED(RED_LED, BLUE_LED, GREEN_LED)

