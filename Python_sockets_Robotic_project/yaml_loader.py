#!/usr/bin/env python3

import yaml


VALID_MOTIONS = {"moveJ", "moveL"}


def load_yaml_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    validate_motion_yaml(data)

    return data


def load_yaml_text(text: str) -> dict:
    data = yaml.safe_load(text)

    validate_motion_yaml(data)

    return data


def validate_motion_yaml(data: dict):
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a dictionary.")

    if "steps" not in data:
        raise ValueError("YAML must contain a 'steps' field.")

    if not isinstance(data["steps"], list):
        raise ValueError("'steps' must be a list.")

    for i, step in enumerate(data["steps"]):

        if "motion" not in step:
            raise ValueError(f"Step {i} has no 'motion' field.")

        motion = step["motion"]

        if motion not in VALID_MOTIONS:
            raise ValueError(f"Step {i} has invalid motion type: {motion}")

        if motion == "moveJ":
            if "joints_deg" not in step:
                raise ValueError(f"Step {i} moveJ requires 'joints_deg'.")

            if len(step["joints_deg"]) != 6:
                raise ValueError(f"Step {i} joints_deg must contain 6 values.")

        if motion == "moveL":
            if "target_xyz_mm" not in step:
                raise ValueError(f"Step {i} moveL requires 'target_xyz_mm'.")

            if "target_rpy_deg" not in step:
                raise ValueError(f"Step {i} moveL requires 'target_rpy_deg'.")

            if len(step["target_xyz_mm"]) != 3:
                raise ValueError(f"Step {i} target_xyz_mm must contain 3 values.")

            if len(step["target_rpy_deg"]) != 3:
                raise ValueError(f"Step {i} target_rpy_deg must contain 3 values.")