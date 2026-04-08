import math
import numpy as np
import serial
import time
import keyboard

# ================= ARM PARAMETERS =================
L1 = 130
L2 = 130

# ================= SERIAL CONFIG =================
PORT = 'COM3'
BAUD = 9600
STEP_DELAY = 0.005
MAX_STEP = 20
CART_STEP = 5
MANUAL_STEP = 3

arduino = serial.Serial(PORT, BAUD)
time.sleep(2)

# ================= FORWARD KINEMATICS =================
def forward(theta1_deg, theta2_deg):
    theta2_deg = 90 - theta2_deg
    theta1 = math.radians(theta1_deg)
    theta2 = math.radians(theta2_deg)

    x = L1*math.cos(theta1) + L2*math.cos(theta1+theta2)
    y = L1*math.sin(theta1) + L2*math.sin(theta1+theta2)

    return np.round(np.array([x, y]), 6)

# ================= INVERSE KINEMATICS =================
def inverse(x, y):
    c2 = (x**2 + y**2 - L1**2 - L2**2) / (2*L1*L2)
    c2 = max(-1, min(1, c2))

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

    pos[0][1] = 90 - pos[0][1]
    pos[1][1] = 90 - pos[1][1]

    return pos

# ================= SERIAL SEND =================
def send_servo(index, angle):
    cmd = f"{index}:{int(angle)}\n"
    arduino.write(cmd.encode())

# ================= SMOOTH MOVE =================
def move_smooth(target):
    global current_position
    moving = True

    while moving:
        moving = False

        for i in range(6):
            diff = target[i] - current_position[i]

            if abs(diff) > MAX_STEP:
                moving = True
                step = MAX_STEP if diff > 0 else -MAX_STEP
                current_position[i] += step
            elif diff != 0:
                moving = True
                current_position[i] = target[i]

            send_servo(i+1, current_position[i])

        time.sleep(STEP_DELAY)

# ================= GO TO FRONT =================
front_position = [88, 5, 90, 180, 90, 90]
current_position = front_position.copy()

print("Moving to FRONT position...")
move_smooth(front_position)
time.sleep(1)

theta2 = current_position[3]
theta1 = current_position[4]
x, y = forward(theta1, theta2)

print("Keyboard Control Started")
print("WASD = XY control")
print("E/R = index0 +/-")
print("T/Y = index1 +/-")
print("Q = Quit")

# ================= MAIN LOOP =================
while True:

    moved = False

    # ===== Cartesian Control =====
    if keyboard.is_pressed('w'):
        y += CART_STEP
        moved = True
    elif keyboard.is_pressed('s'):
        y -= CART_STEP
        moved = True
    elif keyboard.is_pressed('a'):
        x -= CART_STEP
        moved = True
    elif keyboard.is_pressed('d'):
        x += CART_STEP
        moved = True

    # ===== Manual Index 0 =====
    elif keyboard.is_pressed('e'):
        current_position[0] = min(180, current_position[0] + MANUAL_STEP)
        send_servo(1, current_position[0])
        print("Index0:", current_position[0])
        time.sleep(0.2)
        continue

    elif keyboard.is_pressed('r'):
        current_position[0] = max(0, current_position[0] - MANUAL_STEP)
        send_servo(1, current_position[0])
        print("Index0:", current_position[0])
        time.sleep(0.2)
        continue

    # ===== Manual Index 1 =====
    elif keyboard.is_pressed('t'):
        current_position[1] = min(180, current_position[1] + MANUAL_STEP)
        send_servo(2, current_position[1])
        print("Index1:", current_position[1])
        time.sleep(0.2)
        continue

    elif keyboard.is_pressed('y'):
        current_position[1] = max(0, current_position[1] - MANUAL_STEP)
        send_servo(2, current_position[1])
        print("Index1:", current_position[1])
        time.sleep(0.2)
        continue

    elif keyboard.is_pressed('q'):
        print("Exiting control")
        break

    if not moved:
        continue

    # ===== Apply IK =====
    try:
        angles = inverse(x, y)

        if abs(angles[0][0] - theta1) < abs(angles[1][0] - theta1):
            new_theta1, new_theta2 = angles[0]
        else:
            new_theta1, new_theta2 = angles[1]

        target = current_position.copy()
        target[3] = new_theta2
        target[4] = new_theta1

        move_smooth(target)

        theta1 = new_theta1
        theta2 = new_theta2

        print(f"X={x:.2f}, Y={y:.2f}")
        time.sleep(0.2)

    except ValueError:
        print("Out of workspace!")
        time.sleep(0.2)

print("Control Ended")
