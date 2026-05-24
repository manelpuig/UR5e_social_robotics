#!/usr/bin/env python3

from robodk.robolink import *
from robodk.robomath import *

import socket
import threading
import yaml
import math
import time
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

SERVER_IP = "0.0.0.0"
SERVER_PORT = 5000

ROBOT_IP = "192.168.0.20"
ROBOT_PORT = 30002

# Options:
# "simulation_only"      -> only RoboDK simulation
# "simulation_and_real"  -> RoboDK simulation + real UR5e, if connected
# "real_only"            -> only real UR5e, if connected
EXECUTION_MODE = "simulation_only"

BASE_DIR = Path(__file__).resolve().parent
RDK_FILE = BASE_DIR / "resources" / "roboDK" / "Social_UR5e.rdk"

ROBOT_NAME = "UR5e"
BASE_NAME = "UR5e Base"
TOOL_NAME = "Hand"

MAX_YAML_SIZE_BYTES = 20000

robot_lock = threading.Lock()


# ============================================================
# ROBOT CONTROLLER
# ============================================================

class RobotController:

    def __init__(self):
        self.robot_socket = None
        self.real_robot_connected = False

        print("Loading RoboDK...")
        self.rdk = Robolink()
        time.sleep(2)

        self.load_station()
        self.load_items()

        self.connect_robot()
        self.set_tcp_from_robodk()

    def load_station(self):
        print(f"[DEBUG] RDK file: {RDK_FILE}")
        print(f"[DEBUG] RDK exists: {RDK_FILE.exists()}")

        if not RDK_FILE.exists():
            raise FileNotFoundError(f"RoboDK station not found: {RDK_FILE}")

        self.rdk.AddFile(str(RDK_FILE))
        time.sleep(2)

    def load_items(self):
        self.robot = self.rdk.Item(ROBOT_NAME, ITEM_TYPE_ROBOT)
        self.base = self.rdk.Item(BASE_NAME, ITEM_TYPE_FRAME)
        self.tool = self.rdk.Item(TOOL_NAME)

        if not self.robot.Valid():
            raise RuntimeError(f"Robot item not found in RoboDK station: {ROBOT_NAME}")

        if not self.base.Valid():
            raise RuntimeError(f"Base frame item not found in RoboDK station: {BASE_NAME}")

        if not self.tool.Valid():
            raise RuntimeError(f"Tool item not found in RoboDK station: {TOOL_NAME}")

        self.robot.setPoseFrame(self.base)
        self.robot.setPoseTool(self.tool)

        print("RoboDK station loaded correctly.")
        print(f"Robot: {ROBOT_NAME}")
        print(f"Base frame: {BASE_NAME}")
        print(f"Tool: {TOOL_NAME}")

    def connect_robot(self):
        """
        Always tries to connect to the real UR5e.
        If connection fails, the server continues and can run RoboDK simulation.
        """
        self.robot_socket = None
        self.real_robot_connected = False

        try:
            self.robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.robot_socket.settimeout(2.0)
            self.robot_socket.connect((ROBOT_IP, ROBOT_PORT))
            self.real_robot_connected = True
            print(f"Connected to real UR5e at {ROBOT_IP}:{ROBOT_PORT}")

        except Exception as e:
            print(f"Robot connection failed: {e}")
            print("Real UR5e not connected. The server will use RoboDK simulation when possible.")
            self.robot_socket = None
            self.real_robot_connected = False

    def send_script(self, script, wait_time=0.0):
        if not self.real_robot_connected:
            print("Real robot not connected. URScript not sent.")
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
        """
        Sends the RoboDK TCP to the real UR5e only if the real robot is connected.
        RoboDK simulation already uses the tool item directly.
        """
        if not self.real_robot_connected:
            print("Skipping TCP setup on real UR5e because robot is not connected.")
            return

        x, y, z, rx, ry, rz = Pose_2_UR(self.robot.PoseTool())

        script = (
            f"set_tcp(p[{x/1000.0:.6f},{y/1000.0:.6f},{z/1000.0:.6f},"
            f"{rx:.6f},{ry:.6f},{rz:.6f}])"
        )

        self.send_script(script, wait_time=1.0)

    def execute_simulation_movej(self, joints_deg):
        print("Executing moveJ in RoboDK simulation...")
        self.robot.MoveJ(joints_deg)

    def execute_simulation_movel_pose(self, xyz_mm, rpy_deg):
        print("Executing moveL in RoboDK simulation...")

        x, y, z = xyz_mm
        roll, pitch, yaw = rpy_deg

        target_pose = (
            transl(x, y, z)
            * rotx(math.radians(roll))
            * roty(math.radians(pitch))
            * rotz(math.radians(yaw))
        )

        self.robot.MoveL(target_pose)

    def build_movej_script(self, joints_deg, a=1.2, v=0.5, t=-1, r=0.0):
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

        return script, wait_time

    def build_movel_script(self, xyz_mm, rpy_deg, a=1.2, v=0.15, t=-1, r=0.0):
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

        return script, wait_time

    def movej(self, joints_deg, a=1.2, v=0.5, t=-1, r=0.0):
        script, wait_time = self.build_movej_script(joints_deg, a, v, t, r)

        success = True

        if EXECUTION_MODE in ["simulation_only", "simulation_and_real"]:
            self.execute_simulation_movej(joints_deg)

        if EXECUTION_MODE in ["real_only", "simulation_and_real"]:
            if self.real_robot_connected:
                success = self.send_script(script, wait_time=wait_time)
            else:
                print("Real robot requested, but UR5e is not connected.")
                if EXECUTION_MODE == "real_only":
                    success = False

        return success

    def movel_pose(self, xyz_mm, rpy_deg, a=1.2, v=0.15, t=-1, r=0.0):
        script, wait_time = self.build_movel_script(xyz_mm, rpy_deg, a, v, t, r)

        success = True

        if EXECUTION_MODE in ["simulation_only", "simulation_and_real"]:
            self.execute_simulation_movel_pose(xyz_mm, rpy_deg)

        if EXECUTION_MODE in ["real_only", "simulation_and_real"]:
            if self.real_robot_connected:
                success = self.send_script(script, wait_time=wait_time)
            else:
                print("Real robot requested, but UR5e is not connected.")
                if EXECUTION_MODE == "real_only":
                    success = False

        return success

    def execute_sequence(self, data):
        print("\nExecuting sequence:", data.get("sequence_name", "unnamed"))
        print(f"Execution mode: {EXECUTION_MODE}")
        print(f"Real robot connected: {self.real_robot_connected}")

        if "steps" not in data:
            raise RuntimeError("YAML file does not contain 'steps'")

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
                ok = self.movej(
                    joints_deg=step["joints_deg"],
                    a=a,
                    v=v,
                    t=t,
                    r=r
                )

            elif motion == "moveL":
                ok = self.movel_pose(
                    xyz_mm=step["target_xyz_mm"],
                    rpy_deg=step["target_rpy_deg"],
                    a=a,
                    v=v,
                    t=t,
                    r=r
                )

            else:
                raise RuntimeError(f"Unknown motion type: {motion}")

            if not ok:
                raise RuntimeError(f"Motion step failed: {name}")
            
        print("\nSequence completed successfully.")
        print("Waiting for a new motion command...\n")

    def shutdown(self):
        if self.robot_socket:
            self.robot_socket.close()
        try:
            self.rdk.CloseRoboDK()
        except:
            pass
        print("Server and RoboDK closed.")


