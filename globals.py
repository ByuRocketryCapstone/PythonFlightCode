from Logger import Logger
from MainSM import mainStateMachine
from SensorControl import SensorControl
from MotorControl import MotorControl
import time
import math
from enum import Enum

# constants 
LOG_FILE_NAME = "LogFiles/currLog.txt"
REF_FOLDER = "RefData/"
INDEX_FILE = REF_FOLDER + "index.txt"
REF_HEADER_SIZE = 5

MAX_PADDLE_ANGLE = 65 * (math.pi/180)
CONTROLLER_HEIGHT_THRESHOLD = 40    # m
START_TIME = time.time()

TICK_RATE = 1/100   # tick rate of 100 Hz

mainSM = mainStateMachine()
sensorControl = SensorControl()
motorControl = MotorControl()

logger = Logger(LOG_FILE_NAME)

dataListSize = 16
dataList = []


class loglv(Enum):
    FLIGHT = 1
    TEST = 2

LOG_LEVEL = loglv.TEST

