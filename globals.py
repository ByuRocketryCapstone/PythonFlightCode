from Logger import Logger
from MainSM import mainStateMachine
from SensorControl import SensorControl
from MotorControl import MotorControl
from SensorData import SensorData
import time
import math
from enum import Enum
import adafruit_rgbled

lastTime = time.time()
# constants 
LOG_FILE_NAME = "LogFiles/currLog.txt"
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

printTick = time.time()

mainSM = mainStateMachine()
sensorControl = SensorControl()
motorControl = MotorControl()

logger = Logger(LOG_FILE_NAME)

dataListSize = 16
dataList = []
for i in range(dataListSize):
    dataList.append(SensorData(0,0,0,0,0))

class loglv(Enum):
    FLIGHT = 1
    TEST = 2

LOG_LEVEL = loglv.TEST

fake_data_flag = False

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
led = adafruit_rgbled.RGBLED(RED_LED, BLUE_LED, GREEN_LED)
   
