# Echo server program
import socket
import numpy as np
from scipy import optimize


# FULL_DEACTIVATION_TIME = (
#     (1000.0, 1950.0, 40000.0),
#     (1800.0, 600.0, 650.0),
#     (2400.0, 1000.0, 35.0)
#   ) # Photochromeleon

# row 1: cyan; row 2: magenta; row 3: yellow
# col 1: red;  col 2: green  ; col 3: blue
FULL_DEACTIVATION_TIME = [[467, 712, 687], [1500, 242, 177], [10000, 900, 20]]


# solve Ax = b
# get the closest value that it gives while
# keeping x non-negative
def linear_programming_solve(A, b):
    '''
  The linear progression is like this: 
    min(y0 + y1 + y2)
    when 
      y0 >= (Ax-b)[0]
      y0 >= -(Ax-b)[0]
      y1 >= (Ax-b)[1]
      y1 >= -(Ax-b)[1]
      y2 >= (Ax-b)[2]
      y3 >= -(Ax-b)[2]
  We then convert y0, y1, y2 to x3, x4, x5, respectively
  and then solve to fit the scipy API
  here: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html
  input 有cmy,
  y0 = |c-c'| -> Y0>= c-c'; y0>= c'-c
  y1 = |M-M'|
  y2 = |Y-Y‘|
  我们希望色差最小-> y0+y1+y2最小
  梯度下降可能更好，用y0^2 + y1^2 +y3^2
  

  
  '''
    c = [0, 0, 0, 1, 1, 1]
    A_ub = []
    for i in range(6):
        row = []
        for j in range(3):
            if i % 2 == 0:
                row.append(A[i // 2][j])
            else:
                row.append(-A[i // 2][j])
        for j in range(3, 6):
            row.append(0)
        row[i // 2 + 3] = -1
        A_ub.append(row)
    b_ub = [b[0], -b[0], b[1], -b[1], b[2], -b[2]]
    bounds = [(0, None), (0, None), (0, None), (None, None), (None, None),
              (None, None)]

    results = optimize.linprog(c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds)
    # return ({
    #     "x": [results.x[0], results.x[1], results.x[2]],
    #     "error": results.fun,
    #     "deltaColor": [results.x[3], results.x[4], results.x[5]]
    # })
    deltaColor = [results.x[3], results.x[4], results.x[5]]
    deactivation_time = [results.x[0], results.x[1], results.x[2]]

    return deactivation_time, deltaColor

class Deactivation:
    debug = False

    def __init__(self, debug=False):
        deactivation_speed = []
        for i in range(3):
            row = []
            for j in range(3):
                row.append(1 / FULL_DEACTIVATION_TIME[i][j])
            deactivation_speed.append(row)
        self.deactivation_speed = np.array(deactivation_speed)

    def compute_deactivation_time(self,
                                  target_color,
                                  original_color=[1, 1, 1]):
        color_to_deactivate = np.array(original_color) - np.array(target_color)
        deactivation_time, deltaColor = linear_programming_solve(self.deactivation_speed,
                                                     color_to_deactivate)
        realColor =[]                                             
        for i in range(3):
            deltaColorWithReal = 0
            for j in range(3):
                deltaColorWithReal += (1/FULL_DEACTIVATION_TIME[i][j])* deactivation_time[j]
            realColor.append(original_color[i] - deltaColorWithReal)
        return deactivation_time, realColor
 
HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)
dataSent=""
ledNum=0
while True:
    data = conn.recv(1024).decode("utf-8")
    rgbs = data.split("#")
    print('Received:'+ data)
    for i in range(len(rgbs)-1):

        color = rgbs[i].split(',')
        if not data: break
        
        # do whatever you need to do with the data
        for i in range(len(color)):
            color[i] = float(color[i])/255
        # print(color) # Paging Python!
        d = Deactivation();
        time, realColor1 = d.compute_deactivation_time(color)
        ledNum+=1
        # print("realColor")
        # print("ledNum"+str(ledNum))
        # print(realColor1)
        dataSent += str(int(realColor1[0]*255))+","+str(int(realColor1[1]*255))+","+str(int(realColor1[2]*255))+"#";
    dataSent+='\n'
    print("dataSent"+dataSent)
    print("ledNum"+str(ledNum))
    # send dataSent to socket 
    conn.send(dataSent.encode("utf-8"))








conn.close()
# optionally put a loop here so that you start 
# listening again after the connection closes