# ============================================================
# TCP SERVER
# ============================================================

def receive_all(conn):
    chunks = []
    total_size = 0

    while True:
        chunk = conn.recv(4096)

        if not chunk:
            break

        chunks.append(chunk)
        total_size += len(chunk)

        if total_size > MAX_YAML_SIZE_BYTES:
            raise RuntimeError("YAML file too large")

    return b"".join(chunks).decode("utf-8")


def handle_client(conn, addr, robot):
    print(f"\nConnection from {addr}")

    try:
        yaml_text = receive_all(conn)

        print("\nReceived YAML:")
        print(yaml_text)

        data = yaml.safe_load(yaml_text)

        if not robot_lock.acquire(blocking=False):
            response = "ERROR: Robot is busy. Try again later.\n"
        else:
            try:
                robot.execute_sequence(data)
                response = "OK: sequence executed\n"
            finally:
                robot_lock.release()

    except Exception as e:
        response = f"ERROR: {e}\n"
        print(response)

    conn.sendall(response.encode("utf-8"))
    conn.close()


def main():

    robot = RobotController()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow fast socket close and reuse after CTRL+C
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # IMPORTANT
    server_socket.settimeout(1.0)

    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)

    print(f"\nUR5e classroom server listening on {SERVER_IP}:{SERVER_PORT}")

    try:
        while True:

            try:
                conn, addr = server_socket.accept()

            except socket.timeout:
                continue

            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr, robot),
                daemon=True
            )

            thread.start()

    except KeyboardInterrupt:
        print("\nStopping server...")

    finally:
        print("Closing server socket...")
        server_socket.close()
        robot.shutdown()
        print("Server stopped correctly.")

if __name__ == "__main__":
    main()