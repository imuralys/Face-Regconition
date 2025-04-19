import cv2
import face_recognition
import numpy as np
import os
import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import threading
import shutil

# ==== Face Recognition System ====
class FaceRecognitionSystem:
    def __init__(self, known_faces_dir="known_faces"):
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_faces_dir = known_faces_dir
        os.makedirs(self.known_faces_dir, exist_ok=True)
        self.load_known_faces()

    def load_known_faces(self):
        self.known_face_encodings = []
        self.known_face_names = []
        for name in os.listdir(self.known_faces_dir):
            person_dir = os.path.join(self.known_faces_dir, name)
            if os.path.isdir(person_dir):
                for file in os.listdir(person_dir):
                    path = os.path.join(person_dir, file)
                    image = face_recognition.load_image_file(path)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        self.known_face_encodings.append(encodings[0])
                        self.known_face_names.append(name)
        print(f"Đã tải {len(self.known_face_names)} gương mặt.")

    def add_new_face(self, image_path, name):
        img = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(img)
        if not face_locations:
            print("Không tìm thấy khuôn mặt trong ảnh.")
            return False
        encoding = face_recognition.face_encodings(img, face_locations)[0]
        save_path = os.path.join(self.known_faces_dir, name)
        os.makedirs(save_path, exist_ok=True)
        count = len(os.listdir(save_path))
        filename = os.path.join(save_path, f"{count+1}.jpg")
        image_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(filename, image_bgr)
        self.load_known_faces()
        return True

    def add_face_from_webcam(self, name):
        cap = cv2.VideoCapture(0)
        print("Nhấn 's' để chụp ảnh, 'q' để thoát.")
        while True:
            ret, frame = cap.read()
            cv2.imshow("Thêm từ webcam", frame)
            key = cv2.waitKey(1)
            if key == ord('s'):
                save_path = os.path.join(self.known_faces_dir, name)
                os.makedirs(save_path, exist_ok=True)
                count = len(os.listdir(save_path))
                filename = os.path.join(save_path, f"{count+1}.jpg")
                cv2.imwrite(filename, frame)
                print(f"Đã lưu: {filename}")
                break
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        self.load_known_faces()

    def add_face_from_webcam_multiple(self, name, num_samples=5):
        cap = cv2.VideoCapture(0)
        save_path = os.path.join(self.known_faces_dir, name)
        os.makedirs(save_path, exist_ok=True)
        count = 0
        while count < num_samples:
            ret, frame = cap.read()
            cv2.imshow("Thêm từ webcam (nhiều ảnh)", frame)
            key = cv2.waitKey(1)
            if key == ord('s'):
                filename = os.path.join(save_path, f"{count+1}.jpg")
                cv2.imwrite(filename, frame)
                print(f"Đã lưu: {filename}")
                count += 1
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        self.load_known_faces()

# ==== Ghi log nhận diện ====
LOG_FILE = "face_log.csv"
def log_face(name):
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([now, name])
        print(f"Đã ghi log: {now}, {name}")

# ==== GUI Tkinter ====
face_system = FaceRecognitionSystem()

def start_recognition():
    def recognize():
        video_capture = cv2.VideoCapture(0)
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                matches = face_recognition.compare_faces(face_system.known_face_encodings, face_encoding)
                name = "Không xác định"
                if face_system.known_face_encodings:
                    face_distances = face_recognition.face_distance(face_system.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        raw_name = face_system.known_face_names[best_match_index]
                        confidence = 1 - face_distances[best_match_index]
                        name = f"{raw_name} ({confidence:.2f})"
                        log_face(name)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

            cv2.imshow('Nhận diện gương mặt', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        video_capture.release()
        cv2.destroyAllWindows()
    threading.Thread(target=recognize).start()

def add_from_image():
    image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if image_path:
        name = simpledialog.askstring("Nhập tên", "Nhập tên cho gương mặt:")
        if name:
            success = face_system.add_new_face(image_path, name)
            if success:
                messagebox.showinfo("Thành công", f"Đã thêm gương mặt: {name}")
            else:
                messagebox.showwarning("Thất bại", "Không tìm thấy khuôn mặt trong ảnh.")

def add_from_webcam(single=True):
    name = simpledialog.askstring("Nhập tên", "Nhập tên cho gương mặt:")
    if name:
        if single:
            face_system.add_face_from_webcam(name)
        else:
            num_samples = simpledialog.askinteger("Số mẫu", "Nhập số ảnh muốn chụp:", initialvalue=5)
            face_system.add_face_from_webcam_multiple(name, num_samples)

def delete_face():
    popup = tk.Toplevel(root)
    popup.title("Xóa gương mặt")
    popup.geometry("300x150")
    popup.resizable(False, False)

    tk.Label(popup, text="Chọn tên gương mặt muốn xóa:").pack(pady=10)
    names = list(set(face_system.known_face_names))
    selected_name = tk.StringVar(popup)
    combo = ttk.Combobox(popup, textvariable=selected_name, values=names, state="readonly")
    combo.pack(pady=5)

    def confirm_delete():
        name = selected_name.get()
        if not name:
            messagebox.showwarning("Lỗi", "Vui lòng chọn tên.")
            return
        folder = os.path.join(face_system.known_faces_dir, name)
        if os.path.exists(folder):
            shutil.rmtree(folder)
            face_system.load_known_faces()
            messagebox.showinfo("Xóa thành công", f"Đã xóa gương mặt: {name}")
            popup.destroy()
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy thư mục gương mặt.")

    tk.Button(popup, text="Xóa", command=confirm_delete).pack(pady=10)

def update_face():
    name = simpledialog.askstring("Cập nhật gương mặt", "Nhập tên gương mặt cần cập nhật:")
    if name:
        face_system.add_face_from_webcam(name)
        messagebox.showinfo("Thành công", f"Đã cập nhật gương mặt: {name}")

# Giao diện chính
root = tk.Tk()
root.title("Hệ thống nhận diện gương mặt")
root.geometry("500x500")
root.resizable(False, False)

# Căn giữa màn hình
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (600 // 2)
y = (screen_height // 2) - (500 // 2)
root.geometry(f"500x500+{x}+{y}")

# Giao diện chính
tk.Label(root, text="🎯 Chọn chức năng", font=("Helvetica", 16)).pack(pady=15)
tk.Button(root, text="1. Nhận diện từ webcam", width=35, height=2, command=start_recognition).pack(pady=5)
tk.Button(root, text="2. Thêm gương mặt từ ảnh", width=35, height=2, command=add_from_image).pack(pady=5)
tk.Button(root, text="3. Thêm từ webcam (1 ảnh)", width=35, height=2, command=lambda: add_from_webcam(single=True)).pack(pady=5)
tk.Button(root, text="4. Thêm từ webcam (nhiều ảnh)", width=35, height=2, command=lambda: add_from_webcam(single=False)).pack(pady=5)
tk.Button(root, text="5. Xóa gương mặt", width=35, height=2, command=delete_face).pack(pady=5)
tk.Button(root, text="6. Cập nhật gương mặt", width=35, height=2, command=update_face).pack(pady=5)
tk.Button(root, text="Thoát", width=35, command=root.quit).pack(pady=20)

root.mainloop()

