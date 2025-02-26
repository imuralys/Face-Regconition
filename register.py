import cv2
import face_recognition
import numpy as np
import os

ENCODING_FILE = "data/encodings.npy"

def capture_and_save_face():
    """Mở webcam, trích xuất face_encodings và lưu vào file (không lưu ảnh)."""
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Không thể mở camera!")
        return

    print("📸 Nhấn 's' để trích xuất face_encodings. Nhấn 'q' để thoát.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Không thể lấy dữ liệu từ camera.")
            break

        cv2.imshow("Capture Face", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):  # Nhấn 's' để trích xuất face_encodings
            # Chuyển đổi sang RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Trích xuất face_encodings từ webcam
            face_encodings = face_recognition.face_encodings(rgb_frame)

            if face_encodings:
                encoding = face_encodings[0]  # Chỉ lấy khuôn mặt đầu tiên

                # Lưu encoding vào file NumPy
                save_encodings(encoding)
            else:
                print("❌ Không tìm thấy khuôn mặt!")

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def save_encodings(encoding):
    """Lưu face_encodings vào file NumPy (không cần lưu đường dẫn ảnh)."""
    data = load_encodings()
    data.append(encoding)  # Chỉ lưu encoding, không lưu đường dẫn ảnh
    np.save(ENCODING_FILE, data)
    print("✅ Face encoding đã lưu thành công!")

def load_encodings():
    """Tải danh sách face_encodings từ file NumPy."""
    if os.path.exists(ENCODING_FILE):
        return list(np.load(ENCODING_FILE, allow_pickle=True))
    return []

# 🚀 Gọi hàm chụp ảnh và lưu face_encodings (KHÔNG lưu ảnh)
capture_and_save_face()
