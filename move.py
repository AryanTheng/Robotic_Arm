import serial
import time

# ===== CONFIG =====
PORT = 'COM3'     # Change to your port
BAUD = 9600
STEP_DELAY = 0.02   # Smaller = faster motion
MAX_STEP = 2        # Degree change per iteration

# ===== CONNECT =====
arduino = serial.Serial(PORT, BAUD)
time.sleep(2)  # Allow Arduino reset

# ===== WAYPOINTS =====
waypoints = [
    # [88, 90, 90, 90, 90, 90], # stand position
    # [88, 5, 90, 180, 90, 90], # front position
    # [88, 180, 90, 0, 90, 90], # back position
    # [88, 5, 90, 180, 90, 0], # right position
    # [88, 5, 90, 180, 90, 180], # left position
    [88, 90, 90, 90, 90, 90], #stand position
    [88, 90, 90, 90, 90, 90], # stand position
    [88, 5, 90, 180, 90, 90], # front position
    # [88, 180, 90, 0, 90, 90], # back position
    # [88, 5, 90, 180, 90, 0], # right position
    # [88, 5, 90, 180, 90, 180], # left position
    # [88, 90, 90, 90, 90, 90], #stand position,
    # [89, 34, 87, 134, 16, 89], # pick front
    # [10, 34, 87, 134, 16, 89], # pick
    [90, 66, 90, 169, 66, 76],
    [90, 75, 90, 161, 51, 74],
    [50, 75, 90, 161, 51, 74],
    [10, 180, 101, 16, 124, 89], # back drop positon
    [89, 180, 101, 16, 124, 89],    
]

# 90 66 90 169 66 76
# 90 75 90 161 51 74
# 50 75 90 161 51 74

current_position = waypoints[0].copy()

# ===== SEND FUNCTION (COLON FORMAT) =====
def send_servo(index, angle):
    cmd = f"{index}:{int(angle)}\n"
    arduino.write(cmd.encode())

# ===== SMOOTH MOVE FUNCTION =====
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

# ===== EXECUTE PATH =====
while(1):
    for point in waypoints:
        print("Moving to:", point)
        move_smooth(point)
        time.sleep(0.5)

print("Navigation complete")
