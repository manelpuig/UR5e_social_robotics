#!/usr/bin/env python3

from robodk.robolink import *
from robodk.robomath import *

import socket
import math
import time
import os

from config import ROBOT_IP, ROBOT_PORT, RDK_FILE


class RobotController:

    def __init__(self):
        self.robot_socket = None
        self.real_robot_connected = False

        print("Loading RoboDK...")
        self.rdk = Robolink()
        time.sleep(2)

        self.rdk.AddFile(os.path.abspath(RDK_FILE))
        time.sleep(2)

        self.robot = self.rdk.Item("UR5e")
        self.base = self.rdk.Item("UR5e Base")
        self.tool = self.rdk.Item("Hand")

        self.robot.setPoseFrame(self.base)
        self.robot.setPoseTool(self.tool)

        self.connect_robot()
        self.set_tcp_from_robodk()

    def connect_robot(self):
        try:
            self.robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.robot_socket.settimeout(2.0)
            self.robot_socket.connect((ROBOT_IP, ROBOT_PORT))

            self.real_robot_connected = True
            print(f"Connected to UR5e at {ROBOT_IP}:{ROBOT_PORT}")

        except Exception as e:
            print(f"Robot connection failed: {e}")
            self.robot_socket = None
            self.real_robot_connected = False

    def send_script(self, script: str, wait_time: float = 0.0) -> bool:
        if not self.real_robot_connected or self.robot_socket is None:
            print("Robot not connected.")
            return False

        try:
            self.robot_socket.sendall((script.strip() + "\n").encode("utf-8"))
            print("[URSCRIPT]", script)

            if wait_time > 0:
                time.sleep(wait_time)

            return True

        except Exception as e:
            print(f"Error sending URScript: {e}")
            self.real_robot_connected = False
            return False

    def set_tcp_from_robodk(self):
        x, y, z, rx, ry, rz = Pose_2_UR(self.robot.PoseTool())

        script = (
            f"set_tcp(p[{x/1000.0:.6f},{y/1000.0:.6f},{z/1000.0:.6f},"
            f"{rx:.6f},{ry:.6f},{rz:.6f}])"
        )

        return self.send_script(script, wait_time=1.0)

    def movej(self, joints_deg, a=1.2, v=0.5, t=-1, r=0.0):
        joints_rad = [math.radians(q) for q in joints_deg]

        if t is not None and t >= 0:
            script = (
                f"movej([{joints_rad[0]:.6f},{joints_rad[1]:.6f},{joints_rad[2]:.6f},"
                f"{joints_rad[3]:.6f},{joints_rad[4]:.6f},{joints_rad[5]:.6f}], "
                f"a={a}, v={v}, t={t}, r={r})"
            )
            wait_time = t
        else:
            script = (
                f"movej([{joints_rad[0]:.6f},{joints_rad[1]:.6f},{joints_rad[2]:.6f},"
                f"{joints_rad[3]:.6f},{joints_rad[4]:.6f},{joints_rad[5]:.6f}], "
                f"a={a}, v={v}, r={r})"
            )
            wait_time = 0.0

        return self.send_script(script, wait_time=wait_time)

    def movel_pose(self, xyz_mm, rpy_deg, a=1.2, v=0.15, t=-1, r=0.0):
        x, y, z = xyz_mm
        roll, pitch, yaw = rpy_deg

        target_pose = (
            transl(x, y, z)
            * rotx(math.radians(roll))
            * roty(math.radians(pitch))
            * rotz(math.radians(yaw))
        )

        x, y, z, rx, ry, rz = Pose_2_UR(target_pose)

        if t is not None and t >= 0:
            script = (
                f"movel(p[{x/1000.0:.6f},{y/1000.0:.6f},{z/1000.0:.6f},"
                f"{rx:.6f},{ry:.6f},{rz:.6f}], "
                f"a={a}, v={v}, t={t}, r={r})"
            )
            wait_time = t
        else:
            script = (
                f"movel(p[{x/1000.0:.6f},{y/1000.0:.6f},{z/1000.0:.6f},"
                f"{rx:.6f},{ry:.6f},{rz:.6f}], "
                f"a={a}, v={v}, r={r})"
            )
            wait_time = 0.0

        return self.send_script(script, wait_time=wait_time)

    def execute_sequence(self, data: dict):
        print("\nExecuting sequence:", data.get("sequence_name", "unnamed"))

        for step in data["steps"]:
            name = step.get("name", "unnamed_step")
            motion = step["motion"]

            a = step.get("acceleration", 1.2)
            v = step.get("velocity", 0.25)
            t = step.get("time", -1)
            r = step.get("blend", 0.0)

            print(f"\nStep: {name}")
            print(f"Motion: {motion}")

            if motion == "moveJ":
                self.movej(
                    joints_deg=step["joints_deg"],
                    a=a,
                    v=v,
                    t=t,
                    r=r
                )

            elif motion == "moveL":
                self.movel_pose(
                    xyz_mm=step["target_xyz_mm"],
                    rpy_deg=step["target_rpy_deg"],
                    a=a,
                    v=v,
                    t=t,
                    r=r
                )

    def shutdown(self):
        if self.robot_socket:
            self.robot_socket.close()

        try:
            self.rdk.CloseRoboDK()
        except Exception:
            pass