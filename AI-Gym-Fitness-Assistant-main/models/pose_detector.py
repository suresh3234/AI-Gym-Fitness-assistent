"""
models/pose_detector.py – AI Gym Trainer using MediaPipe Pose.

Detects body landmarks, counts repetitions for common exercises,
and flags posture issues in real time.
"""
import math
import cv2
import mediapipe as mp


class PoseDetector:
    """Wraps MediaPipe Pose to provide angle computation and rep counting."""

    def __init__(self, min_detection_confidence: float = 0.6,
                 min_tracking_confidence: float = 0.6):
        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        # Rep counting state
        self.rep_count: int = 0
        self.stage: str = "up"   # "up" | "down"
        self.feedback: str = "Get in position"

    # ------------------------------------------------------------------
    # Core processing
    # ------------------------------------------------------------------

    def process_frame(self, frame):
        """
        Run pose estimation on *frame* (BGR numpy array).
        Returns (annotated_frame, landmarks_or_None).
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb)
        if result.pose_landmarks:
            self.mp_draw.draw_landmarks(
                frame, result.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2),
            )
        return frame, result.pose_landmarks

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_angle(a, b, c) -> float:
        """
        Return the angle (degrees) at joint *b* formed by points *a*-*b*-*c*.
        Each point is a landmark with .x, .y attributes (normalised 0-1).
        """
        ax, ay = a.x, a.y
        bx, by = b.x, b.y
        cx, cy = c.x, c.y

        radians = math.atan2(cy - by, cx - bx) - math.atan2(ay - by, ax - bx)
        angle = abs(math.degrees(radians))
        if angle > 180:
            angle = 360 - angle
        return round(angle, 1)

    # ------------------------------------------------------------------
    # Exercise analysers
    # ------------------------------------------------------------------

    def analyse_bicep_curl(self, landmarks) -> dict:
        """Detect bicep-curl reps and posture feedback."""
        lm = landmarks.landmark
        mp_lm = self.mp_pose.PoseLandmark

        # Use right arm
        shoulder = lm[mp_lm.RIGHT_SHOULDER.value]
        elbow = lm[mp_lm.RIGHT_ELBOW.value]
        wrist = lm[mp_lm.RIGHT_WRIST.value]

        angle = self.get_angle(shoulder, elbow, wrist)

        # Rep counting
        if angle > 160:
            self.stage = "down"
        if angle < 40 and self.stage == "down":
            self.stage = "up"
            self.rep_count += 1

        # Posture feedback
        if 40 <= angle <= 160:
            self.feedback = "Good form – keep going!"
        elif angle > 160:
            self.feedback = "Fully extend your arm"
        else:
            self.feedback = "Curl all the way up!"

        return {
            "exercise": "Bicep Curl",
            "angle": angle,
            "reps": self.rep_count,
            "stage": self.stage,
            "feedback": self.feedback,
        }

    def analyse_squat(self, landmarks) -> dict:
        """Detect squat reps and posture feedback."""
        lm = landmarks.landmark
        mp_lm = self.mp_pose.PoseLandmark

        hip = lm[mp_lm.RIGHT_HIP.value]
        knee = lm[mp_lm.RIGHT_KNEE.value]
        ankle = lm[mp_lm.RIGHT_ANKLE.value]

        angle = self.get_angle(hip, knee, ankle)

        if angle > 170:
            self.stage = "up"
        if angle < 100 and self.stage == "up":
            self.stage = "down"
            self.rep_count += 1

        if angle < 80:
            self.feedback = "Too deep – watch your knees!"
        elif 80 <= angle <= 170:
            self.feedback = "Good squat depth!"
        else:
            self.feedback = "Lower into the squat"

        return {
            "exercise": "Squat",
            "angle": angle,
            "reps": self.rep_count,
            "stage": self.stage,
            "feedback": self.feedback,
        }

    def analyse_pushup(self, landmarks) -> dict:
        """Detect push-up reps and posture feedback."""
        lm = landmarks.landmark
        mp_lm = self.mp_pose.PoseLandmark

        shoulder = lm[mp_lm.RIGHT_SHOULDER.value]
        elbow = lm[mp_lm.RIGHT_ELBOW.value]
        wrist = lm[mp_lm.RIGHT_WRIST.value]

        angle = self.get_angle(shoulder, elbow, wrist)

        if angle > 160:
            self.stage = "up"
        if angle < 80 and self.stage == "up":
            self.stage = "down"
            self.rep_count += 1

        if angle < 60:
            self.feedback = "Great depth!"
        elif angle < 160:
            self.feedback = "Keep your body straight"
        else:
            self.feedback = "Lower your chest"

        return {
            "exercise": "Push-up",
            "angle": angle,
            "reps": self.rep_count,
            "stage": self.stage,
            "feedback": self.feedback,
        }

    def reset(self):
        """Reset rep counter and stage for a new set."""
        self.rep_count = 0
        self.stage = "up"
        self.feedback = "Get in position"

    def analyse(self, exercise: str, landmarks) -> dict:
        """Dispatch to the appropriate exercise analyser."""
        dispatch = {
            "Bicep Curl": self.analyse_bicep_curl,
            "Squat": self.analyse_squat,
            "Push-up": self.analyse_pushup,
        }
        fn = dispatch.get(exercise, self.analyse_bicep_curl)
        return fn(landmarks)
