import time
import random
import numpy as np
import scipy.signal as signal


dataListSize = 33
# FIR_COEFFS = []
# for i in range(dataListSize):
#    FIR_COEFFS.append(1/(2**(i+1)))
# FIR_COEFFS.append(1/(2**(dataListSize)))
# FIR_COEFFS.pop(0)
# FIR_COEFFS.reverse()

# a = [1]*dataListSize
# a = [a]
# for i in range(dataListSize-1):
#     row = []
#     for j in range(i): row.append(0)
#     row.append(0.8)
#     row.append(-1)
#     while len(row) < dataListSize: row.append(0)
#     a.append(row)
# 
# b = [1]
# for i in range(dataListSize-1):
#     b.append(0)
# 
# a = np.array(a)
# b = np.array(b)
# c = np.linalg.solve(a, b)
# FIR_COEFFS = c
# FIR_COEFFS = np.flip(FIR_COEFFS)
# print(FIR_COEFFS)
#while(1): pass

	#phase1="peaplabel=0"
	#phase2="auth=MSCHAPV2"

#FIR_COEFFS = [0.000092, 0.000755, 0.001520, 0.000815, -0.002630, -0.006567, -0.004950, 0.005873, 0.018819, 0.017050, -0.009810, -0.046123, -0.050667, 0.013104, 0.138275, 0.265262, 0.318940, 0.265262, 0.138275, 0.013104, -0.050667, -0.046123, -0.009810, 0.017050, 0.018819, 0.005873, -0.004950, -0.006567, -0.002630, 0.000815, 0.001520, 0.000755, 0.000092]

FIR_COEFFS_B = signal.firwin(numtaps = 33, cutoff = 10, window = 'blackmanharris', pass_zero = True, fs = 100.0)
print(FIR_COEFFS_B)
#print(FIR_COEFFS_A)
# FIR_COEFFS.reverse()



data = [[0,0,0,0,0]]
t1 = time.time()
heights = []
times = []
while(time.time() - t1 < 4):
    t = time.time()-t1
    h = 20*t**2 + random.random() * 4 - 2
    a = 20 + random.random() * 4 - 2
    theta = 5 + random.random() * 4 - 2
    
    V = 0 + random.random() * 4 - 2
    data.append([t,h,V,a,theta])
    times.append(t)
    heights.append(h)
    time.sleep(0.01)

#for row in data: print(row)
#while(1): pass

filtered = []
for i in range(dataListSize):
    filtered.append([0,0,0,0,0])
    
raw = []
for i in range(dataListSize):
    raw.append([0,0,0,0,0])

#print(len(data))
#exit(0)
for row in data: print(row)
for i in range(len(data)):
    row = data[i]
    print(i)
    continue
    raw.append(row)
    raw.pop(0)
    
    t = 0; h = 0; V = 0; a = 0; theta = 0
    for j in range(dataListSize):
        h += FIR_COEFFS_B[j] * raw[-(j+1)][1]
        a += FIR_COEFFS_B[j] * raw[-(j+1)][3]
        theta = FIR_COEFFS_B[j] * raw[-(j+1)][4]
        #h += signal.lfilter(
    
    t = row[0]
    dt = t - filtered[-1][0]
    if dt == 0: dt = 0.01
    
    V_deriv = (h - filtered[-1][1]) / dt
    V_int = ((a + filtered[-1][3]) / 2) * dt
    V = (V_deriv+V_int) / 2
    
    filtered.append([t,h,V,a,theta])
    filtered.pop(0)
    print(filtered[-1])
exit(0)

import copy
data = copy.deepcopy(filtered)

raw = []
for i in range(dataListSize):
    raw.append([0,0,0,0,0])
    
filtered = []
for i in range(dataListSize):
    filtered.append([0,0,0,0,0])
    
for i in range(len(data)):
    row = data[i]
    raw.append(row)
    raw.pop(0)
    
    t = 0; h = 0; V = 0; a = 0; theta = 0
    for j in range(dataListSize):
        h += FIR_COEFFS[j] * raw[-(j+1)][1]
        a += FIR_COEFFS[j] * raw[-(j+1)][3]
        theta = FIR_COEFFS[j] * raw[-(j+1)][4]
    
    t = row[0]
    dt = t - filtered[-1][0]
    if dt == 0: dt = 0.01
    
    V_deriv = (h - filtered[-1][1]) / dt
    V_int = ((a + filtered[-1][3]) / 2) * dt
    V = (V_deriv+V_int) / 2
    
    filtered.append([t,h,V,a,theta])
    filtered.pop(0)
    print(filtered[-1])



    


    
