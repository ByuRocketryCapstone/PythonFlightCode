import time
import spidev

bus = 0
device = 0
spi = spidev.SpiDev()
spi.open(bus, device)

spi.max_speed_hz = 500000
spi.mode = 0

#reset encoder turns so we dont use the old one
msg1= [0x00, 0x60]
spi.xfer2(msg1)
msg1 = [0x00, 0x70]
spi.xfer2(msg1)
    

 
print(msg1)
print("")

#time.sleep(1)

def getAngle():
    msg = [0x0, 0x0]
    spi.xfer2(msg) 
    
    msg[0] = msg[0] & 0x3F
    msg[0] <<= 8
    pos = msg[0] | msg[1]
    angle = pos*(360/16384)
    return angle
    
numTurns = 0
angle = getAngle()
prev = angle
t1 = time.time()
t2 = time.time()
while time.time() - t1 < 50:
    prev = angle
    angle = getAngle()
    if prev > 355 and angle < 5:
        numTurns += 1
    elif prev <5 and angle > 355:
        numTurns -= 1
    
    if time.time() - t2 > 0.1:
        print("angle: " + str(angle + 360*numTurns))
        t2 = time.time()
    

while False:
    
    def ENC_INFO(self):
        msg = [0x00, 0xA0, 0x00, 0x00]
        spi.xfer2(msg)
    
        self.turns = msg[2] | msg[3]
        msg[0] = msg[0] & 0x3F
        msg[0] <<= 8
        self.pos = msg[0] | msg[1]
        #print(pos)
        #print("")
        #print(turns - 160)
        self.angle = pos*(360/16384)
        #print("")
        #print(angle)
        time.sleep(1)
    
        info = (angle,turns)
        return info
        
    
    

'''msg = [0x76]
spi.xfer2(msg)

time.sleep(2)

i = 1
while i < 0x7f:
    msg = [0x77]
    msg.append(i)
    result = spi.xfer2(msg)
    
    msg = [0x7b]
    msg.append(i)
    result = spi.xfer2(msg)
    
    msg = [0x7c]
    msg.append(i)
    result = spi.xfer2(msg)
    
    msg = [0x7d]
    msg.append(i)
    result = spi.xfer2(msg)
    
    msg = [0x7e]
    msg.append(i)
    result = spi.xfer2(msg)
    
    i <<= 1
    time.sleep(2)

msg = [0x76]
spi.xfer2(msg)

print('hello world')'''

