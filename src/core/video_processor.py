import logging

import cv2

logger = logging.getLogger(__name__)

class VideoProcessor:

    def __init__(self, detector):
        self.detector = detector
        self.log_callback = None

    def set_log_callback(self, callback):
        self.log_callback = callback

    def _log(self, message, level="INFO"):
        if self.log_callback:
            self.log_callback(message, level)

    def process_video(self, input_path, output_path, progress_callback=None):
        cap = cv2.VideoCapture(input_path)

        if not cap.isOpened():
            self._log(f"Cannot open video: {input_path}", "ERROR")
            return False

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        if not out.isOpened():
            self._log(f"Cannot create output video: {output_path}", "ERROR")
            cap.release()
            return False

        self._log(f"Processing video: {width}x{height} @ {fps}fps, {total_frames} frames", "INFO")

        frame_count = 0
        detection_count = 0

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                annotated_frame, detections = self.detector.detect(frame)
                out.write(annotated_frame)

                frame_count += 1
                detection_count += len(detections)

                if progress_callback and frame_count % 10 == 0:
                    progress = int((frame_count / total_frames) * 100)
                    progress_callback(progress)

                if frame_count % 100 == 0:
                    self._log(f"Processed {frame_count}/{total_frames} frames, {detection_count} detections", "INFO")

            self._log(f"Successfully processed {frame_count} frames with {detection_count} total detections", "SUCCESS")
            return True

        except Exception as e:
            self._log(f"Error during video processing: {e}", "ERROR")
            return False

        finally:
            cap.release()
            out.release()
