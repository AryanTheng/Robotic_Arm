import math
import numpy as np

L1 = 130
L2 = 130

def forward(theta1_deg, theta2_deg):
    # convert to radians
    theta2_deg = 90 - theta2_deg
    theta1 = math.radians(theta1_deg)
    theta2 = math.radians(theta2_deg)

    x = L1*math.cos(theta1) + L2*math.cos(theta1+theta2)
    y = L1*math.sin(theta1) + L2*math.sin(theta1+theta2)

    return np.round(np.array([x, y]), 6)


def inverse(x, y):
    c2 = (x**2 + y**2 - L1**2 - L2**2) / (2*L1*L2)

    theta2_1 = math.acos(c2)
    theta2_2 = -math.acos(c2)

    theta1_1 = math.atan2(y, x) - math.atan2(
        L2*math.sin(theta2_1),
        L1 + L2*math.cos(theta2_1)
    )

    theta1_2 = math.atan2(y, x) - math.atan2(
        L2*math.sin(theta2_2),
        L1 + L2*math.cos(theta2_2)
    )
    pos = np.degrees([
        [theta1_1, theta2_1],
        [theta1_2, theta2_2]
    ])
    pos[0][1]=90-pos[0][1]
    pos[1][1]=90-pos[1][1]

    return pos



# Test
pos = forward(90, 180)
print("forward:", pos)

angles = inverse(pos[0], pos[1])
print("inverse:", angles)

angles = inverse(0, 260)
print("inverse:", angles)