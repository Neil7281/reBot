#!/usr/bin/env python3
"""
continuous_smooth_motion.py

Runs the repo's trajectory-control example and feeds it a repeating sequence
of smooth Cartesian waypoints for continuous motion.

Before running:
1. Power the arm and make sure the workspace is clear.
2. Confirm manual tests already work.
3. Keep one hand near power-off / emergency stop.

Usage:
    uv run python continuous_smooth_motion.py
"""

from __future__ import annotations

import subprocess
import sys
import time
import signal


# Conservative demo waypoints:
# x, y, z, roll, pitch, yaw, duration
#
# Units:
# - x, y, z in meters
# - roll, pitch, yaw in radians
# - duration in seconds
#
# These stay fairly close to center and use gentle durations.
WAYPOINTS = [
    (0.22,  0.00, 0.18, 0.00, 0.35,  0.00, 1.2),
    (0.30,  0.15, 0.25, 0.00, 0.50,  0.35, 1.2),
    (0.38,  0.00, 0.32, 0.00, 0.60,  0.00, 1.2),
    (0.30, -0.15, 0.25, 0.00, 0.50, -0.35, 1.2),
]

CMD = ["uv", "run", "python", "example/8_arm_traj_control.py"]


def start_controller() -> subprocess.Popen:
    proc = subprocess.Popen(
        CMD,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    return proc


def main() -> int:
    proc = start_controller()

    def shutdown(*_args):
        try:
            if proc.stdin:
                proc.stdin.write("q\n")
                proc.stdin.flush()
        except Exception:
            pass

        time.sleep(0.5)

        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Let the controller start up.
    time.sleep(2.0)

    if proc.poll() is not None:
        print("Trajectory controller exited immediately.")
        return 1

    print("Started trajectory controller.")
    print("Sending continuous smooth motion waypoints...")
    print("Press Ctrl+C to stop.")

    waypoint_index = 0

    while True:
        x, y, z, roll, pitch, yaw, duration = WAYPOINTS[waypoint_index]
        line = f"{x:.4f} {y:.4f} {z:.4f} {roll:.4f} {pitch:.4f} {yaw:.4f} {duration:.2f}\n"

        print(f">>> {line.strip()}")

        try:
            assert proc.stdin is not None
            proc.stdin.write(line)
            proc.stdin.flush()
        except BrokenPipeError:
            print("Controller pipe closed.")
            return 1

        # Wait slightly longer than the commanded duration
        # so each segment finishes before the next begins.
        time.sleep(duration + 0.3)

        if proc.poll() is not None:
            print("Trajectory controller exited.")
            return proc.returncode or 0

        waypoint_index = (waypoint_index + 1) % len(WAYPOINTS)


if __name__ == "__main__":
    raise SystemExit(main())
