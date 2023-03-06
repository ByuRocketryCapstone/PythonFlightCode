import globals as glb
import time


def setup():
    glb.logger.writeLog("Hello this is a first message\n")
    time.sleep(2)
    glb.logger.writeLog("This is a second message")
    time.sleep(9)
    glb.logger.writeLog("Good night")


def loop():
    pass




setup()
while(True):
    loop()
    break
