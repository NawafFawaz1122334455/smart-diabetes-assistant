import streamlit as st
import os
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv

# --- بيانات الترجمة (Translation Data) ---
TRANSLATIONS = {
    'ar': {
        'app_title': "مساعد السكري الذكي",
        'welcome': "مرحباً بك في مساعد السكري الذكي",
        'app_purpose': "تم تصميم هذا التطبيق لمساعدتك في إدارة صحتك.",
        'explore_features': "استخدم قائمة التنقل لاستكشاف الميزات المختلفة.",
        'login_register': "تسجيل الدخول أو التسجيل",
        'otp_note': "ملاحظة: يتم تسجيل الدخول والتسجيل باستخدام البريد الإلكتروني وكلمة المرور ورمز التحقق (OTP).",
        
        # مفاتيح المصادقة
        'enter_email': "البريد الإلكتروني",
        'password_label': "كلمة المرور (6 أحرف أو أكثر)",
        'login_button': "تسجيل الدخول",
        'signup_button': "تسجيل جديد",
        'forgot_password_button': "نسيت كلمة المرور؟ (دخول مؤقت)",
        
        'enter_email_password_warning': "الرجاء إدخال البريد الإلكتروني وكلمة المرور.",
        'password_length_error': "خطأ: كلمة المرور يجب أن تكون 6 أحرف على الأقل.",
        
        'signup_success': "تم التسجيل بنجاح! يرجى الآن تسجيل الدخول (سيُطلب منك رمز تحقق).",
        'signup_error': "خطأ في التسجيل:",
        
        'verification_success': "تم تسجيل الدخول بنجاح! لقد سجلت دخولك الآن.",
        'login_invalid': "بيانات تسجيل الدخول غير صحيحة. يرجى التحقق من البريد الإلكتروني وكلمة المرور.",
        'verification_error': "خطأ في تسجيل الدخول:",
        
        'enter_email_for_reset': "أدخل بريدك الإلكتروني لإرسال رمز التحقق لمرة واحدة (OTP)",
        'send_reset_link_button': "إرسال رمز التحقق",
        'password_reset_sent': "تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني. **يجب تفعيل رابط التأكيد في إعدادات Supabase/Auth/Email Templates.**",
        'password_reset_error': "خطأ في إعادة تعيين كلمة المرور:",
        
        # مفاتيح OTP الجديدة
        'verify_otp_title': "التحقق بخطوتين (OTP)",
        'otp_sent_info': "تم إرسال رمز تحقق مكون من 6 أرقام إلى بريدك الإلكتروني. يرجى التحقق من صندوق الوارد (وقد تجده في البريد غير الهام).",
        'enter_otp': "أدخل رمز التحقق (OTP)",
        'verify_otp_button': "تحقق من الرمز",
        'otp_invalid': "رمز التحقق غير صحيح أو انتهت صلاحيته.",
        'otp_error': "خطأ في التحقق من الرمز:",
        
        # مفاتيح عامة
        'logout': "تسجيل الخروج",
        'logged_out': "تم تسجيل خروجك.",
        'navigation': "التنقل",
        'home_page': "الرئيسية",
        'products_page': "كتالوج المنتجات",
        'admin_page': "لوحة المسؤول",
        'water_page': "حاسبة المياه اليومية",
        'exercise_page': "توصيات التمارين",
        'admin_dashboard': "لوحة تحكم المسؤول",
        'admin_password': "أدخل كلمة مرور المسؤول",
        'admin_access_denied': "كلمة المرور غير صحيحة. تم رفض الوصول.",
        'add_product': "إضافة منتج جديد",
        'product_name': "اسم المنتج",
        'calories': "السعرات الحرارية",
        'sugar_g': "السكر (غ)",
        'carbs_g': "الكربوهيدرات (غ)",
        'protein_g': "البروتين (غ)",
        'fats_g': "الدهون (غ)",
        'suitability_question': "هل هذا المنتج مناسب لمرضى السكري؟",
        'suitable': "مناسب",
        'moderately_suitable': "مناسب باعتدال",
        'not_suitable': "غير مناسب",
        'upload_image': "تحميل صورة المنتج",
        'add_product_button': "إضافة المنتج",
        'fill_all_fields': "الرجاء ملء جميع الحقول المطلوبة وتحميل صورة.",
        'adding_product_spinner': "جاري إضافة المنتج...",
        'product_added_success': "تمت إضافة المنتج بنجاح!",
        'product_added_failed': "فشل في إضافة المنتج:",
        'edit_delete_product': "تعديل أو حذف منتج موجود",
        'select_product_to_edit': "اختر منتجاً للتعديل",
        'update_product': "تحديث المنتج",
        'delete_product': "حذف المنتج",
        'upload_new_image': "تحميل صورة جديدة (اختياري)",
        'updating_image_spinner': "جاري تحميل الصورة الجديدة...",
        'product_updated_success': "تم تحديث المنتج بنجاح!",
        'product_updated_failed': "فشل في تحديث المنتج:",
        'product_deleted_success': "تم حذف المنتج بنجاح!",
        'product_deleted_failed': "فشل في حذف المنتج:",
        'no_products_available': "لا توجد منتجات متاحة للتعديل أو الحذف.",
        'error_loading_products': "خطأ في تحميل المنتجات للتعديل/الحذف:",
        'search_product': "البحث عن منتج...",
        'suitability_label': "ملاءمة",
        'no_products_found': "لم يتم العثور على منتجات.",
        'error_fetching_products': "خطأ في جلب المنتجات:",
        'recommended_intake': "الكمية اليومية الموصى بها",
        'water_calc_title': "حاسبة المياه",
        'water_calc_desc': "احسب كمية الماء الموصى بها يومياً بناءً على وزنك وعمرك.",
        'water_tips_title': "نصائح عامة لمرضى السكري",
        'water_tip1': "نظام غذائي متوازن: ركّز على الأطعمة الكاملة، الفواكه، الخضروات، والبروتينات الخالية من الدهون.",
        'water_tip2': "تمرين منتظم: اهدف إلى 30 دقيقة على الأقل من التمارين المعتدلة معظم أيام الأسبوع.",
        'water_tip3': "مراقبة سكر الدم: افحص مستويات سكر الدم بانتظام حسب إرشادات طبيبك.",
        'water_tip4': "ابقَ رطباً: شرب كمية كافية من الماء يساعد في إدارة مستويات السكر في الدم.",
        'weight_kg': "وزنك (بالكيلوغرام)",
        'age_years': "عمرك (بالسنوات)",
        'calculate': "احسب",
        'realistic_input_warning': "الرجاء إدخال وزن وعمر واقعيين للحصول على توصية صالحة.",
        'liters': "لتر",
        'current_consumption': "استهلاكك الحالي",
        'daily_goal': "هدفك اليومي",
        'log_glass': "شربت كأس ماء ($250 \text{ml}$)",
        'reset_water': "إعادة تعيين الاستهلاك",
        'goal_reached': "تهانينا! لقد وصلت إلى هدفك اليومي أو تجاوزته! 🥳",
        'exercise_title': "توصيات التمارين",
        'exercise_desc': "اعثر على رياضة مناسبة لك بناءً على عمرك ووزنك.",
        'get_rec': "احصل على توصية",
        'exercise_tips_title': "نصائح حول ممارسة الرياضة مع مرض السكري",
        'exercise_tip1': "استشر طبيباً: تحدث دائماً مع طبيبك قبل بدء برنامج تمارين جديد.",
        'exercise_tip2': "افحص سكر الدم: افحص سكر الدم قبل وبعد التمرين لمعرفة كيفية استجابة جسمك.",
        'exercise_tip3': "حافظ على رطوبتك: اشرب الكثير من الماء قبل وأثناء وبعد التمرين.",
        'exercise_tip4': "احمل وجبة خفيفة: احتفظ بمصدر سريع للجلوكوز معك في حالة انخفاض نسبة السكر في الدم.",
        'loading_image_error': "خطأ في تحميل الصورة:",
        'image_upload_error': "خطأ في رفع الصورة:",
        'db_config_error': "خطأ: لم يتم تعيين متغيرات بيئة Supabase. يرجى التحقق من ملف .env الخاص بك.",
        'db_connect_error': "خطأ في الاتصال بـ Supabase:",
        'rec_realistic_input': "الرجاء إدخال عمر ووزن واقعيين للحصول على توصية موثوقة. بالنسبة للأطفال الصغار جداً، يجب أن يركز النشاط البدني على اللعب الحر.",
        'rec_under_18': "أنت في سن رائعة للنشاط البدني! ركّز على الأنشطة الممتعة مثل الجري أو السباحة أو الرياضات الجماعية.",
        'rec_18_40_light': "وزن جيد لسنك! حاول الحفاظ عليه من خلال أنشطة مثل الجري وركوب الدراجات وتمارين الأثقال.",
        'rec_18_40_heavy': "فكّر في تمارين الكارديو المعتدلة مثل المشي السريع أو الهرولة أو السباحة للتحكم في الوزن. استشر مدرباً للحصول على خطة مناسبة.",
        'rec_over_40': "ركّز على التمارين منخفضة التأثير مثل المشي أو السباحة أو اليوجا. هذه الأنشطة لطيفة على المفاصل وممتازة للتحكم في سكر الدم.",
    },
    'en': {
        'app_title': "Smart Diabetes Assistant",
        'welcome': "Welcome to the Smart Diabetes Assistant",
        'app_purpose': "This app is designed to help you manage your health.",
        'explore_features': "Use the navigation menu to explore different features.",
        'login_register': "Login or Register",
        'otp_note': "Note: Login and registration are handled using Email, Password, and a One-Time Password (OTP) for verification.",
        
        # New Auth Keys
        'enter_email': "Email",
        'password_label': "Password (6 characters or more)",
        'login_button': "Login",
        'signup_button': "Sign Up",
        'forgot_password_button': "Forgot Password? (Temporary Login)",

        'enter_email_password_warning': "Please enter email and password.",
        'password_length_error': "Error: Password must be at least 6 characters.",

        'signup_success': "Registration successful! Please proceed to login (OTP will be required).",
        'signup_error': "Signup Error:",

        'verification_success': "Login successful! You are now logged in.",
        'login_invalid': "Invalid login credentials. Please check your email and password.",
        'verification_error': "Login Error:",
        
        'enter_email_for_reset': "Enter your email to send a One-Time Password (OTP)",
        'send_reset_link_button': "Send Verification Code",
        'password_reset_sent': "A password reset link has been sent to your email. **You must configure the Confirmation URL in Supabase/Auth/Email Templates.**",
        'password_reset_error': "Error resetting password:",
        
        # New OTP Keys
        'verify_otp_title': "Two-Factor Verification (OTP)",
        'otp_sent_info': "A 6-digit verification code has been sent to your email. Please check your inbox (and spam folder).",
        'enter_otp': "Enter OTP Code",
        'verify_otp_button': "Verify Code",
        'otp_invalid': "Invalid or expired OTP code.",
        'otp_error': "OTP Verification Error:",
        
        # General Keys
        'logout': "Logout",
        'logged_out': "You have been logged out.",
        'navigation': "Navigation",
        'home_page': "Home",
        'products_page': "Product Catalog",
        'admin_page': "Admin Dashboard",
        'water_page': "Daily Water Calculator",
        'exercise_page': "Exercise Recommendations",
        'admin_dashboard': "Admin Dashboard",
        'admin_password': "Enter Admin Password",
        'admin_access_denied': "Incorrect password. Access denied.",
        'add_product': "Add a New Product",
        'product_name': "Product Name",
        'calories': "Calories",
        'sugar_g': "Sugar (g)",
        'carbs_g': "Carbohydrates (g)",
        'protein_g': "Protein (g)",
        'fats_g': "Fats (g)",
        'suitability_question': "Is this product suitable for diabetics?",
        'suitable': "Suitable",
        'moderately_suitable': "Moderately Suitable",
        'not_suitable': "Not Suitable",
        'upload_image': "Upload Product Image",
        'add_product_button': "Add Product",
        'fill_all_fields': "Please fill in all required fields and upload an image.",
        'adding_product_spinner': "Adding product...",
        'product_added_success': "Product added successfully!",
        'product_added_failed': "Failed to add product:",
        'edit_delete_product': "Edit or Delete Existing Product",
        'select_product_to_edit': "Select a product to edit",
        'update_product': "Update Product",
        'delete_product': "Delete Product",
        'upload_new_image': "Upload new image (optional)",
        'updating_image_spinner': "Uploading new image...",
        'product_updated_success': "Product updated successfully!",
        'product_updated_failed': "Failed to update product:",
        'product_deleted_success': "Product deleted successfully!",
        'product_deleted_failed': "Failed to delete product:",
        'no_products_available': "No products available to edit or delete.",
        'error_loading_products': "Error loading products for edit/delete:",
        'search_product': "Search for a product...",
        'suitability_label': "Suitability",
        'no_products_found': "No products found.",
        'error_fetching_products': "Error fetching products:",
        'recommended_intake': "Your recommended daily water intake is",
        'water_calc_title': "Water Intake Calculator",
        'water_calc_desc': "Calculate your recommended daily water intake based on your weight and age.",
        'water_tips_title': "General Tips for Diabetics",
        'water_tip1': "Balanced Diet: Focus on whole foods, fruits, vegetables, and lean proteins.",
        'water_tip2': "Regular Exercise: Aim for at least 30 minutes of moderate exercise most days of the week.",
        'water_tip3': "Monitor Blood Sugar: Check your blood sugar levels regularly as advised by your doctor.",
        'water_tip4': "Stay Hydrated: Drinking enough water helps manage blood sugar levels.",
        'weight_kg': "Your Weight (in kg)",
        'age_years': "Your Age (in years)",
        'calculate': "Calculate",
        'realistic_input_warning': "Please enter a realistic weight (e.g., above 15 kg) and age (e.g., above 5 years) to get a valid recommendation.",
        'liters': "liters",
        'current_consumption': "Current Consumption",
        'daily_goal': "Daily Goal",
        'log_glass': "Drank a glass of water ($250 \text{ml}$)",
        'reset_water': "Reset Consumption",
        'goal_reached': "Congratulations! You have reached or exceeded your daily goal! 🥳",
        'exercise_title': "Exercise Recommendations",
        'exercise_desc': "Find a sport that's suitable for you based on your age and weight.",
        'get_rec': "Get Recommendation",
        'exercise_tips_title': "Tips on Exercising with Diabetes",
        'exercise_tip1': "Consult a Doctor: Always talk to your doctor before starting a new exercise program.",
        'exercise_tip2': "Check Blood Sugar: Check your blood sugar before and after exercise to see how your body responds.",
        'exercise_tip3': "Stay Hydrated: Drink plenty of water before, during, and after your workout.",
        'exercise_tip4': "Carry a Snack: Keep a quick source of glucose with you in case of a low blood sugar episode.",
        'loading_image_error': "Error loading image:",
        'image_upload_error': "Error uploading image:",
        'db_config_error': "Error: Supabase environment variables are not set. Please check your .env file.",
        'db_connect_error': "Error connecting to Supabase:",
        'rec_realistic_input': "Please enter a realistic age and weight to get a reliable recommendation. For very young children, physical activity should focus on free play.",
        'rec_under_18': "You are in a great age for physical activity! Focus on playful activities like running, swimming, or team sports.",
        'rec_18_40_light': "Good weight for your age! Try to maintain it with activities like running, cycling, and weight training.",
        'rec_18_40_heavy': "Consider moderate-intensity cardio like brisk walking, jogging, or swimming to manage weight. Consult a trainer for a suitable plan.",
        'rec_over_40': "Focus on low-impact exercises like walking, swimming, or yoga. These activities are gentle on joints and great for blood sugar control.",
    }
}

def t(key):
    """دالة مساعدة لجلب النص المترجم بناءً على اللغة المختارة."""
    lang = st.session_state.get('language', 'ar')
    return TRANSLATIONS[lang].get(key, key) 

# --- دوال الإعداد والتخزين المؤقت (Setup and Caching Functions) ---

load_dotenv()

# استخدام st.cache_resource لضمان تهيئة Supabase مرة واحدة فقط
@st.cache_resource
def init_supabase_client() -> Client | None:
    """تهيئة عميل Supabase وضمان عدم تكرار العملية."""
    supabase_url: str = os.environ.get("SUPABASE_URL")
    supabase_key: str = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        st.error(t('db_config_error'))
        return None
    try:
        # st.cache_resource يضمن أن هذا الكائن لا يُنشأ إلا مرة واحدة
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"{t('db_connect_error')} {e}")
        return None

def init_session_state():
    """تهيئة متغيرات حالة الجلسة (Session State)."""
    if 'user' not in st.session_state:
        st.session_state['user'] = None
