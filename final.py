import dxl
import math
import numpy as np
import posestim

x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5 = (
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
print(d.scan())

# x0,y0 -> Neck
# (x1,y1) (x3,y3) (x5,y5) -> Theara's left
# (x2,y2) (x4,y4) (x6,y6) -> Theara's right


def move():
    global x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5
    # for right:
    m = np.array([(y0 - y1), (x0 - x1)])
    t = np.array([(y1 - y3), (x1 - x3)])
    l1 = np.array([(y3 - y5), (x3 - x5)])

    mm = np.sqrt(m.dot(m))
    mt = np.sqrt(t.dot(t))
    ml1 = np.sqrt(l1.dot(l1))

    an3 = 57.296 * (math.acos((m.dot(t)) / (mm * mt)))
    an4 = 57.296 * (math.acos((t.dot(l1)) / (mt * ml1)))

    if an3 > 0:
        rshoulder = int(2720 - (11.377 * (an1)))
        if rshoulder < 1889:
            rshoulder = 1889
    if an4 > 0:
        relbow = int(2048 - (11.377 * (an2)))
        if relbow < 1024:
            relbow = 1024
    if an3 <= 0:
        rshoulder = int(2720 + (11.377 * (an1)))
        if rshoulder > 3567:
            rshouler = 3567
    if an4 <= 0:
        relbow = int(2048 + (11.377 * (an2)))
        if relbow > 3072:
            relbow = 3072

    # for left:
    n = np.array([(y0 - y2), (x0 - x2)])
    s = np.array([(y2 - y4), (x2 - x4)])
    l2 = np.array([(y4 - y6), (x4 - x6)])

    mn = np.sqrt(n.dot(n))
    ms = np.sqrt(s.dot(s))
    ml2 = np.sqrt(l2.dot(l2))

    an1 = 57.296 * (math.acos((n.dot(s)) / (mn * ms)))
    an2 = 57.296 * (math.acos((s.dot(l2)) / (ms * ml2)))

    if an1 > 0:
        lshoulder = int(1024 - (11.377 * (an1)))
        if lshoulder < 224:
            lshoulder = 224
    if an2 > 0:
        lelbow = int(2048 - (11.377 * (an2)))
        if lelbow < 1024:
            lelbow = 1024
    if an1 <= 0:
        lshoulder = int(1024 + (11.377 * (an1)))
        if lshoulder > 1933:
            lshouler = 1933
    if an2 <= 0:
        lelbow = int(2048 + (11.377 * (an2)))
        if lelbow > 3072:
            lelbow = 3072

    dictio = {3: rshoulder, 4: lshoulder, 5: relbow, 6: lelbow}
    d.speed(3, 40)
    d.speed(4, 40)
    d.speed(5, 40)
    d.speed(6, 40)
    d.set_goal_position(dictio)


while True:
    x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5 = posestim.advaykafunc()
    move()
