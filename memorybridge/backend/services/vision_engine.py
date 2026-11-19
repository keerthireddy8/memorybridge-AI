import cv2
import time
import numpy as np
from datetime import datetime

class VisionEngine:
    def __init__(self):
        self.camera = None
        self.is_camera_open = False
        self.privacy_mode_active = False
        self.active_detected_object = "Keys"
        self.confidence = 0.94
        self.active_zone = "Living Room"
        self._try_open_camera()

    def _try_open_camera(self):
        try:
            # Try default camera index 0
            self.camera = cv2.VideoCapture(0)
            if self.camera and self.camera.isOpened():
                self.is_camera_open = True
            else:
                self.is_camera_open = False
        except Exception:
            self.is_camera_open = False

    def set_privacy_mode(self, active: bool):
        self.privacy_mode_active = active

    def set_simulation_target(self, obj_name: str, zone: str, conf: float = 0.95):
        self.active_detected_object = obj_name
        self.active_zone = zone
        self.confidence = conf

    def get_frame(self):
        # If camera is open and accessible
        success = False
        frame = None
        if self.is_camera_open and self.camera:
            try:
                success, frame = self.camera.read()
            except Exception:
                success = False

        if not success or frame is None:
            # Generate synthetic realistic studio feed for hackathon
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            # Soft warm ambient background gradient
            for y in range(480):
                frame[y, :, 0] = int(24 + (y / 480) * 16)  # B
                frame[y, :, 1] = int(28 + (y / 480) * 18)  # G
                frame[y, :, 2] = int(36 + (y / 480) * 20)  # R

            # Draw virtual room grid & table
            cv2.rectangle(frame, (100, 240), (540, 440), (60, 68, 78), -1)
            cv2.rectangle(frame, (100, 240), (540, 440), (90, 105, 120), 2)
            cv2.putText(frame, "AMBIENT LIVING-ROOM SENSOR [CAMERA 01]", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 200, 220), 1, cv2.LINE_AA)

        # Check privacy firewall state
        if self.privacy_mode_active:
            # Blind/mask the camera feed completely with animated privacy shield
            mask = np.zeros_like(frame)
            mask[:] = (20, 24, 32)
            alpha = 0.92
            cv2.addWeighted(mask, alpha, frame, 1 - alpha, 0, frame)

            # Draw privacy firewall banner
            cv2.rectangle(frame, (80, 160), (560, 320), (35, 30, 95), -1)
            cv2.rectangle(frame, (80, 160), (560, 320), (70, 60, 200), 2)

            cv2.putText(frame, "PRIVACY FIREWALL ACTIVE", (110, 210),
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, "Visual tracking disabled in Private Zone.", (110, 250),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 210, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, "Only permitted non-visual boundary logs retained.", (110, 280),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 180, 220), 1, cv2.LINE_AA)
        else:
            # Draw live detection bounding box on detected item
            h, w, _ = frame.shape
            bx, by, bw, bh = 220, 250, 200, 140
            cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (70, 200, 90), 2)

            # Label box
            label = f"{self.active_detected_object} ({int(self.confidence * 100)}%)"
            cv2.rectangle(frame, (bx, by - 30), (bx + bw, by), (70, 200, 90), -1)
            cv2.putText(frame, label, (bx + 8, by - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 20, 10), 2, cv2.LINE_AA)

            # Status pill in corner
            now_str = datetime.now().strftime("%H:%M:%S")
            status_text = f"LIVE | Zone: {self.active_zone} | {now_str}"
            cv2.putText(frame, status_text, (30, h - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 220, 140), 1, cv2.LINE_AA)

        # Encode to JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            return None
        return jpeg.tobytes()

    def generate_mjpeg_stream(self):
        while True:
            frame_bytes = self.get_frame()
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.06)  # ~15-18 FPS

vision_service = VisionEngine()
