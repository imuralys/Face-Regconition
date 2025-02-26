import numpy as np
import face_recognition
import cv2
import os

ENCODING_FILE = "data/encodings.npy"

def load_encodings():
    """Tải danh sách face_encodings từ file NumPy."""
    try:
        return list(np.load(ENCODING_FILE, allow_pickle=True))
    except FileNotFoundError:
        print("❌ Không tìm thấy file encodings.npy!")
        return []

encodings_data = load_encodings()
print(f"🔍 Đã tải {len(encodings_data)} khuôn mặt.")

def recognize_face_in_camera(encodings_data):
    """Mở webcam và nhận diện khuôn mặt có trùng với dữ liệu đã lưu không."""
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Không thể mở camera!")
        return

    print("🔍 Đang nhận diện khuôn mặt... Nhấn 'q' để thoát.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Không thể lấy dữ liệu từ camera.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"

            for stored_encoding in encodings_data:
                match = face_recognition.compare_faces([stored_encoding], face_encoding)[0]

                if match:
                    name = "Matched!"
                    break  # Dừng kiểm tra nếu tìm thấy khớp

            # Vẽ hình chữ nhật quanh khuôn mặt
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Chạy nhận diện khuôn mặt từ webcam
recognize_face_in_camera(encodings_data)
