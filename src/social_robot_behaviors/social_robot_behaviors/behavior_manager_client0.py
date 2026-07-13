#!/usr/bin/env python3

from pathlib import Path
from typing import Optional


class BehaviorManagerClient:

    def __init__(self, motions_dir: str):

        self.motions_dir = Path(motions_dir)

        self.motions = {
            "init": "init.yaml",
            "home": "home.yaml",
            "hand_shake": "handshake.yaml",
            "give5": "give5.yaml",
        }

    def get_motion_file(self, command: str) -> Optional[str]:

        motion_name = self.motions.get(command)

        if motion_name is None:
            return None

        return str(self.motions_dir / motion_name)