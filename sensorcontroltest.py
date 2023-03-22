from SensorControl import SensorControl as SC

SC_object = SC()

while True:
    
    print(SC_object.pullData())