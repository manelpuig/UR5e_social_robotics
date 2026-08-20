#!/usr/bin/env python3
"""Optional HRI client: face verification followed by voice control."""

from config import CAMERA_INDEX, FACE_MATCH_TOLERANCE, REFERENCE_FACE_IMAGE
from face_verification import FaceVerifier
from voice_motion_client import main as run_voice_client


def main():
    verifier = FaceVerifier(
        REFERENCE_FACE_IMAGE,
        camera_index=CAMERA_INDEX,
        tolerance=FACE_MATCH_TOLERANCE,
    )
    if not verifier.verify():
        print("[FACE] Access denied.")
        return 1

    run_voice_client()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
