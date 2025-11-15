import cv2
import logging
from pathlib import Path
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class VideoProcessor:

    def __init__(self, detector):
        self.detector = detector

    def process_video(
            self,
            input_path: str,
            output_path: str,
            progress_callback: Optional[Callable[[int], None]] = None
    ) -> bool:

        cap = cv2.VideoCapture(input_path)

        if not cap.isOpened():
            logger.error(f"Cannot open video: {input_path}")
            return False

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        if not out.isOpened():
            logger.error(f"Cannot create output video: {output_path}")
            cap.release()
            return False

        logger.info(f"Processing video: {width}x{height} @ {fps}fps, {total_frames} frames")

        frame_count = 0

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                annotated_frame, detections = self.detector.detect(frame)
                out.write(annotated_frame)

                frame_count += 1

                if progress_callback and frame_count % 10 == 0:
                    progress = int((frame_count / total_frames) * 100)
                    progress_callback(progress)

            logger.info(f"Successfully processed {frame_count} frames")
            return True

        except Exception as e:
            logger.error(f"Error during video processing: {e}")
            return False

        finally:
            cap.release()
            out.release()
