import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from process_video import process_video
import os

st.set_page_config(page_title="Vehicle Speed Dashboard", layout="centered")
st.title("Vehicle Speed & Count Dashboard")

# Thư mục dữ liệu
upload_dir = Path("data/uploads")
output_dir = Path("data/outputs")
log_dir = Path("data/logs")

upload_dir.mkdir(parents=True, exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)
log_dir.mkdir(parents=True, exist_ok=True)

uploaded_file = st.file_uploader("Upload video (.mp4 hoặc .avi)", type=["mp4", "avi"])

# Sử dụng session state để lưu trạng thái
if "video_processed" not in st.session_state:
    st.session_state["video_processed"] = False
if "output_path" not in st.session_state:
    st.session_state["output_path"] = ""
if "log_path" not in st.session_state:
    st.session_state["log_path"] = ""

if uploaded_file:
    input_path = upload_dir / uploaded_file.name
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Đã upload: {uploaded_file.name}")

    output_path = output_dir / f"annotated_{uploaded_file.name}"
    log_path = log_dir / f"log_{uploaded_file.name.replace('.mp4', '.csv')}"

    # Chỉ xử lý nếu chưa xử lý hoặc file chưa tồn tại
    if not st.session_state["video_processed"] or not output_path.exists() or not log_path.exists():
        with st.spinner("Đang xử lý video..."):
            process_video(str(input_path), str(output_path), str(log_path))
        st.session_state["video_processed"] = True
        st.session_state["output_path"] = str(output_path)
        st.session_state["log_path"] = str(log_path)
        st.success("Hoàn tất xử lý video!")
    else:
        st.success("Video đã được xử lý trước đó.")

    # Hiển thị video kết quả (chỉ khi file > 0 bytes)
    # Hiển thị video kết quả
    if output_path.exists() and os.path.getsize(output_path) > 0:
        st.subheader("Kết quả video")
        with open(output_path, "rb") as video_file:
            video_bytes = video_file.read()
        st.video(video_bytes)

    # Load log và biểu đồ
    if log_path.exists():
        df = pd.read_csv(log_path)

        # Số lượng xe theo thời gian (giây)
        count_by_sec = df.groupby("timestamp")["object_id"].nunique()

        st.subheader("Số lượng xe theo thời gian")
        fig, ax = plt.subplots()
        count_by_sec.plot(ax=ax)
        ax.set_xlabel("Thời gian (giây)")
        ax.set_ylabel("Số lượng xe")
        st.pyplot(fig)

        # Nút tải file log (không gây reload lại)
        st.download_button(
            "Tải file log CSV",
            df.to_csv(index=False),
            file_name=log_path.name,
            mime="text/csv"
        )