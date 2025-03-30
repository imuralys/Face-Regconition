import streamlit as st
from connect import init_db
from register import register_face
from identify import identify_face

# Khởi tạo trạng thái ban đầu
if "page" not in st.session_state:
    st.session_state.page = "home"

def set_page(page):
    st.session_state.page = page

def main():
    st.title("💻 Hệ thống nhận diện khuôn mặt")

    # Khởi tạo database
    init_db()

    if st.session_state.page == "home":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Đăng ký khuôn mặt"):
                set_page("register")
        with col2:
            if st.button("🔍 Nhận diện khuôn mặt"):
                set_page("identify")

    elif st.session_state.page == "register":
        register_face()
        if st.button("⬅ Quay lại"):
            set_page("home")

    elif st.session_state.page == "identify":
        identify_face()
        if st.button("⬅ Quay lại"):
            set_page("home")

if __name__ == "__main__":
    main()
