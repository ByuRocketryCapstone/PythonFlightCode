from Logger import Logger
from MainSM import mainStateMachine
from SensorControl import SensorControl
from MotorControl import MotorControl
from SensorData import SensorData
import time
import math
from enum import Enum

lastTime = time.time()
# constants 
LOG_FILE_NAME = "LogFiles/currLog.txt"
REF_FOLDER = "RefData/"
INDEX_FILE = "index.txt"
REF_HEADER_SIZE = 5

KP = 10.618
KI = 3.98
KD = 0.0985

MAX_PADDLE_ANGLE = 65 * (math.pi/180)
CONTROLLER_HEIGHT_THRESHOLD = 40    # m
START_TIME = time.time()

TICK_RATE = 1/1000   # tick rate of 100 Hz
lastTick = 0

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