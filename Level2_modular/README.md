# Modular Social Robot App

This is a Level-2 modular Python version of the original monolithic script.

## Files

- `config.py`
- `ur5e_social_motion.py`
- `social_robot_hri.py`
- `chatgpt_interpreter.py`
- `social_robot_perception.py`
- `main.py`

## Execution

Run from this folder:

```bash
python main.py
```

or:

```bash
python3 main.py
```

## Notes

- RoboDK must be installed and its Python API must be available.
- The RoboDK project file path is configured in `config.py`.
- The voice interface uses `speech_recognition` and `pyttsx3`.
- Face identification uses OpenCV and `face_recognition`.
- GPT fallback requires `OPENAI_API_KEY` in the environment or in a `.env` file.
- If you want simulation only, set:

```python
USE_REAL_ROBOT = False
```

in `config.py`.
