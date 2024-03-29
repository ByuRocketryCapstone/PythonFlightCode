import globals as glb

class Controller:
    def __init__(self, pVal:float, iVal:float, dVal:float):
        self.kp = pVal
        self.ki = iVal
        self.kd = dVal

        self.ref_alpha = 0
        self.cmd_alpha = 0

        self.refHeight = []
        self.refVelocity = []
        self.refAccel = []
        self.refTime = []

        self.loadRefData(glb.dataList[-1].h, glb.dataList[-1].V)


    def calcAngle(self, currTime:float, currHeight:float, currVelocity:float, currAccel:float):
        error_h = currHeight - self.getRefHeight(currTime)
        error_v = currVelocity - self.getRefVelocity(currTime)
        error_a = currAccel - self.getRefAccel(currTime)

        # Actual PID Magic
        self.cmd_alpha = self.ref_alpha + (error_v * self.kp) + (error_h * self.ki) - (error_a * self.kd)

        # Trigger band antiwindup scheme (trying to improve robustnesss)
        if (abs(error_v) > self.getRefVelocity(currTime) * .15):
            self.cmd_alpha = self.ref_alpha + (error_v * self.kp) - (error_a * self.kd)
        
        if (abs(error_v) <= self.getRefVelocity(currTime) * .15): 
            self.cmd_alpha = self.ref_alpha + (error_v * self.kp) + (error_h * self.ki) - (error_a * self.kd) 

        self.cmd_alpha = self.cmd_alpha * (180/3.14159)
        # This is our saturation limits so we dont break things cause that would cause mucho problems
        if (self.cmd_alpha >= glb.MAX_PADDLE_ANGLE): 
            self.cmd_alpha = glb.MAX_PADDLE_ANGLE
        if (self.cmd_alpha <= 0): 
            self.cmd_alpha = 0
        else: 
            self.cmd_alpha = self.cmd_alpha

        return self.cmd_alpha


    # select reference trajectory and load data for use with the PID algorithm
    def loadRefData(self, mecoHeight:float, mecoVelocity:float):
        reader = open(glb.REF_FOLDER + glb.INDEX_FILE, "r")
        candidateHeights = []; candidateVelocities = []; filenames = []
        selectedFileName = ""

        # read starting values from index file and choose trajectory that most closely matches
        # the height and velocity of the rocket at main engine cutoff (MECO)
        data = reader.read()
        lines = data.splitlines()
        for line in lines:
            values = line.split()
            candidateHeights.append(float(values[0]))
            candidateVelocities.append(float(values[1]))
            filenames.append(values[2])

        minError = 0
        for i in range(len(candidateHeights)):
            currError = abs(candidateVelocities[i] - mecoVelocity) + \
                0.5*abs(candidateHeights[i] - mecoHeight)
            if (currError < minError): 
                selectedFileName = filenames[i]
        
        if selectedFileName == "":
            selectedFileName = "refData1.txt"


        
        # close index file 
        reader.close()

        # read data from selected trajectory file
        glb.logger.queueLog("Selected reference trajectory: " + selectedFileName + " in controller.", glb.loglv.FLIGHT)
        reader = open(glb.REF_FOLDER+selectedFileName, "r")
        data = reader.read()
        lines = data.splitlines()
        lines = lines[glb.REF_HEADER_SIZE:] # cut off header lines
        for line in lines:
            line = line.replace(",","") # remove commas from each line
            values = line.split()

            # add data values to corresponding arrays
            self.refTime.append(float(values[0]))
            self.refHeight.append(float(values[1]))
            self.refVelocity.append(float(values[2]))
            self.refAccel.append(float(values[3]))
          

    def getRefHeight(self, t:float):
        return self.refHeight[self.getTimeIndex(t)]


    def getRefVelocity(self, t:float):
        return self.refVelocity[self.getTimeIndex(t)]


    def getRefAccel(self, t:float):
        return self.refAccel[self.getTimeIndex(t)]


    # get index corresponding to the given time
    def getTimeIndex(self, t:float):
        for i in range(len(self.refTime)-1):
            if (self.refTime[i] < t and self.refTime[i+1] > t): return i
        return len(self.refTime)-1
    