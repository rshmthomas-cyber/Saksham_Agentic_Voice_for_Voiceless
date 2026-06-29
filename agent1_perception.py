import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_face = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Initialize detectors
pose_detector = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

face_detector = mp_face.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Open webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
time.sleep(2)

print("Saksham Agent 1 is watching...")
print("Press Q to stop safely.")

try:
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("Camera not found. Check your webcam.")
            break

        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect face landmarks
        face_results = face_detector.process(rgb_frame)

        # Detect body pose
        pose_results = pose_detector.process(rgb_frame)

        # Draw face landmarks
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    mp_face.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles
                    .get_default_face_mesh_contours_style()
                )
            cv2.putText(frame, "Face: Detected", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Face: Not detected", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Draw body pose landmarks
        if pose_results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                pose_results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )
            cv2.putText(frame, "Pose: Detected", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Pose: Not detected", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Show live feed
        cv2.imshow("Saksham - Agent 1 Perception", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Stopping safely...")
            break

finally:
    # This ALWAYS runs — webcam always closes cleanly
    pose_detector.close()
    face_detector.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Webcam safely released. Agent 1 stopped.")