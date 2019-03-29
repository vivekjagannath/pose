import dxl
import math
import numpy as np
from posestim import *

"""limits:
3- 1889 B, 3567 U, 2720 C
5- 1864 S, 598 D, 3225 U 

4- 1933 B, 224 U, 1024 C 
6- 2337 S, 3525 D, 745 U"""

a = dxl.get_available_ports()
print(a)
d = dxl.dxl(a[0], 1000000)
print(d.scan())

# x0,y0 -> Neck
# (x1,y1) (x3,y3) (x5,y5) -> Theara's left
# (x2,y2) (x4,y4) (x6,y6) -> Theara's right

def move(x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5):
        #for right:
        n = np.array([(y0 - y2), (x0 - x2)])
        s = np.array([(y2 - y4), (x2 - x4)])
        l2 = np.array([(y4- y6),  (x4 - x6)])
    
        mn = np.sqrt(n.dot(n))
        ms = np.sqrt(s.dot(s))
        ml2 = np.sqrt(l2.dot(l2))
    
        an1 = 57.296 * (math.acos ((n.dot(s))/(mn*ms)))
        an2 = 57.296 * (math.acos ((s.dot(l2))/(ms*ml2)))

        if an1 > 0:
                rshoulder = 1024 - (11.377 * (an1))
                if rshoulder < 224:
                        rshoulder = 224
        if an2 > 0:
                relbow = 2048 - (11.377 * (an2))
                if relbow < 745:
                        relbow = 745
        if an1 <= 0:
                rshoulder = 1024 + (11.377 * (an1))
                if rshoulder > 1933:
                        rshouler = 1933
        if an2 <= 0:
                relbow = 2048 + (11.377 * (an2))
                if relbow > 3525:
                        relbow = 3525
        
        #for left:
        m = np.array([(y0 - y1), (x0 - x1)])
        t = np.array([(y1 - y3), (x1 - x3)])
        l1 = np.array([(y3- y5),  (x3 - x5)])
    
        mm = np.sqrt(m.dot(m))
        mt = np.sqrt(t.dot(t))
        ml1 = np.sqrt(l1.dot(l1))
    
        an3 = 57.296 * (math.acos ((m.dot(t))/(mm*mt)))
        an4 = 57.296 * (math.acos ((t.dot(l1))/(mt*ml1)))

        if an3 > 0:
                lshoulder = 2720 - (11.377 * (an1))
                if lshoulder < 1889 :
                        lshoulder = 1889
        if an4 > 0:
                lelbow = 2048 - (11.377 * (an2))
                if lelbow < 598:
                        lelbow = 598
        if an3 <= 0:
                lshoulder = 2720 + (11.377 * (an1))
                if lshoulder > 3567:
                        lshouler = 3567
        if an4 <= 0:
                lelbow = 2048 + (11.377 * (an2))
                if lelbow > 3225:
                        lelbow = 3225

        dictio = {2: rshoulder, 3: lshoulder, 4:relbow, 5: lelbow}

        d.set_goal_position(dictio)

while true():
x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5 = advaykafunc()
move (x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5)
