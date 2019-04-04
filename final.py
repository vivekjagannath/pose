import dxl
import math
import numpy as np
import posestim

e4, e1, e2, f4, f1, f2, elbow, lelbow, rshoulder, lshoulder, x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5 = (
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
)

"""limits:
3- 1889 B, 3567 U, 2720 C
5- 1864 S, 1024 D, 3072 U 

4- 1933 B, 224 U, 1024 C 
6- 2337 S, 3072 D, 1024 U"""

a = dxl.get_available_ports()
print(a)
d = dxl.dxl(a[0], 1000000)
print(d.scan(8))

# x0,y0 -> Neck
# (x1,y1) (x3,y3) (x5,y5) -> Theara's left
# (x2,y2) (x4,y4) (x6,y6) -> Theara's right


def move(int c1, int c2):
    global e4, e1, e2, f4, f1, f2, x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5, relbow, lelbow, rshoulder, lshoulder

   # for right:
    n = np.array([(y0 - y2), (x0 - x2)])
    s = np.array([(y2 - y4), (x2 - x4)])
    l2 = np.array([(y4 - y6), (x4 - x6)])

    mn = (np.sqrt(n.dot(n))) + 1
    ms = (np.sqrt(s.dot(s))) + 1
    ml2 = (np.sqrt(l2.dot(l2))) + 1

    if e1/f4 != c1:
        an3 = 57.296 * (math.acos((n.dot(s)) / (mn * ms)))
        m2 = angle facing down 

        if y4 > y0:
            rshoulder = int(1024 - (11.377 * (an3)))
            if rshoulder < 224:
                rshouler = 224
        elif y4 >= y0:
            rshoulder = int(1024 + (11.377 * (an3)))
            if rshoulder > 1933:
                rshoulder = 1933
    
    

    an4 = 57.296 * (math.acos((s.dot(l2)) / (ms * ml2)))
    if y6 > y4:
        relbow = int(2048 - (11.377 * (an4)))
        if relbow < 1024:
            relbow = 1024

    elif y6 <= y4:
        relbow = int(2048 + (11.377 * (an4)))
        if relbow > 3072:
            relbow = 3072

    if e1/f4 == c2:
        m1 = 2048
    else : 
        m1a = 57.296 * (math.acos(f4/e4))
        m1 = x +/- (11.377 * m1a)

    # for left:
    m = np.array([(y0 - y1), (x0 - x1)])
    t = np.array([(y1 - y3), (x1 - x3)])
    l1 = np.array([(y3 - y5), (x3 - x5)])

    mm = (np.sqrt(m.dot(m))) + 1
    mt = (np.sqrt(t.dot(t))) + 1
    ml1 = (np.sqrt(l1.dot(l1))) + 1

    an1 = 57.296 * (math.acos((m.dot(t)) / (mm * mt)))
    an2 = 57.296 * (math.acos((t.dot(l1)) / (mt * ml1)))

    if y3 < y0:
        lshoulder = int(2720 + (11.377 * (an1)))
        if lshoulder > 3567:
            lshoulder = 3567
    elif y3 >= y0:
        lshoulder = int(2720 - (11.377 * (an1)))
        if lshoulder < 1889:
            lshouler = 1889
    if y5 < y3:
        lelbow = int(2048 + (11.377 * (an2)))
        if lelbow > 3072:
            lelbow = 3072
    elif y5 >= y3:
        lelbow = int(2048 - (11.377 * (an2)))
        if lelbow > 1024:
            lelbow = 1024
    if e1/f4 == c1:
        m2 = 2048
    else : 
        m2a = 57.296 * (math.acos(f2/e2))
        m2 = x +/- (11.377 * m2a)

    dictio = {1: m1, 2: m2, 3: lshoulder, 4: rshoulder, 5: lelbow, 6: relbow}
    d.set_goal_position(dictio)

d.speed(3, 40)
d.speed(4, 40)
d.speed(5, 40)
d.speed(6, 40)
stand = {3: 2720, 4: 1024, 5: 2048, 6: 2048}
d.set_goal_position(stand)
e4, e1, e2, x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5 = posestim.advaykafunc()
e1/e4 = c1
e1/e2 = c2
time.sleep(3)
while True:
    f4, f1, f2, x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5 = posestim.advaykafunc()
    move(c1, c2)
