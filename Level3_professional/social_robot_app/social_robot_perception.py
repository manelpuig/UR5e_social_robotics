import os
import time
import cv2
import face_recognition

from social_robot_app.config import CONFIG


class FaceIdentifier:

    def __init__(self):
        self.encodings = []
        self.names = []

        for name, path in CONFIG.KNOWN_FACES.items():
            if not os.path.exists(path):
                continue

            img = face_recognition.load_image_file(path)
            enc = face_recognition.face_encodings(img)

            if enc:
                self.encodings.append(enc[0])
                self.names.append(name)

    def identify_once(self) -> str:
        cap = cv2.VideoCapture(CONFIG.CAMERA_INDEX)

        time.sleep(1)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return "friend"

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        enc = face_recognition.face_encodings(rgb)

        if not enc:
            return "friend"

        matches = face_recognition.compare_faces(self.encodings, enc[0])

        for i, match in enumerate(matches):
            if match:
                return self.names[i]

        return "friend"
