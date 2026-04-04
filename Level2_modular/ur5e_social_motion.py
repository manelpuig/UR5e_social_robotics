from robodk.robolink import Robolink
from robodk.robomath import Pose_2_UR
import socket
import time
import numpy as np

from config import CONFIG


class RobotController:

    def __init__(
        self,
        use_real_robot: bool = True,
        robot_ip: str = "192.168.1.4",
        robot_port: int = 30002,
    ):
        self.use_real_robot = use_real_robot
        self.robot_ip = robot_ip
        self.robot_port = robot_port
        self.robot_socket = None
        self.real_robot_connected = False

        print("Loading RoboDK...")
        self.rdk = Robolink()
        time.sleep(2)

        print("Loading RoboDK project...")
        self.rdk.AddFile(CONFIG.RDK_FILE)
        time.sleep(2)

        # Important: do NOT recreate Robolink() here
        self.robot = self.rdk.Item("UR5e")
        self.base = self.rdk.Item("UR5e Base")
        self.tool = self.rdk.Item("Hand")

        self.init_target = self.rdk.Item("Init")
        self.app_shake_target = self.rdk.Item("App_shake")
        self.shake_target = self.rdk.Item("Shake")
        self.app_give5_target = self.rdk.Item("App_give5")
        self.give5_target = self.rdk.Item("Give5")

        self.robot.setPoseFrame(self.base)
        self.robot.setPoseTool(self.tool)
        self.robot.setSpeed(20)

        if self.use_real_robot:
            self.connect_robot()
            if self.real_robot_connected:
                self.set_tcp_from_robodk(wait_time=1.0)

    # -------------------------------------------------
    # SOCKET COMMUNICATION
    # -------------------------------------------------

    def connect_robot(self) -> bool:
        """Open a TCP socket to the real UR robot."""
        try:
            self.robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.robot_socket.settimeout(2.0)
            self.robot_socket.connect((self.robot_ip, self.robot_port))
            self.real_robot_connected = True
            print(f"Connected to real robot at {self.robot_ip}:{self.robot_port}")
            return True
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            print(f"Connection to real robot failed: {e}")
            self.robot_socket = None
            self.real_robot_connected = False
            return False

    def send_script(self, script: str, wait_time: float = 0.0) -> bool:
        """
        Send one URScript command to the real robot.
        Returns True if sent correctly, False otherwise.
        """
        if not (self.real_robot_connected and self.robot_socket):
            print("Real robot not connected. Script not sent.")
            return False

        try:
            self.robot_socket.sendall((script.strip() + "\n").encode("utf-8"))
            print(f"[URSCRIPT] {script}")
            if wait_time > 0:
                time.sleep(wait_time)
            return True
        except Exception as e:
            print(f"Error sending script: {e}")
            self.real_robot_connected = False
            return False

    def close_robot_connection(self) -> None:
        """Close the TCP socket to the real robot."""
        if self.robot_socket:
            try:
                self.robot_socket.close()
                print("Socket connection to robot closed.")
            except Exception as e:
                print(f"Error closing robot socket: {e}")
            finally:
                self.robot_socket = None
                self.real_robot_connected = False

    # -------------------------------------------------
    # TARGET-BASED MOTION HELPERS
    # -------------------------------------------------

    def movej_target(self, target, time_param=5.0, accel=1.2, speed=0.75, blend=0.0) -> bool:
        """
        Joint move to a RoboDK target.
        In real mode -> send movej by socket.
        In simulation mode -> RoboDK MoveJ.
        """
        if self.real_robot_connected and self.robot_socket:
            try:
                joints_deg = target.Joints().tolist()[0]
                joints_rad = np.radians(joints_deg)

                script = (
                    f"movej([{joints_rad[0]:.6f},{joints_rad[1]:.6f},{joints_rad[2]:.6f},"
                    f"{joints_rad[3]:.6f},{joints_rad[4]:.6f},{joints_rad[5]:.6f}], "
                    f"a={accel}, v={speed}, t={time_param}, r={blend})"
                )
                return self.send_script(script, wait_time=time_param)
            except Exception as e:
                print(f"Error preparing movej command: {e}")
                return False
        else:
            try:
                print("Simulating MoveJ in RoboDK.")
                self.robot.MoveJ(target, True)
                return True
            except Exception as e:
                print(f"Simulation MoveJ failed: {e}")
                return False

    def movel_target(self, target, time_param=5.0, accel=1.2, speed=0.25, blend=0.0) -> bool:
        """
        Linear move to a RoboDK target.
        In real mode -> send movel by socket.
        In simulation mode -> RoboDK MoveL.
        """
        if self.real_robot_connected and self.robot_socket:
            try:
                x, y, z, rx, ry, rz = Pose_2_UR(target.Pose())

                script = (
                    f"movel(p[{x/1000.0:.6f},{y/1000.0:.6f},{z/1000.0:.6f},"
                    f"{rx:.6f},{ry:.6f},{rz:.6f}], "
                    f"a={accel}, v={speed}, t={time_param}, r={blend})"
                )
                return self.send_script(script, wait_time=time_param)
            except Exception as e:
                print(f"Error preparing movel command: {e}")
                return False
        else:
            try:
                print("Simulating MoveL in RoboDK.")
                self.robot.MoveL(target, True)
                return True
            except Exception as e:
                print(f"Simulation MoveL failed: {e}")
                return False

    def set_tcp_from_robodk(self, wait_time=1.0) -> bool:
        """
        Read TCP from RoboDK tool and send set_tcp() to the real robot.
        In simulation mode just set the tool in RoboDK.
        """
        if self.real_robot_connected and self.robot_socket:
            try:
                x, y, z, rx, ry, rz = Pose_2_UR(self.robot.PoseTool())
                script = (
                    f"set_tcp(p[{x/1000.0:.6f},{y/1000.0:.6f},{z/1000.0:.6f},"
                    f"{rx:.6f},{ry:.6f},{rz:.6f}])"
                )
                return self.send_script(script, wait_time=wait_time)
            except Exception as e:
                print(f"Error sending set_tcp: {e}")
                return False
        else:
            try:
                print("Setting TCP in RoboDK simulation.")
                self.robot.setPoseTool(self.tool)
                time.sleep(wait_time)
                return True
            except Exception as e:
                print(f"Error setting TCP in simulation: {e}")
                return False

    # -------------------------------------------------
    # HIGH-LEVEL COMMANDS
    # -------------------------------------------------

    def execute(self, command: str):
        if command == "init":
            ok = self.movej_target(self.init_target, time_param=5.0)
            return "Init finished" if ok else "Init failed"

        if command == "hand_shake":
            ok1 = self.movel_target(self.app_shake_target, time_param=3.0)
            ok2 = self.movel_target(self.shake_target, time_param=1.0)
            ok3 = self.movel_target(self.app_shake_target, time_param=1.0)
            return "Hand shake finished" if (ok1 and ok2 and ok3) else "Hand shake failed"

        if command == "give_me_5":
            ok1 = self.movel_target(self.app_give5_target, time_param=3.0)
            ok2 = self.movel_target(self.give5_target, time_param=1.0)
            ok3 = self.movel_target(self.app_give5_target, time_param=1.0)
            return "Give me five finished" if (ok1 and ok2 and ok3) else "Give me five failed"

        return None

    def go_to_init(self) -> bool:
        """Move robot to safe Init pose."""
        try:
            return self.movej_target(self.init_target, time_param=5.0)
        except Exception as e:
            print(f"Error moving to Init: {e}")
            return False

    def shutdown(self) -> None:
        """Close robot socket and RoboDK cleanly."""
        try:
            self.close_robot_connection()
        except Exception as e:
            print(f"Error closing robot connection: {e}")

        try:
            print("Closing RoboDK...")
            self.rdk.CloseRoboDK()
        except Exception as e:
            print(f"Error closing RoboDK: {e}")
