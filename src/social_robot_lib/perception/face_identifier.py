import face_recognition
import cv2
from social_robot_lib.config.settings import KNOWN_PERSON

REFERENCE_IMAGE = "Documentation/Files/pictures/Manel_ref.png"

def identify_person():

    try:
        reference = face_recognition.load_image_file(REFERENCE_IMAGE)
        reference_encoding = face_recognition.face_encodings(reference)[0]

        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return None

        rgb_frame = frame[:, :, ::-1]

        encodings = face_recognition.face_encodings(rgb_frame)

        for encoding in encodings:
            match = face_recognition.compare_faces([reference_encoding], encoding)

            if match[0]:
                return KNOWN_PERSON

        return None

    except Exception:
        return None
