import globals as glb
import SensorData

class SensorControl:
    def __init__(self):
        pass

    def sensorTick(self):
        pass

    def pullData(self):
        # @Jacob, insert CircuitPy code here to get sensor data, and then return a SensorData object
        sd = SensorData(0,0,0,0,0)
        return sd