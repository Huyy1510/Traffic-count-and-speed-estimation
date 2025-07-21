import cv2
import pandas as pd
import os
from ultralytics import YOLO
from ultralytics.solutions import SpeedEstimator
from bytetrack_config import ByteTrackArgument
import sys
from speed_estimator_args import SpeedEstimatorArgument as SEA
import numpy as np
sys.path.append(os.path.abspath("ByteTrack"))
from yolox.tracker.byte_tracker import BYTETracker  






def process_video(input_path, output_path, log_path, model_path="yolov8n.pt"):
    # 1. Load mô hình
    model = YOLO(model_path)
    speed_estimator = SpeedEstimator(
        region=SEA.region,
        meter_per_pixel=SEA.meter_per_pixel,
        fps=SEA.fps,
        max_hist=SEA.max_hist,
        max_speed=SEA.max_speed
    )
    np.float = float  # Fix cho các thư viện cũ dùng np.float
    tracker = BYTETracker(ByteTrackArgument)

    # 2. Đọc video
    cap = cv2.VideoCapture(input_path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


    # Đảm bảo dùng H.264 cho output mp4
    if output_path.endswith('.mp4'):
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  #streamlit run app.py H.264
    else:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    frame_id = 0
    logs = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_id += 1
        time_sec = round(frame_id / fps, 2)

        # 3. Detect + Bytetrack
        results = model.track(frame, persist=True, tracker='bytetrack.yaml', classes=[2, 3, 5, 7])

        if results[0].boxes.id is not None:
            speed_result = speed_estimator.process(frame)
            annotated_frame = speed_result.plot_im
            for box_data in results[0].boxes.data:
                # Đảm bảo box_data có đủ phần tử trước khi truy cập
                if len(box_data) < 7:  # Cần ít nhất 7 phần tử: x1, y1, x2, y2, conf, cls, track_id
                    continue  # Bỏ qua nếu dữ liệu không đủ

                x1, y1, x2, y2 = box_data[0:4].cpu().numpy().astype(int)  # Bounding box
                track_id = int(box_data[6].cpu().item())  # Track ID

                # Lấy tốc độ từ speed_estimator.spd (dict trong SpeedEstimator lưu trữ tốc độ)
                speed_kmph = speed_estimator.spd.get(track_id, 0.0)

                # Thêm dữ liệu vào danh sách logs
                logs.append({
                    "frame_id": frame_id,
                    "timestamp": time_sec,
                    "object_id": track_id,
                    "speed_kmph": speed_kmph,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                })
        else:
            annotated_frame = frame.copy()

        vehicle_count = 0
        if results[0].boxes.id is not None:
            vehicle_count = results[0].boxes.id.shape[0]

        # Overlay số lượng xe
        cv2.putText(annotated_frame, f"Vehicles: {vehicle_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        writer.write(annotated_frame)

    cap.release()
    writer.release()

    # 6. Ghi log ra CSV
    df = pd.DataFrame(logs)
    df.to_csv(log_path, index=False)