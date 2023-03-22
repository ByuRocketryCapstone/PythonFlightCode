import spidev                                  #import the SPI library for RB Pi 4 B board
import time                                    #import the Timing library for RB Pi 4 B board

AMT22_NOP = 0x00                              #command to read the position of the encoder
NEWLINE = 0x0A
spi = spidev.SpiDev()                          #create the spi object
spi.open(0, 0)                                 #SPI port 0, CS 0
speed_hz=5000000                                #setting the speed in hz
delay_us=1000000000    

def checksum_ok(n):		#function for checking the checksum equation
         return (not(bool(n & (1<<(8+5))) ^ bool(n & (1<<(8+3))) ^ bool(n & (1<<(8+1))) ^ bool(n & (1<<7)) ^ bool(n & (1<<5)) ^ bool(n & (1<<3)) ^ bool(n & (1<<1)))==bool(n & (1<<15))) and (not(bool(n & (1<<(8+4))) ^ bool(n & (1<<(8+2))) ^ bool(n & (1<<8)) ^ bool(n & (1<<6)) ^ bool(n & (1<<4)) ^ bool(n & (1<<2)) ^ bool(n & (1<<0)))==bool(n & (1<<14)))
         
try:
    while True:          			#creating an infinite while loop
        #def checksum_ok(n):		#function for checking the checksum equation
         #return (not(bool(n & (1<<(8+5))) ^ bool(n & (1<<(8+3))) ^ bool(n & (1<<(8+1))) ^ bool(n & (1<<7)) ^ bool(n & (1<<5)) ^ bool(n & (1<<3)) ^ bool(n & (1<<1)))==bool(n & (1<<15))) and (not(bool(n & (1<<(8+4))) ^ bool(n & (1<<(8+2))) ^ bool(n & (1<<8)) ^ bool(n & (1<<6)) ^ bool(n & (1<<4)) ^ bool(n & (1<<2)) ^ bool(n & (1<<0)))==bool(n & (1<<14)))
        result=spi.xfer2([AMT22_NOP, AMT22_NOP],speed_hz,delay_us)
        #print(result)#transferring the data from the encoder
        pos_data = result[0]<<8 | result[1]    # Concatenate two bytes into 16-bit value
        #print(hex(pos_data))
        #print(checksum_ok(pos_data))  # Check the checksum
        position = pos_data & 0x3FFF
        print (position)
        #print ("hello")
        #def Enc_angle(position):
        angle = position*(360/16384)
        #print ("your momz")#Using this equation to convert the recieved data to an angle[°]
            #return (angle)						#printing the angular position
        #print(angle)    
            
        
except: 								#In case while loop doesn't work
    print("done")
    spi.close()
    GPIO.cleanup()
