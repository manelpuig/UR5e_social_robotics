# Level 2 Professional Modular Python Architecture

This folder contains a **professional Python package** version of the social robot application.
It is the intermediate step between:

- **Level 1**: one single monolithic Python script
- **Level 4**: a full ROS 2 distributed architecture

The objective is to keep the same main functionalities while organizing the code as a real Python project.

---

## Project structure

```text
level2_modular_python_professional/
├── README.md
├── requirements.txt
├── setup.py
├── pyproject.toml
├── resources/
│   ├── roboDK/
│   │   └── Social_UR5e.rdk
│   └── pictures/
│       └── Manel_ref.png
└── social_robot_app/
    ├── __init__.py
    ├── config.py
    ├── chatgpt_interpreter.py
    ├── social_robot_hri.py
    ├── social_robot_perception.py
    ├── ur5e_social_motion.py
    └── main.py
```

---

## Structure overview

### `setup.py`
Defines the Python package, dependencies, and the executable entry point.

### `pyproject.toml`
Defines the modern Python build system. It tells Python how the project should be built.

### `requirements.txt`
Lists the external Python libraries required by the project.

### `resources/`
Contains external assets used by the application.

- `roboDK/Social_UR5e.rdk` -> RoboDK project file
- `pictures/Manel_ref.png` -> reference face image

### `social_robot_app/`
This is the real Python package containing the source code.

#### `__init__.py`
Marks the folder as a Python package.

#### `config.py`
Central configuration file:
- robot IP and port
- voice settings
- OpenAI model
- file paths
- camera index

#### `chatgpt_interpreter.py`
Interprets spoken commands:
- first with local keyword logic
- then with GPT fallback if needed

#### `social_robot_hri.py`
Handles human-robot voice interaction:
- text-to-speech
- microphone listening
- speech recognition

#### `social_robot_perception.py`
Handles perception:
- camera capture
- face recognition
- person identification

#### `ur5e_social_motion.py`
Controls the robot:
- RoboDK loading
- target access
- URScript socket communication
- execution of social motions

#### `main.py`
Coordinates the whole application:
- creates all modules
- runs the interaction loop
- starts voice, perception, command interpretation, and motion execution

---

## Why this structure is important

A professional Python structure is important because it improves:

### Modularity
Each file has a clear responsibility.

### Maintainability
The code is easier to update and debug.

### Reusability
Modules can be reused in other projects.

### Scalability
New features can be added with less risk of breaking the whole program.

### Professional software practice
Students learn a structure closer to real robotics and software engineering workflows.

---

## Relation with ROS 2

This Level 2 structure is still **not ROS 2**, but it already resembles a ROS 2 `ament_python` package:

- there is a `setup.py`
- there is a package directory
- there is an executable entry point
- there is a separation between project metadata and source code

This makes it an excellent academic transition before moving to the final ROS 2 architecture.

---

## Installation

From this folder:

```bash
py -3.10 -m pip install -e .
```
> You can specify the Python version and in this case has to be equal or higher than 3.10

---

## Execution

After installation:

```bash
social-robot-app
```

Alternative execution:

```bash
python -m social_robot_app.main
```

---

## Important note

To run correctly, you must place the following files in:

- `resources/roboDK/Social_UR5e.rdk`
- `resources/pictures/Manel_ref.png`

These resource files are not included in this ZIP.
