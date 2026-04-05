# Voice-Controlled RoboDK UR5e Script

## Libraries Used

* **robodk.robolink**
  Connects Python with RoboDK and allows control of the robot.

* **robodk.robomath**
  Provides mathematical tools for robot pose operations.

* **time**
  Adds delays between actions when needed.

* **re**
  Used to clean and normalize recognized speech text.

* **speech_recognition**
  Converts microphone audio into text commands.

* **pyttsx3**
  Converts text into speech through the PC speakers.

### Installation

If you are working on Windows, Install:
````python
python -m pip install SpeechRecognition pyttsx3 pyaudio
````

## What the Program Does

This script allows voice control of a **UR5e robot in RoboDK**.

Workflow:

1. Loads a RoboDK project file.
2. Waits for a voice command starting with the word **"robot"**.
3. Recognizes one of three commands:

   * `robot init`
   * `robot hand shake`
   * `robot give me five`
4. Executes the corresponding robot movement.
5. Speaks status messages before and after each motion.
6. Keeps listening for the next command until:

   * `robot exit`

# Face Recognition

We can add `Face recognition` to detect the user's face and make the robot to say his name
    - Install:
        ````python
        python -m pip install face_recognition opencv-python numpy
        ````
    - Test with a simple program:
        ````python
        python test_face_webcam.py
        ````

# Voice and Vision Social Robot

To include the face recognition in the voice control program, we have made a more proffessional structure with classes and methods to make the code more modular and easier to understand.

## Structure

The program is organized into four main classes:

- **RobotController**  
  Loads the RoboDK station and executes the predefined robot motions.

- **VoiceCommandInterface**  
  Handles speech recognition, command parsing, and text-to-speech.

- **FaceIdentifier**  
  Uses the PC camera and `face_recognition` to identify a known person.

- **SocialRobotApp**  
  Coordinates the full workflow: identify the user, listen for a voice command, execute the robot motion, and speak feedback messages.

## What the Code Does

This script creates a simple voice-controlled social robot application in RoboDK.

Workflow:

1. Loads the RoboDK project and configures the UR5e robot.
2. Identifies the person in front of the camera from a known face image.
3. Waits for a spoken command starting with the activation word **"robot"**.
4. Recognizes a predefined command such as:
   - `init`
   - `hand shake`
   - `give me five`
   - `exit`
5. Executes the corresponding robot motion.
6. Speaks messages before and after the motion, sometimes including the recognized person's name.
7. Keeps running in a loop until the user says the exit command.

**Execute:**
````python
python voice_vision_social_sw.py
````

# Voice, Vision and GPT Interpretation in Social Robot

To further enhance the social robot, we can integrate a GPT-based natural language understanding module to interpret more complex commands and provide more dynamic responses.

This would involve sending the recognized speech text to a GPT model (like OpenAI's API) and using the response to determine the robot's actions and spoken feedback.

You have to install the OpenAI library and set up your API key:
````python
python -m pip install openai speechrecognition pyttsx3 opencv-python face_recognition numpy
python -m pip install python-dotenv
````

Then, you can modify the `VoiceCommandInterface` class to include a method that sends the recognized command to the GPT model and processes the response to determine the robot's actions.

You need to create an API Key to:
- authorize your python script to use ChatGPT
- associate your usage with your account for billing and monitoring purposes

To obtain this key:
- Go to https://platform.openai.com/api-keys
- Select `Create new secret key`
- Copy the generated key and store it securely (you will need it in your script)
- You have to add the API key to your environment variables: 
  ````bash
  setx OPENAI_API_KEY "LA_TEVA_NOVA_API_KEY"
  ````
  > You can also create a `.env` file in the same directory as your script and add the line:
  `OPENAI_API_KEY=your_api_key_here`
- To buy credits and see usage: https://platform.openai.com/settings/organization/usage


## Structure

The program is organized into the following classes:

- **CONFIG**
  Central configuration for API key, robot file path, speech settings, camera index, activation word, and known faces.

- **RobotController**
  Loads the RoboDK station and executes predefined robot motions (`init`, `hand_shake`, `give_me_5`).

- **VoiceInterface**
  Handles speech recognition (microphone input) and text-to-speech feedback.

- **ChatGPTInterpreter**
  Sends recognized speech to ChatGPT and converts it into a valid robot command.

- **FaceIdentifier**
  Uses the PC camera and `face_recognition` to identify a known person.

- **SocialRobotApp**
  Coordinates the workflow between vision, voice, ChatGPT, and robot motion execution.

---

## Program Workflow

1. Load RoboDK station.
2. Identify the person using the camera.
3. Wait for a spoken command starting with the activation word **"robot"**.
4. Send the spoken text to ChatGPT.
5. Convert the text into one allowed command:
   - `init`
   - `hand_shake`
   - `give_me_5`
   - `exit`
6. Execute the corresponding robot motion.
7. Speak status messages before and after execution.
8. Continue waiting for the next command.

---

## Differences Compared to the Previous Version

Main improvements:

- Added **CONFIG class** to centralize all parameters.
- Added **ChatGPTInterpreter** to replace manual keyword parsing.
- Commands can now be spoken in natural language instead of fixed phrases.
- Cleaner modular architecture for future extensions (YOLO, 3D camera, ROS2).
- Easier maintenance: paths, API key, and settings are edited in one place only.

Example improvement:

Previous version:
```
robot hand shake
```

New version:
```
robot please shake my hand
robot let's do a high five
robot go to the initial position
```
