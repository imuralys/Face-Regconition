import pyodbc
import bcrypt

# Cấu hình SQL Server
SERVER_NAME = "dght1104"
DATABASE_NAME = "face_recognition"
DRIVER = "{ODBC Driver 17 for SQL Server}"

def get_db_connection():
    """Kết nối SQL Server."""
    return pyodbc.connect(
        f'DRIVER={DRIVER};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;'
    )

def init_db():
    """Tạo bảng users nếu chưa tồn tại."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
            CREATE TABLE users (
                id INT IDENTITY PRIMARY KEY,
                name NVARCHAR(100) UNIQUE NOT NULL,
                password VARBINARY(MAX) NOT NULL,
                encoding VARBINARY(MAX) NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("✅ Kiểm tra & tạo bảng users thành công!")
    except Exception as e:
        print(f"❌ Lỗi tạo bảng: {e}")

def hash_password(password):
    """Băm mật khẩu bằng bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def check_password(password, hashed_password):
    """Kiểm tra mật khẩu có khớp với hash không."""
    return bcrypt.checkpw(password.encode(), hashed_password)

if __name__ == "__main__":
    init_db()  # Chạy file này để tạo bảng trước khi đăng ký