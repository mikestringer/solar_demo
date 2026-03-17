import time
from collections import deque

import board
import busio
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from adafruit_ina219 import INA219

# -----------------------------
# INA219 setup
# -----------------------------
i2c = busio.I2C(board.SCL, board.SDA)
ina = INA219(i2c)

# -----------------------------
# Data storage
# -----------------------------
MAX_POINTS = 60
times = deque(maxlen=MAX_POINTS)
powers = deque(maxlen=MAX_POINTS)

start_time = time.time()
max_power_seen = 0.0

# -----------------------------
# Figure layout
# -----------------------------
fig = plt.figure(figsize=(10, 6))
gs = fig.add_gridspec(3, 1, height_ratios=[1.2, 0.8, 2.0], hspace=0.45)

ax_top = fig.add_subplot(gs[0])
ax_meter = fig.add_subplot(gs[1])
ax_graph = fig.add_subplot(gs[2])

for ax in (ax_top, ax_meter):
    ax.set_axis_off()

# Top text placeholders
title_text = ax_top.text(
    0.5, 0.92, "SOLAR PANEL OUTPUT",
    ha="center", va="center", fontsize=20, fontweight="bold",
    transform=ax_top.transAxes
)

voltage_label = ax_top.text(
    0.18, 0.62, "Voltage",
    ha="center", va="center", fontsize=16, fontweight="bold",
    transform=ax_top.transAxes
)
current_label = ax_top.text(
    0.50, 0.62, "Current",
    ha="center", va="center", fontsize=16, fontweight="bold",
    transform=ax_top.transAxes
)
power_label = ax_top.text(
    0.82, 0.62, "Power",
    ha="center", va="center", fontsize=16, fontweight="bold",
    transform=ax_top.transAxes
)

voltage_value = ax_top.text(
    0.18, 0.28, "--.-- V",
    ha="center", va="center", fontsize=22,
    transform=ax_top.transAxes
)
current_value = ax_top.text(
    0.50, 0.28, "---.- mA",
    ha="center", va="center", fontsize=22,
    transform=ax_top.transAxes
)
power_value = ax_top.text(
    0.82, 0.28, "---.- mW",
    ha="center", va="center", fontsize=22,
    transform=ax_top.transAxes
)

# Efficiency meter placeholders
meter_title = ax_meter.text(
    0.02, 0.85, "Efficiency Meter",
    ha="left", va="center", fontsize=16, fontweight="bold",
    transform=ax_meter.transAxes
)

meter_bar_bg = plt.Rectangle((0.02, 0.30), 0.76, 0.28, fill=False, linewidth=2,
                             transform=ax_meter.transAxes)
ax_meter.add_patch(meter_bar_bg)

meter_bar = plt.Rectangle((0.02, 0.30), 0.0, 0.28, transform=ax_meter.transAxes)
ax_meter.add_patch(meter_bar)

meter_text = ax_meter.text(
    0.82, 0.44, "0%",
    ha="left", va="center", fontsize=20, fontweight="bold",
    transform=ax_meter.transAxes
)

best_power_text = ax_meter.text(
    0.02, 0.05, "Best power seen: 0.0 mW",
    ha="left", va="bottom", fontsize=11,
    transform=ax_meter.transAxes
)

# Graph setup
line_power, = ax_graph.plot([], [], linewidth=2, label="Power (mW)")
ax_graph.set_title("Live Power Graph", fontsize=14, fontweight="bold")
ax_graph.set_xlabel("Time (s)")
ax_graph.set_ylabel("Power (mW)")
ax_graph.grid(True)
ax_graph.legend(loc="upper left")

def update(frame):
    global max_power_seen

    now = time.time() - start_time

    try:
        voltage = ina.bus_voltage
        current = ina.current
        power = voltage * current  # mW because V * mA = mW
    except Exception as e:
        print(f"Sensor read error: {e}")
        return (
            voltage_value, current_value, power_value,
            meter_bar, meter_text, best_power_text, line_power
        )

    if power > max_power_seen:
        max_power_seen = power

    efficiency = (power / max_power_seen * 100.0) if max_power_seen > 0 else 0.0
    efficiency = max(0.0, min(100.0, efficiency))

    times.append(now)
    powers.append(power)

    # Update top numeric display
    voltage_value.set_text(f"{voltage:0.2f} V")
    current_value.set_text(f"{current:0.1f} mA")
    power_value.set_text(f"{power:0.1f} mW")

    # Update efficiency meter
    meter_bar.set_width(0.76 * (efficiency / 100.0))
    meter_text.set_text(f"{efficiency:0.0f}%")
    best_power_text.set_text(f"Best power seen: {max_power_seen:0.1f} mW")

    # Update graph
    if len(times) > 1:
        x_vals = [t - times[0] for t in times]
    else:
        x_vals = [0]

    line_power.set_data(x_vals, list(powers))

    ax_graph.set_xlim(0, max(10, x_vals[-1] if x_vals else 10))
    ymax = max(100, max(powers) * 1.2 if powers else 100)
    ax_graph.set_ylim(0, 15)
    ax_graph.set_yticks([0, 2, 4, 6, 8, 10, 12, 14, 16])

    return (
        voltage_value, current_value, power_value,
        meter_bar, meter_text, best_power_text, line_power
    )

ani = FuncAnimation(fig, update, interval=500, cache_frame_data=False)

try:
    manager = plt.get_current_fig_manager()
    manager.full_screen_toggle()
except Exception:
    pass

plt.show()
