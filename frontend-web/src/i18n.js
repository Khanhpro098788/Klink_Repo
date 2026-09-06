import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Translations for Auth screens (Login, Register)
const resources = {
  en: {
    translation: {
      // Common
      "klink_ai_video": "Klink AI",
      "video": "Video",
      
      // Login Screen
      "login_banner_text": "Experience the virtual director platform with RAG technology and lightning-fast rendering. Sign in to start creating.",
      "welcome_back": "Welcome back",
      "email": "Email",
      "enter_email": "Enter your email",
      "password": "Password",
      "enter_password": "••••••••",
      "forgot_password": "Forgot password?",
      "sign_in": "Sign In",
      "signing_in": "Signing in...",
      "no_account": "Don't have an account?",
      "create_one": "Create one",
      "login_failed": "Login failed. Please check your credentials.",

      // Register Screen
      "create_account": "Create Account",
      "join_klink": "Join",
      "get_free_credits": "and get 10 free credits.",
      "full_name": "Full Name",
      "enter_full_name": "John Doe",
      "sign_up": "Sign Up",
      "creating": "Creating...",
      "have_account": "Already have an account?",
      
      // OTP Screen
      "verify_otp": "Verify OTP",
      "otp_sent": "Please check your email for the OTP code.",
      "enter_otp": "Enter 6-digit OTP",
      "verify": "Verify",
      "verifying": "Verifying...",
      
      // Google Auth
      "google_signin": "Sign in with Google",
      "google_signup": "Sign up with Google",
      
      // Language Switcher
      "language": "Language",
      "vi": "Tiếng Việt",
      "en": "English",
      
      // Header & Dropdown
      "profile": "Profile",
      "change_password": "Change Password",
      "settings": "Settings",
      "logout": "Logout",
      
      // Profile Screen
      "profile_settings": "Profile Settings",
      "avatar": "Avatar",
      "update_profile": "Update Profile",
      "updating": "Updating...",
      "profile_updated": "Profile updated successfully",
      "old_password": "Old Password",
      "new_password": "New Password",
      "password_changed": "Password changed successfully"
    }
  },
  vi: {
    translation: {
      // Common
      "klink_ai_video": "Klink AI",
      "video": "Video",

      // Login Screen
      "login_banner_text": "Trải nghiệm nền tảng đạo diễn ảo với công nghệ RAG và Render siêu tốc. Đăng nhập để bắt đầu sáng tạo.",
      "welcome_back": "Chào mừng trở lại",
      "email": "Email",
      "enter_email": "Nhập email của bạn",
      "password": "Mật khẩu",
      "enter_password": "••••••••",
      "forgot_password": "Quên mật khẩu?",
      "sign_in": "Đăng Nhập",
      "signing_in": "Đang xử lý...",
      "no_account": "Chưa có tài khoản?",
      "create_one": "Tạo ngay",
      "login_failed": "Đăng nhập thất bại. Vui lòng kiểm tra lại.",

      // Register Screen
      "create_account": "Tạo Tài Khoản",
      "join_klink": "Tham gia",
      "get_free_credits": "và nhận ngay 10 credit miễn phí.",
      "full_name": "Họ và Tên",
      "enter_full_name": "Nguyễn Văn A",
      "sign_up": "Đăng Ký",
      "creating": "Đang tạo...",
      "have_account": "Đã có tài khoản?",

      // OTP Screen
      "verify_otp": "Xác thực OTP",
      "otp_sent": "Vui lòng kiểm tra email để lấy mã OTP.",
      "enter_otp": "Nhập mã OTP 6 số",
      "verify": "Xác thực",
      "verifying": "Đang xác thực...",
      
      // Google Auth
      "google_signin": "Đăng nhập bằng Google",
      "google_signup": "Đăng ký bằng Google",

      // Language Switcher
      "language": "Ngôn ngữ",
      "vi": "Tiếng Việt",
      "en": "English",
      
      // Header & Dropdown
      "profile": "Hồ sơ",
      "change_password": "Đổi mật khẩu",
      "settings": "Cài đặt",
      "logout": "Đăng xuất",
      
      // Profile Screen
      "profile_settings": "Cài đặt hồ sơ",
      "avatar": "Ảnh đại diện",
      "update_profile": "Cập nhật hồ sơ",
      "updating": "Đang cập nhật...",
      "profile_updated": "Cập nhật hồ sơ thành công",
      "old_password": "Mật khẩu cũ",
      "new_password": "Mật khẩu mới",
      "password_changed": "Đổi mật khẩu thành công"
    }
  }
};

i18n
  .use(initReactI18next) // passes i18n down to react-i18next
  .init({
    resources,
    lng: 'vi', // default language is Vietnamese
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false // react already safes from xss
    }
  });

export default i18n;
