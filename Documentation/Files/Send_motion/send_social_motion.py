#!/usr/bin/env python3

import subprocess
from pathlib import Path

# -------------------------
# CONFIGURACIÓ
# -------------------------

PROFESSOR_IP = "192.168.1.55"
PROFESSOR_USER = "student"

LOCAL_FOLDER = "/home/user/UR5e_social_robotics/src/ur5e_motion_utils/ur5e_robot_controller/config/"
REMOTE_FOLDER = "/home/student/UR5e_social_robotics/install/ur5e_robot_controller/share/ur5e_robot_controller/config/"

# -------------------------

filename = input("Nom del fitxer YAML: ")

local_file = Path(LOCAL_FOLDER) / filename

if not local_file.exists():
    print(f"Error: {local_file} no existeix.")
    exit(1)

cmd = [
    "scp",
    str(local_file),
    f"{PROFESSOR_USER}@{PROFESSOR_IP}:{REMOTE_FOLDER}"
]

print("Copiant fitxer...")

try:
    subprocess.run(cmd, check=True)
    print("Fitxer copiat correctament.")
except subprocess.CalledProcessError:
    print("Error en la còpia.")