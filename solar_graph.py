import time
from collections import deque

import board
import busio
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from adafruit_ina219 import INA219

# Setup I2C
i2c = busio.I2C(board.SCL, board.SDA)
ina = INA219(i2c)

# Data storage
times = deque(maxlen=60)
voltages = deque(maxlen=60)
currents = deque(maxlen=60)
powers = deque(maxlen=60)

start = time.time()

fig, ax = plt.subplots()

line_v, = ax.plot([], [], label="Voltage (V)")
line_p, = ax.plot([], [], label="Power (mW)")
line_c, = ax.plot([], [], label="Current (mA)")

ax.set_xlabel("Time")
ax.set_ylabel("Value")
ax.set_title("Solar Panel Output")
ax.legend()

def update(frame):

    t = time.time() - start

    voltage = ina.bus_voltage
    current = ina.current
    power = voltage * current

    times.append(t)
    voltages.append(voltage)
    currents.append(current)
    powers.append(power)

    line_v.set_data(times, voltages)
    line_c.set_data(times, currents)
    line_p.set_data(times, powers)

    ax.relim()
    ax.autoscale_view()

    return line_v, line_c, line_p

ani = FuncAnimation(fig, update, interval=1000)

plt.show()
