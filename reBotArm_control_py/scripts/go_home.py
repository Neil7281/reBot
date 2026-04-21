#!/usr/bin/env python3
"""
go_home.py

Moves the reBot arm to a safe home position using trajectory control.
"""

import subprocess
import time

CMD = ["uv", "run", "python", "example/8_arm_traj_control.py"]

# Safe HOME position (you can tune this later)
# x, y, z, roll, pitch, yaw, duration
HOME = (0.28, 0.00, 0.25, 0.00, 0.45, 0.00, 3.0)


def main():
    print("Starting trajectory controller...")

    proc = subprocess.Popen(
        CMD,
        stdin=subprocess.PIPE,
        text=True
    )

    # wait for controller to initialize
    time.sleep(2.0)

    x, y, z, r, p, yw, t = HOME
    cmd = f"{x} {y} {z} {r} {p} {yw} {t}\n"

    print(f"Sending HOME command: {cmd.strip()}")

    proc.stdin.write(cmd)
    proc.stdin.flush()

    # wait until motion finishes
    time.sleep(t + 1.0)

    print("Reached HOME position. Exiting.")

    # clean exit
    proc.stdin.write("q\n")
    proc.stdin.flush()

    time.sleep(0.5)
    proc.terminate()


if __name__ == "__main__":
    main()
