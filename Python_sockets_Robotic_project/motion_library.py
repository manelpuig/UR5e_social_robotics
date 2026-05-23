#!/usr/bin/env python3

from config import MOTIONS_DIR
from typing import Optional

MOTIONS = {
    "init": f"{MOTIONS_DIR}/init.yaml",
    "hand_shake": f"{MOTIONS_DIR}/hand_shake.yaml",
    "give_me_5": f"{MOTIONS_DIR}/give_me_5.yaml",
}


def get_motion_file(command: str) -> Optional[str]:
    return MOTIONS.get(command)