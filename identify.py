import cv2
import face_recognition
import streamlit as st
import numpy as np
import pickle
from connect import get_db_connection

def load_encodings():
    """Tải dữ liệu khuôn mặt từ database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, encoding FROM users")
    users = cursor.fetchall()
    conn.close()
    return [(name, pickle.loads(enc)) for name, enc in users]

def identify_face():
    """Giao diện nhận diện khuôn mặt."""
    st.title("🔍 Nhận diện khuôn mặt")
    known_encodings = load_encodings()
    
    if not known_encodings:
        st.error("❌ Chưa có dữ liệu khuôn mặt trong hệ thống.")
        return
    
    cap = cv2.VideoCapture(0)  # Mở camera
    frame_holder = st.empty()  # Vùng hiển thị ảnh
    result_holder = st.empty()  # Vùng hiển thị kết quả
    detected_name = "Không nhận diện được"
    
    exit_button = st.button("❌ Thoát", key="exit_button")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("❌ Không thể lấy hình ảnh từ camera.")
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        new_detected_name = "Không nhận diện được"
        for face_encoding in face_encodings:
            distances = [np.linalg.norm(face_encoding - enc) for _, enc in known_encodings]
            min_distance = min(distances) if distances else 1.0
            if min_distance < 0.6:
                new_detected_name = known_encodings[distances.index(min_distance)][0]
                break
        
        # Chỉ cập nhật kết quả nếu có sự thay đổi
        if new_detected_name != detected_name:
            detected_name = new_detected_name
            result_holder.subheader(f"🆔 Kết quả: {detected_name}")
        
        # Vẽ khung nhận diện
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        frame_holder.image(frame, channels="BGR")
        
        if exit_button:
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    identify_face()
