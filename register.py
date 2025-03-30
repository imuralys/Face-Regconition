import cv2
import face_recognition
import streamlit as st
import pickle
import numpy as np
from connect import get_db_connection, hash_password

# 🔹 Khởi tạo trạng thái nếu chưa có
if "captured_image" not in st.session_state:
    st.session_state.captured_image = None
if "camera_active" not in st.session_state:
    st.session_state.camera_active = False

def save_encoding(name, password, encoding):
    """Lưu thông tin khuôn mặt vào SQL Server."""
    try:
        hashed_pw = hash_password(password)  # Băm mật khẩu trước khi lưu
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, password, encoding) VALUES (?, ?, ?)",
                       (name, hashed_pw, pickle.dumps(encoding)))  # Chuyển encoding thành nhị phân
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu dữ liệu: {e}")
        return False

def register_face():
    """Giao diện đăng ký khuôn mặt."""
    st.title("🔐 Đăng ký khuôn mặt")

    # 🟢 Nhập thông tin trước khi bật camera
    col1, col2 = st.columns([2, 3])
    with col1:
        name = st.text_input("👤 Nhập tên:")
        password = st.text_input("🔑 Nhập mật khẩu:", type="password")

    # 🟢 Khi nhấn "Bật camera", mở camera
    if st.button("📷 Bật camera", key="open_cam"):
        st.session_state.camera_active = True
        st.session_state.captured_image = None  # Reset ảnh cũ

    # 🟢 Nếu camera đang bật
    if st.session_state.camera_active:
        cap = cv2.VideoCapture(0)
        frame_holder = st.empty()  # Dùng để hiển thị video

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.error("❌ Không thể lấy hình ảnh từ camera.")
                break

            # Nhận diện khuôn mặt
            face_locations = face_recognition.face_locations(frame)
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Hiển thị video camera
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_holder.image(frame, channels="RGB")

            # 🔹 Nếu bấm "Chụp ảnh" thì lưu ảnh và tắt camera
            if st.button("📸 Chụp ảnh", key="capture_btn"):
                st.session_state.captured_image = frame.copy()
                st.session_state.camera_active = False  # Tắt camera
                cap.release()
                break

    # 🟢 Nếu đã chụp ảnh, hiển thị ảnh
    if st.session_state.captured_image is not None:
        st.image(st.session_state.captured_image, caption="📷 Ảnh đã chụp", channels="RGB")

        # 🟢 Kiểm tra nhập đủ tên & mật khẩu trước khi đăng ký
        if name and password:
            if st.button("✅ Xác nhận & Đăng ký", key="confirm_btn"):
                face_locations = face_recognition.face_locations(st.session_state.captured_image)
                encoding = face_recognition.face_encodings(st.session_state.captured_image, face_locations)

                if len(encoding) == 1:
                    if save_encoding(name, password, encoding[0]):
                        st.success("✅ Đăng ký thành công!")
                        st.session_state.captured_image = None  # Reset sau khi đăng ký
                        st.session_state.camera_active = False
                else:
                    st.error("❌ Không tìm thấy khuôn mặt hoặc có nhiều hơn một khuôn mặt.")
        else:
            st.warning("⚠️ Vui lòng nhập **tên** và **mật khẩu** trước khi đăng ký.")
