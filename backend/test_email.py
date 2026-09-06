import asyncio
import os
from dotenv import load_dotenv
from email.message import EmailMessage
import aiosmtplib

# Đọc file .env
load_dotenv(dotenv_path="../.env")

async def test_email():
    email = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    
    if password == "<NHAP_MAT_KHAU_UNG_DUNG_16_KY_TU_VAO_DAY>" or not password:
        print("❌ LỖI: Bạn chưa nhập Mật khẩu ứng dụng vào file .env!")
        print("👉 Hãy mở file d:\\Klink\\.env, tìm dòng SMTP_PASSWORD và dán mật khẩu 16 ký tự của bạn vào đó.")
        return

    print(f"🔄 Đang kết nối đến máy chủ Google bằng tài khoản: {email}...")
    
    message = EmailMessage()
    message["From"] = email
    message["To"] = email # Gửi cho chính mình để test
    message["Subject"] = "Klink AI - Test Email Thành Công"
    message.set_content(
        "Xin chào,\n\n"
        "Nếu bạn nhận được email này, tính năng gửi mã OTP của hệ thống Klink AI đã hoạt động hoàn hảo!\n\n"
        "Bây giờ mọi endpoint đăng ký đều có thể gửi mail thật."
    )

    try:
        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            username=email,
            password=password,
            use_tls=False,
            start_tls=True,
            timeout=10,
        )
        print("✅ THÀNH CÔNG! Thư đã được gửi đi. Hãy mở hộp thư Gmail của bạn để kiểm tra nhé!")
    except Exception as e:
        print(f"❌ THẤT BẠI. Google báo lỗi: {e}")
        print("👉 Nguyên nhân thường là: Mật khẩu ứng dụng bị sai, hoặc bạn nhập thiếu/thừa dấu cách.")

if __name__ == "__main__":
    asyncio.run(test_email())
