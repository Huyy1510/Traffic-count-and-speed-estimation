# speed_estimator_args.py

class SpeedEstimatorArgument:
    """
    Lớp cấu hình tham số cho SpeedEstimator của Ultralytics.
    Dùng để truyền vào constructor của ultralytics.solutions.SpeedEstimator.
    """
    @staticmethod
    def get_center_region(frame_width: int, frame_height: int, line_length_ratio: float = 0.8):
        """
        Tạo một đường region nằm giữa khung hình (ngang), mặc định dài 80% chiều rộng.

        Args:
            frame_width (int): Chiều rộng frame
            frame_height (int): Chiều cao frame
            line_length_ratio (float): Tỉ lệ chiều dài của đường trên tổng chiều rộng

        Returns:
            list: reg_pts [(x1, y), (x2, y)]
        """
        y = frame_height // 2  # đường nằm giữa chiều cao
        line_half = int((frame_width * line_length_ratio) / 2)
        center_x = frame_width // 2

        return [(center_x - line_half, y), (center_x + line_half, y)]
    
    # Vùng tính toán tốc độ: 2 điểm (đường) hoặc 4 điểm (vùng)
    region = [(100, 400), (1200, 400)]  # hoặc ví dụ: [(100, 400), (1200, 400), (1200, 420), (100, 420)]

    # Tên các class cần tính tốc độ. Nếu None → tất cả.
    #dạng số nha, này sửa sau
    classes = ['car', 'bus', 'truck', 'motorbike'] #để tạm, sau đó sẽ chỉnh sau theo model custom T_T

    # Có hiển thị khung hình và overlay không
    view_img = True

    # Khoảng cách thực tế mỗi pixel (mét / pixel)
    meter_per_pixel = 0.05  # tức là 1 pixel ~ 5 cm

    # Tốc độ khung hình của video (fps) → bắt buộc phải đúng để tính tốc độ
    fps = 30.0

    # Số lượng frame tối thiểu để tính tốc độ (nếu object chưa đi qua đủ → chưa tính)
    max_hist = 5

    # Tốc độ tối đa được hiển thị (km/h). Nếu tính > giá trị này sẽ bị giới hạn.
    max_speed = 180

    # Màu vẽ khung vật thể (BGR)
    box_color = (0, 255, 0)  # xanh lá cây

    # Màu vẽ chữ tốc độ (BGR)
    text_color = (255, 255, 255)  # trắng

    # Font chữ
    font = 0  # cv2.FONT_HERSHEY_SIMPLEX

    # Font size
    font_scale = 0.6

    # Độ dày đường viền khung
    thickness = 2

    # Vẽ region hay không
    show_region = True
