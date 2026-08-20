#!/usr/bin/env python3
"""Face-verification helper used by the optional ROS 2 HRI gate."""

from pathlib import Path

import cv2
import face_recognition


class FaceVerifier:
    def __init__(self, reference_image, camera_index=0, tolerance=0.6):
        self.reference_image = Path(reference_image).expanduser()
        self.camera_index = camera_index
        self.tolerance = tolerance

    def verify(self):
        if not self.reference_image.is_file():
            raise FileNotFoundError(
                f'Reference image not found: {self.reference_image}'
            )

        image = face_recognition.load_image_file(str(self.reference_image))
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            raise RuntimeError('No face found in the reference image.')

        camera = cv2.VideoCapture(self.camera_index)
        if not camera.isOpened():
            raise RuntimeError(f'Camera {self.camera_index} is not available.')

        print('[FACE] Look at the camera. Press Q to cancel.')
        try:
            while True:
                ok, frame = camera.read()
                if not ok:
                    continue

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                faces = face_recognition.face_encodings(rgb_frame)
                authorised = bool(faces) and face_recognition.compare_faces(
                    [encodings[0]], faces[0], tolerance=self.tolerance
                )[0]

                label = 'AUTHORISED' if authorised else 'UNKNOWN'
                color = (0, 255, 0) if authorised else (0, 0, 255)
                cv2.putText(
                    frame, label, (30, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, color, 2
                )
                cv2.imshow('Face verification', frame)

                if authorised:
                    cv2.waitKey(750)
                    return True
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    return False
        finally:
            camera.release()
            cv2.destroyAllWindows()
