import streamlit as st
import subprocess

def main():
    st.title("Nhận diện khuôn mặt")
    
    st.write("Chọn một thao tác:")
    
    if st.button("📷 Đăng ký khuôn mặt"):
        st.write("🔄 Đang mở camera để đăng ký...")
        subprocess.run(["python", "register.py"])
        st.success("✅ Đăng ký khuôn mặt thành công!")
    
    if st.button("🔍 Nhận diện khuôn mặt"):
        st.write("🔄 Đang mở camera để nhận diện...")
        subprocess.run(["python", "identify.py"])
        st.success("✅ Quá trình nhận diện hoàn tất!")

if __name__ == "__main__":
    main()
