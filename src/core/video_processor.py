import logging
import cv2
from collections import deque, defaultdict
from threading import Thread
from queue import Queue, Empty
import time

logger = logging.getLogger(__name__)


class VideoProcessor:

    def __init__(self, detector):
        self.detector = detector
        self.log_callback = None
        self.detection_history = deque(maxlen=15)
        self.current_speed = None
        self.speed_confidence = 0
        self.frames_since_detection = 0
        self.detection_regions = {}

    def set_log_callback(self, callback):
        self.log_callback = callback

    def _log(self, message, level="INFO"):
        if self.log_callback:
            self.log_callback(message, level)

    def _calculate_iou(self, box1, box2):
        """Calculate IoU between two bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2

        xi1 = max(x1_1, x1_2)
        yi1 = max(y1_1, y1_2)
        xi2 = min(x2_1, x2_2)
        yi2 = min(y2_1, y2_2)

        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

        box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)

        union_area = box1_area + box2_area - inter_area

        return inter_area / union_area if union_area > 0 else 0

    def _temporal_nms(self, current_detections):
        """Improved temporal smoothing - prioritizes HIGHEST confidence"""
        if not current_detections:
            self.frames_since_detection += 1

            if self.frames_since_detection < 20 and self.current_speed:
                return []
            else:
                self.current_speed = None
                return []

        self.detection_history.append(current_detections)

        if len(self.detection_history) < 3:
            return current_detections

        speed_data = defaultdict(lambda: {
            'count': 0,
            'total_conf': 0,
            'max_conf': 0,
            'positions': [],
            'avg_conf': 0
        })

        for i, frame_dets in enumerate(self.detection_history):
            weight = (i + 1) / len(self.detection_history)

            for det in frame_dets:
                speed = det.get('speed_limit') or det.get('class_name')
                conf = det.get('confidence', 0)
                bbox = det.get('bbox')

                if speed and speed != 'speed-sign-end':
                    speed_data[speed]['count'] += weight
                    speed_data[speed]['total_conf'] += conf * weight
                    speed_data[speed]['max_conf'] = max(speed_data[speed]['max_conf'], conf)
                    speed_data[speed]['positions'].append(bbox)

        if not speed_data:
            return current_detections

        for speed in speed_data:
            if speed_data[speed]['count'] > 0:
                speed_data[speed]['avg_conf'] = speed_data[speed]['total_conf'] / speed_data[speed]['count']

        best_speed = max(speed_data, key=lambda s: (
            speed_data[s]['max_conf'] * 1.5,
            speed_data[s]['count'],
            speed_data[s]['avg_conf']
        ))

        if speed_data[best_speed]['count'] >= 2 or speed_data[best_speed]['max_conf'] > 0.85:
            self.current_speed = best_speed
            self.speed_confidence = speed_data[best_speed]['max_conf']
            self.frames_since_detection = 0

            filtered = [d for d in current_detections
                        if (d.get('speed_limit') == best_speed or
                            d.get('class_name') == best_speed)]

            return filtered if filtered else current_detections

        return current_detections

    def _draw_detection(self, frame, detection):
        """Draw bounding box with thicker lines for visibility"""
        x1, y1, x2, y2 = detection['bbox']
        conf = detection['confidence']
        speed = detection.get('speed_limit') or detection.get('class_name', 'unknown')

        if conf >= 0.8:
            color = (0, 255, 0)
        elif conf >= 0.6:
            color = (0, 165, 255)
        else:
            color = (0, 100, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 5)

        label = f"{speed} ({conf:.2f})"

        font_scale = 0.9
        thickness = 2
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)

        cv2.rectangle(frame, (x1, y1 - h - 12), (x1 + w + 8, y1), color, -1)
        cv2.putText(frame, label, (x1 + 4, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

        return frame

    def _draw_stable_detection(self, frame):
        """Draw persistent detection indicator - ALWAYS shows HIGHEST confidence sign"""
        if self.current_speed and self.frames_since_detection < 20:
            h, w = frame.shape[:2]
            box_w, box_h = 240, 100
            x1, y1 = w - box_w - 20, 20
            x2, y2 = w - 20, 20 + box_h

            if self.speed_confidence >= 0.8:
                color = (0, 255, 0)
            elif self.speed_confidence >= 0.6:
                color = (0, 165, 255)
            else:
                color = (0, 100, 255)

            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 4)

            label = f"{self.current_speed}"
            font_scale = 1.5
            thickness = 3
            (w_text, h_text), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)

            text_x = x1 + (box_w - w_text) // 2
            text_y = y1 + (box_h + h_text) // 2 - 10

            cv2.putText(frame, label, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

            conf_text = f"MAX conf: {self.speed_confidence:.2f}"
            cv2.putText(frame, conf_text, (x1 + 12, y2 - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        return frame

    def _frame_reader_thread(self, cap, frame_queue, stop_flag, skip_frames):
        frame_count = 0
        while not stop_flag['stop']:
            ret, frame = cap.read()
            if not ret:
                stop_flag['stop'] = True
                break

            should_process = (frame_count % skip_frames == 0)
            frame_queue.put((frame_count, frame, should_process))
            frame_count += 1

    def _detection_thread(self, frame_queue, detection_queue, stop_flag, batch_size=8):
        frame_batch = []
        frame_indices = []
        should_process_flags = []

        while not stop_flag['stop']:
            try:
                frame_count, frame, should_process = frame_queue.get(timeout=0.1)

                frame_batch.append(frame)
                frame_indices.append(frame_count)
                should_process_flags.append(should_process)

                if len(frame_batch) >= batch_size or (stop_flag['stop'] and frame_batch):
                    frames_to_process = []
                    process_map = {}

                    for i, (idx, frm, should_proc) in enumerate(zip(frame_indices, frame_batch, should_process_flags)):
                        if should_proc:
                            frames_to_process.append(frm)
                            process_map[len(frames_to_process) - 1] = i

                    if frames_to_process:
                        batch_detections = self.detector.detect_batch(
                            frames_to_process,
                            multi_scale=True,
                            enhance=True,
                            conf_override=0.4
                        )

                        for batch_idx, detections in enumerate(batch_detections):
                            original_idx = process_map[batch_idx]
                            smoothed = self._temporal_nms(detections)
                            detection_queue.put((
                                frame_indices[original_idx],
                                frame_batch[original_idx],
                                smoothed,
                                True
                            ))
                    else:
                        for idx, frm in zip(frame_indices, frame_batch):
                            self.frames_since_detection += 1
                            detection_queue.put((idx, frm, [], False))

                    frame_batch.clear()
                    frame_indices.clear()
                    should_process_flags.clear()

            except Empty:
                if frame_batch and stop_flag['stop']:
                    for idx, frm, should_proc in zip(frame_indices, frame_batch, should_process_flags):
                        detection_queue.put((idx, frm, [], should_proc))
                    frame_batch.clear()
                    frame_indices.clear()
                    should_process_flags.clear()
                continue

    def _rendering_thread(self, detection_queue, out, stop_flag, total_frames, progress_callback):
        frame_count = 0
        detection_count = 0
        start_time = time.time()

        render_buffer = []
        buffer_size = 30

        while not stop_flag['stop'] or not detection_queue.empty():
            try:
                frame_idx, frame, detections, was_processed = detection_queue.get(timeout=1)

                annotated_frame = frame.copy()

                if was_processed and detections:
                    for det in detections:
                        annotated_frame = self._draw_detection(annotated_frame, det)
                    detection_count += len(detections)

                annotated_frame = self._draw_stable_detection(annotated_frame)

                render_buffer.append(annotated_frame)

                if len(render_buffer) >= buffer_size:
                    for buffered_frame in render_buffer:
                        out.write(buffered_frame)
                        frame_count += 1
                    render_buffer.clear()

                if progress_callback and frame_count % 10 == 0:
                    progress = int((frame_count / total_frames) * 100)
                    progress_callback(progress)

                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps_current = frame_count / elapsed if elapsed > 0 else 0
                    self._log(f"Processed {frame_count}/{total_frames} frames "
                              f"({fps_current:.1f} FPS), {detection_count} detections", "INFO")

            except Empty:
                continue

        for buffered_frame in render_buffer:
            out.write(buffered_frame)
            frame_count += 1

    def process_video_threaded(self, input_path, output_path, progress_callback=None, skip_frames=2, batch_size=6):
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

        self._log(f"Processing video (ENHANCED): {width}x{height} @ {fps}fps, {total_frames} frames", "INFO")
        self._log(f"Frame skip: {skip_frames} | Batch size: {batch_size} | Multi-scale: ON | Enhance: ON", "INFO")

        self.detection_history.clear()
        self.current_speed = None
        self.frames_since_detection = 0

        frame_queue = Queue(maxsize=batch_size * 4)
        detection_queue = Queue(maxsize=batch_size * 4)
        stop_flag = {'stop': False}

        reader_thread = Thread(target=self._frame_reader_thread,
                               args=(cap, frame_queue, stop_flag, skip_frames))
        detection_thread = Thread(target=self._detection_thread,
                                  args=(frame_queue, detection_queue, stop_flag, batch_size))
        rendering_thread = Thread(target=self._rendering_thread,
                                  args=(detection_queue, out, stop_flag, total_frames, progress_callback))

        start_time = time.time()

        try:
            reader_thread.start()
            detection_thread.start()
            rendering_thread.start()

            reader_thread.join()
            detection_thread.join()
            rendering_thread.join()

            elapsed = time.time() - start_time
            fps_avg = total_frames / elapsed if elapsed > 0 else 0

            self._log(f"Successfully processed {total_frames} frames in {elapsed:.1f}s "
                      f"(avg {fps_avg:.1f} FPS)", "SUCCESS")
            return True

        except Exception as e:
            self._log(f"Error during video processing: {e}", "ERROR")
            stop_flag['stop'] = True
            return False

        finally:
            cap.release()
            out.release()

    def process_video(self, input_path, output_path, progress_callback=None, skip_frames=2, batch_size=6,
                      use_threading=True):
        if use_threading:
            return self.process_video_threaded(input_path, output_path, progress_callback, skip_frames, batch_size)
        else:
            return self.process_video_single(input_path, output_path, progress_callback, skip_frames)

    def process_video_single(self, input_path, output_path, progress_callback=None, skip_frames=2):
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
        self.detection_history.clear()
        self.current_speed = None
        self.frames_since_detection = 0

        start_time = time.time()

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                should_detect = (frame_count % skip_frames == 0)

                if should_detect:
                    _, raw_detections = self.detector.detect(frame, conf_override=0.4, multi_scale=True, enhance=True)
                    smoothed_detections = self._temporal_nms(raw_detections)

                    annotated_frame = frame.copy()
                    for det in smoothed_detections:
                        annotated_frame = self._draw_detection(annotated_frame, det)

                    detection_count += len(smoothed_detections)
                else:
                    annotated_frame = frame.copy()
                    annotated_frame = self._draw_stable_detection(annotated_frame)
                    self.frames_since_detection += 1

                out.write(annotated_frame)
                frame_count += 1

                if progress_callback and frame_count % 10 == 0:
                    progress = int((frame_count / total_frames) * 100)
                    progress_callback(progress)

                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps_current = frame_count / elapsed if elapsed > 0 else 0
                    self._log(f"Processed {frame_count}/{total_frames} frames "
                              f"({fps_current:.1f} FPS), {detection_count} detections", "INFO")

            elapsed = time.time() - start_time
            fps_avg = frame_count / elapsed if elapsed > 0 else 0

            self._log(f"Successfully processed {frame_count} frames in {elapsed:.1f}s "
                      f"(avg {fps_avg:.1f} FPS)", "SUCCESS")
            return True

        except Exception as e:
            self._log(f"Error during video processing: {e}", "ERROR")
            return False

        finally:
            cap.release()
            out.release()
