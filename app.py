
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
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Home'
    if 'language' not in st.session_state: # حالة اللغة الجديدة
        st.session_state['language'] = 'ar' # الافتراضي: العربية
    # حالة جديدة لتحديد وضع المصادقة
    if 'auth_mode' not in st.session_state:
        st.session_state['auth_mode'] = 'login' 
    # حالة لتخزين البريد الإلكتروني مؤقتاً أثناء التحقق من OTP
    if 'temp_email' not in st.session_state:
        st.session_state['temp_email'] = None 
    # حالات جديدة لتتبع الماء
    if 'water_goal_liters' not in st.session_state:
        st.session_state['water_goal_liters'] = 0.0 # الهدف اليومي باللتر
    if 'water_consumed_ml' not in st.session_state:
        st.session_state['water_consumed_ml'] = 0 # الكمية المستهلكة بالمليلتر

# --- الإعداد الرئيسي للتطبيق ---
supabase = init_supabase_client()
init_session_state()

# --- دوال المصادقة (Auth Functions) ---

def sign_up_user(email, password):
    """تسجيل مستخدم جديد بالبريد الإلكتروني وكلمة المرور."""
    if not supabase: return
    try:
        # إنشاء المستخدم
        # ملاحظة: Supabase يرسل تلقائياً رابط تأكيد عند التسجيل
        supabase.auth.sign_up({"email": email, "password": password})
        st.success(t('signup_success'))
        # بعد التسجيل الناجح، نعود لوضع تسجيل الدخول
        st.session_state['auth_mode'] = 'login'
        st.session_state['temp_email'] = email # لتسهيل الانتقال لنموذج الدخول
        st.rerun()
    except Exception as e:
        st.error(f"{t('signup_error')} {e}")

def sign_in_user(email, password):
    """تسجيل دخول المستخدم بكلمة المرور، ثم الانتقال لخطوة OTP."""
    if not supabase: return
    try:
        # 1. التحقق من كلمة المرور
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        if response.user:
            # 2. إذا نجح التحقق: نقوم بتسجيل الخروج فوراً (لتدمير الجلسة مؤقتاً)
            # ثم ننتقل إلى وضع التحقق بخطوتين (OTP)
            supabase.auth.sign_out() 
            st.session_state['temp_email'] = email
            st.session_state['auth_mode'] = 'otp_verify'
            
            # نرسل رمز التحقق (OTP) للتحقق النهائي
            # نستخدم sign_in_with_otp فقط لإرسال الرمز، حتى لو كنا قد تحققنا من كلمة المرور
            supabase.auth.sign_in_with_otp({"email": email}) 
            st.rerun() 
        else:
            st.error(t('login_invalid'))
    except Exception as e:
        error_message = str(e)
        # محاولة تحديد إذا كان الخطأ متعلقاً ببيانات الاعتماد
        if "Invalid login credentials" in error_message or "Invalid login credentials" in error_message or "AuthApiError" in error_message:
            st.error(t('login_invalid'))
        else:
            st.error(f"{t('verification_error')} {e}")

def verify_otp_code(email, token):
    """التحقق من رمز OTP وإكمال تسجيل الدخول."""
    if not supabase: return
    try:
        # استخدام verify_otp لإكمال تدفق المصادقة
        response = supabase.auth.verify_otp({"email": email, "token": token, "type": "email"})
        
        if response.user:
            st.session_state['user'] = response.user
            st.session_state['page'] = 'Home'
            st.session_state['temp_email'] = None
            st.success(t('verification_success')) 
            st.rerun() 
        else:
            st.error(t('otp_invalid'))
            
    except Exception as e:
        error_message = str(e)
        if "Invalid" in error_message or "invalid" in error_message or "AuthApiError" in error_message:
            st.error(t('otp_invalid'))
        else:
            st.error(f"{t('otp_error')} {e}")

def reset_password(email):
    """
    إرسال رمز OTP لتمكين المستخدم من الدخول مؤقتاً عند نسيان كلمة المرور،
    بدلاً من إرسال رابط إعادة تعيين كلمة مرور. (التعديل المطلوب)
    """
    if not supabase: return
    try:
        # **التعديل الرئيسي:** استخدام sign_in_with_otp لإرسال رمز التحقق
        supabase.auth.sign_in_with_otp({"email": email})
        
        # تخزين البريد الإلكتروني مؤقتاً والانتقال إلى وضع التحقق
        st.session_state['temp_email'] = email
        st.session_state['auth_mode'] = 'otp_verify'
        
        # إظهار رسالة النجاح الخاصة بإرسال الرمز
        st.success(t('otp_sent_info'))
        st.rerun() 
        
    except Exception as e:
        st.error(f"{t('password_reset_error')} {e}")

def logout_user():
    """تسجيل خروج المستخدم ومسح حالة الجلسة."""
    if not supabase: return
    try:
        supabase.auth.sign_out()
        st.session_state['user'] = None
        st.session_state['page'] = 'Home'
        st.session_state['auth_mode'] = 'login' # إرجاع لوضع الدخول
        st.session_state['temp_email'] = None 
        st.info(t('logged_out'))
        st.rerun() 
    except Exception as e:
        st.error(f"Error during logout: {e}")

# --- دوال إدارة المنتجات والملفات (Product and File Management Functions) ---

# حجم الكأس الواحد بالمليلتر
GLASS_VOLUME_ML = 250

# دالة رفع الصورة إلى Supabase Storage
def upload_image_to_storage(image_file):
    if not supabase: return None
    try:
        # إنشاء اسم ملف فريد باستخدام UUID
        file_extension = image_file.name.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_extension}"
        bucket_name = "product_images" 

        # قراءة محتوى الملف
        file_bytes = image_file.read()

        # رفع الملف إلى Supabase Storage
        supabase.storage.from_(bucket_name).upload(
            file=file_bytes,
            path=file_name,
            file_options={"content-type": image_file.type}
        )

        # الحصول على الرابط العام للصورة المرفوعة
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        return public_url
    except Exception as e:
        st.error(f"{t('image_upload_error')} {e}")
        return None

def add_new_product(name, calories, sugar, protein, fats, carbs, suitability, image_url):
    if not supabase: return
    try:
        supabase.table("products").insert({"name": name, "calories": calories, "sugar": sugar, "protein": protein, "fats": fats, "carbs": carbs, "suitability": suitability, "image_url": image_url}).execute()
        st.success(t('product_added_success'))
    except Exception as e:
        st.error(f"{t('product_added_failed')} {e}")

def update_product_in_db(product_id, data_to_update):
    if not supabase: return
    try:
        supabase.table("products").update(data_to_update).eq("id", product_id).execute()
        st.success(t('product_updated_success'))
    except Exception as e:
        st.error(f"{t('product_updated_failed')} {e}")

def delete_product_from_db(product_id):
    if not supabase: return
    try:
        supabase.table("products").delete().eq("id", product_id).execute()
        st.success(t('product_deleted_success'))
    except Exception as e:
        st.error(f"{t('product_deleted_failed')} {e}")

# --- دوال حاسبة المياه والرياضة (Calculator and Exercise Functions) ---

def calculate_water_intake(weight_kg, age_years):
    if weight_kg <= 15 or age_years <= 5: 
        return 0 
        
    if 18 <= age_years <= 30:
        recommended_ml = weight_kg * 35
    elif 31 <= age_years <= 55:
        recommended_ml = weight_kg * 30
    else:
        recommended_ml = weight_kg * 25
    return recommended_ml / 1000

def get_exercise_recommendation(age, weight):
    if age <= 5 or weight <= 15:
        return t('rec_realistic_input')
        
    if age < 18:
        return t('rec_under_18')
    elif age <= 40:
        if weight < 70:
            return t('rec_18_40_light')
        else:
            return t('rec_18_40_heavy')
    else:
        return t('rec_over_40')

# --- دوال تحديث حالة الماء التفاعلية ---

def log_water_intake():
    """تضيف كأس ماء (250 مل) إلى الاستهلاك الحالي."""
    # نستخدم .get للحصول على القيمة الحالية مع قيمة افتراضية صفر في حال عدم وجودها
    st.session_state['water_consumed_ml'] = st.session_state.get('water_consumed_ml', 0) + GLASS_VOLUME_ML

def reset_water_intake():
    """تعيد تعيين الاستهلاك الحالي للماء إلى الصفر."""
    st.session_state['water_consumed_ml'] = 0


# --- صفحات التطبيق (App Pages) ---

def show_auth_page():
    st.title(t('login_register'))
    st.markdown(f"*{t('otp_note')}*") 

    # أزرار التبديل بين الأوضاع
    cols = st.columns(3)
    
    # تحديث وضع المصادقة عند الضغط على الزر
    if cols[0].button(t('login_button'), key='auth_login_btn'):
        st.session_state['auth_mode'] = 'login'
    if cols[1].button(t('signup_button'), key='auth_signup_btn'):
        st.session_state['auth_mode'] = 'signup'
    if cols[2].button(t('forgot_password_button'), key='auth_reset_btn'):
        st.session_state['auth_mode'] = 'reset'

    st.markdown("---")
    
    # --- نموذج التحقق بخطوتين (OTP Verification Form) ---
    if st.session_state['auth_mode'] == 'otp_verify' and st.session_state['temp_email']:
        email_to_verify = st.session_state['temp_email']
        st.subheader(t('verify_otp_title'))
        st.info(t('otp_sent_info'))
        
        with st.form(key="otp_verify_form_key"):
            st.markdown(f"**التحقق لـ:** `{email_to_verify}`")
            otp_code = st.text_input(t('enter_otp'), max_chars=6, key='otp_input')
            submit_button = st.form_submit_button(t('verify_otp_button'))
            
            if submit_button:
                if otp_code:
                    verify_otp_code(email_to_verify, otp_code)
                else:
                    st.warning(t('otp_invalid'))


    # --- نموذج تسجيل الدخول (Login Form) ---
    elif st.session_state['auth_mode'] == 'login':
        st.subheader(t('login_button'))
        # استخدام البريد الإلكتروني المؤقت كقيمة افتراضية إذا كان موجوداً
        default_email = st.session_state['temp_email'] if st.session_state['temp_email'] else ""
        with st.form(key="login_form_key"):
            email = st.text_input(t('enter_email'), key='login_email', value=default_email)
            password = st.text_input(t('password_label'), type='password', key='login_password')
            submit_button = st.form_submit_button(t('login_button'))
            
            if submit_button:
                if email and password:
                    sign_in_user(email, password)
                else:
                    st.warning(t('enter_email_password_warning'))

    # --- نموذج التسجيل (Signup Form) ---
    elif st.session_state['auth_mode'] == 'signup':
        st.subheader(t('signup_button'))
        with st.form(key="signup_form_key"):
            email = st.text_input(t('enter_email'), key='signup_email')
            password = st.text_input(t('password_label'), type='password', key='signup_password')
            submit_button = st.form_submit_button(t('signup_button'))
            
            if submit_button:
                if email and password:
                    if len(password) < 6:
                        st.error(t('password_length_error'))
                    else:
                        sign_up_user(email, password)
                else:
                    st.warning(t('enter_email_password_warning'))

    # --- نموذج نسيت كلمة المرور (Forgot Password Form) ---
    elif st.session_state['auth_mode'] == 'reset':
        st.subheader(t('forgot_password_button'))
        with st.form(key="reset_form_key"):
            email = st.text_input(t('enter_email_for_reset'), key='reset_email')
            submit_button = st.form_submit_button(t('send_reset_link_button'))
            
            if submit_button:
                if email:
                    reset_password(email)
                else:
                    st.warning(t('enter_email_password_warning'))

def show_home_page():
    st.title(t('welcome'))
    
    st.image("http://googleusercontent.com/image_collection/image_retrieval/some_id_string") # 

[Image of an illustration of a person drinking water next to a plate with healthy food]

    
    st.write(t('app_purpose'))
    st.write(t('explore_features'))

def show_products_page():
    st.title(t('products_page'))
    st.image("https://placehold.co/600x200/50C878/FFFFFF?text=Healthy+Foods")
    search_query = st.text_input(t('search_product'))
    try:
        query = supabase.table("products").select("*")
        if search_query:
            # البحث الجزئي
            query = query.ilike("name", f"%{search_query}%")
        products = query.execute().data
        if products:
            for product in products:
                # ترجمة مفتاح الملائمة المخزن في قاعدة البيانات
                suitability_keys = ['suitable', 'moderately_suitable', 'not_suitable']
                suitability_key_lookup = {key: t(key) for key in suitability_keys}
                suitability_text = suitability_key_lookup.get(product.get('suitability', 'not_suitable'), product.get('suitability', 'غير معروف'))
                
                st.subheader(f"{product['name']} - {t('suitability_label')}: {suitability_text}")
                
                try:
                    st.image(product['image_url'], width=200)
                except Exception:
                    st.warning(t('loading_image_error') + f" {product['image_url']}")

                st.write(f"**{t('calories')}:** {product['calories']}")
                carbs_value = product.get('carbs')
                st.write(f"**{t('carbs_g')}:** {carbs_value if carbs_value is not None else 'N/A'}")
                st.write(f"**{t('sugar_g')}:** {product['sugar']}g")
                st.write(f"**{t('protein_g')}:** {product['protein']}g")
                st.write(f"**{t('fats_g')}:** {product['fats']}g")
                st.write("---")
        else:
            st.info(t('no_products_found'))
    except Exception as e:
        st.error(f"{t('error_fetching_products')} {e}")

def show_admin_page():
    st.title(t('admin_dashboard'))
    admin_password = st.text_input(t('admin_password'), type="password")
    SECRET_CODE = "admin123" # كلمة المرور الافتراضية للمسؤول
    if admin_password == SECRET_CODE:
        show_add_product_form()
        st.markdown("---")
        show_edit_delete_form()
    else:
        st.warning(t('admin_access_denied'))

def show_add_product_form():
    st.subheader(t('add_product'))
    # الحصول على الخيارات المترجمة للملائمة
    suitability_keys = ['suitable', 'moderately_suitable', 'not_suitable']
    suitability_options_translated = [t(key) for key in suitability_keys]
    
    with st.form(key="add_product_form_key"):
        product_name = st.text_input(t('product_name'))
        calories = st.number_input(t('calories'), min_value=0)
        sugar = st.number_input(t('sugar_g'), min_value=0.0)
        carbs = st.number_input(t('carbs_g'), min_value=0.0)
        protein = st.number_input(t('protein_g'), min_value=0.0)
        fats = st.number_input(t('fats_g'), min_value=0.0)
        # استخدام الخيارات المترجمة في واجهة المستخدم
        suitability_translated = st.selectbox(t('suitability_question'), suitability_options_translated)
        uploaded_image = st.file_uploader(t('upload_image'), type=["png", "jpg", "jpeg"])
        submit_button = st.form_submit_button(t('add_product_button'))
        if submit_button:
            if uploaded_image and product_name:
                with st.spinner(t('adding_product_spinner')):
                    image_url = upload_image_to_storage(uploaded_image)
                    if image_url:
                        # نستخدم القيمة الإنجليزية (المفتاح) الموافق للخيار المترجم لحفظها في قاعدة البيانات
                        db_suitability_key = suitability_keys[suitability_options_translated.index(suitability_translated)]
                        add_new_product(product_name, calories, sugar, protein, fats, carbs, db_suitability_key, image_url)
            else:
                st.warning(t('fill_all_fields'))

def show_edit_delete_form():
    st.subheader(t('edit_delete_product'))
    try:
        products = supabase.table("products").select("*").execute().data
        if products:
            # استخدام قاموس يربط اسم المنتج بالكائن كاملاً
            product_names = {product['name']: product for product in products}
            selected_product_name = st.selectbox(t('select_product_to_edit'), list(product_names.keys()))

            if selected_product_name:
                selected_product = product_names[selected_product_name]
                
                # استخدام مفاتيح الملائمة الإنجليزية والقيم المترجمة
                suitability_options_keys = ['suitable', 'moderately_suitable', 'not_suitable']
                suitability_options_translated = [t(key) for key in suitability_options_keys]
                
                with st.form(key="edit_product_form_key"):
                    st.image(selected_product.get('image_url', 'https://placehold.co/200x200'), width=200) 
                    
                    new_name = st.text_input(t('product_name'), value=selected_product['name'])
                    new_calories = st.number_input(t('calories'), value=selected_product['calories'], min_value=0)

                    def safe_number(key, product):
                        value = product.get(key)
                        return float(value) if value is not None else 0.0

                    new_sugar = st.number_input(t('sugar_g'), value=safe_number('sugar', selected_product), min_value=0.0)
                    new_carbs = st.number_input(t('carbs_g'), value=safe_number('carbs', selected_product), min_value=0.0)
                    new_protein = st.number_input(t('protein_g'), value=safe_number('protein', selected_product), min_value=0.0)
                    new_fats = st.number_input(t('fats_g'), value=safe_number('fats', selected_product), min_value=0.0)
                    
                    # تحديد القيمة الافتراضية المترجمة (القيمة المخزنة هي المفتاح الإنجليزي)
                    db_suitability_key = selected_product['suitability'] if selected_product['suitability'] in suitability_options_keys else suitability_options_keys[0]
                    current_translated_value = t(db_suitability_key)
                    
                    # تحديد الفهرس للـ selectbox
                    current_index = suitability_options_translated.index(current_translated_value)

                    new_suitability_translated = st.selectbox(t('suitability_question'), suitability_options_translated, index=current_index)
                    new_image = st.file_uploader(t('upload_new_image'), type=["png", "jpg", "jpeg"])

                    col1, col2 = st.columns(2)
                    with col1:
                        update_button = st.form_submit_button(t('update_product'))
                    with col2:
                        delete_button = st.form_submit_button(t('delete_product'))

                    if update_button:
                        image_url_to_update = selected_product['image_url']
                        if new_image:
                            with st.spinner(t('updating_image_spinner')):
                                image_url_to_update = upload_image_to_storage(new_image)
                        
                        # إعادة القيمة المختارة إلى المفتاح الإنجليزي (الذي يُخزن في DB)
                        db_suitability_update = suitability_options_keys[suitability_options_translated.index(new_suitability_translated)]
                        
                        data_to_update = {
                            "name": new_name, 
                            "calories": new_calories, 
                            "sugar": new_sugar, 
                            "carbs": new_carbs, 
                            "protein": new_protein, 
                            "fats": new_fats, 
                            "suitability": db_suitability_update
                        }
                        if new_image: 
                            data_to_update["image_url"] = image_url_to_update
                            
                        update_product_in_db(selected_product['id'], data_to_update)
                        st.rerun()

                    if delete_button:
                        delete_product_from_db(selected_product['id'])
                        st.rerun() 
        else:
            st.info(t('no_products_available'))
    except Exception as e:
        st.error(f"{t('error_loading_products')} {e}")

def show_water_calculator_page():
    st.title(t('water_calc_title'))
    st.write(t('water_calc_desc'))
    
    # نموذج إدخال الوزن والعمر لحساب الهدف
    with st.form(key="water_goal_form_key"):
        weight_kg = st.number_input(t('weight_kg'), min_value=15.0, value=70.0, key='water_weight') 
        age_years = st.number_input(t('age_years'), min_value=5, value=30, key='water_age') 
        calculate_button = st.form_submit_button(t('calculate'))
    
    if calculate_button:
        if weight_kg < 15 or age_years < 5:
            st.warning(t('realistic_input_warning'))
            # إعادة تعيين الهدف إذا كان الإدخال غير صحيح
            st.session_state['water_goal_liters'] = 0.0 
        else:
            # حساب الهدف وتخزينه في حالة الجلسة
            recommended_liters = calculate_water_intake(weight_kg, age_years)
            st.session_state['water_goal_liters'] = recommended_liters
            st.success(f"{t('recommended_intake')} **{recommended_liters:.2f} {t('liters')}**.")

    # --- شاشة التتبع التفاعلية للماء ---
    st.markdown("---")
    st.subheader(f"💧 {t('daily_goal')}")
    
    # تعريف المتغيرات المحلية من حالة الجلسة وتجهيزها
    water_goal_ml = st.session_state.get('water_goal_liters', 0.0) * 1000
    consumed_ml = st.session_state.get('water_consumed_ml', 0) 

    # حساب نسبة التقدم
    if water_goal_ml > 0:
        progress_ratio = min(consumed_ml / water_goal_ml, 1.0) # لا تتجاوز 100%
        progress_percent = int(progress_ratio * 100)
    else:
        # إذا لم يتم حساب الهدف بعد أو كان الهدف صفراً
        progress_ratio = 0.0
        progress_percent = 0

    # عرض التقدم 
    st.markdown(f"**{t('current_consumption')}:** $${consumed_ml} \\text{{ml}} / {water_goal_ml:.0f} \\text{{ml}}$$")
    st.progress(progress_ratio, text=f"{progress_percent}%")

    if progress_ratio >= 1.0:
        st.balloons()
        st.success(t('goal_reached'))

    # أزرار التفاعل
    col1, col2 = st.columns(2)
    
    # زر إضافة كأس ماء
    with col1:
        st.button(t('log_glass'), on_click=log_water_intake, use_container_width=True, type='primary')
    
    # زر إعادة التعيين
    with col2:
        st.button(t('reset_water'), on_click=reset_water_intake, use_container_width=True)

    # نصائح عامة 
    st.markdown("---")
    with st.expander(t('water_tips_title')):
        st.write(f"- **{t('water_tip1')}**")
        st.write(f"- **{t('water_tip2')}**")
        st.write(f"- **{t('water_tip3')}**")
        st.write(f"- **{t('water_tip4')}**")


def show_exercise_page():
    st.title(t('exercise_title'))
    st.write(t('exercise_desc'))
    st.image("http://googleusercontent.com/image_collection/image_retrieval/some_id_string") # 

[Image of person jogging outdoors]

    with st.form(key="exercise_form_key"):
        age = st.number_input(t('age_years'), min_value=5, value=30) 
        weight = st.number_input(t('weight_kg'), min_value=15.0, value=70.0) 
        get_rec_button = st.form_submit_button(t('get_rec'))
    if get_rec_button:
        if age < 5 or weight < 15:
            st.warning(t('realistic_input_warning'))
        else:
            st.info(get_exercise_recommendation(age, weight))
    with st.expander(t('exercise_tips_title')):
        st.write(f"- **{t('exercise_tip1')}**")
        st.write(f"- **{t('exercise_tip2')}**")
        st.write(f"- **{t('exercise_tip3')}**")
        st.write(f"- **{t('exercise_tip4')}**")

# --- منطق التنقل الرئيسي مع اختيار اللغة ---
st.sidebar.title(t('navigation'))

# قائمة تحديد اللغة
lang_options = {'العربية': 'ar', 'English': 'en'}
current_lang_display = 'العربية' if st.session_state['language'] == 'ar' else 'English'
selected_lang_display = st.sidebar.radio("Language / اللغة", list(lang_options.keys()), index=list(lang_options.keys()).index(current_lang_display))

# إذا تم تغيير اللغة، قم بتحديثها وإعادة التشغيل
if st.session_state['language'] != lang_options[selected_lang_display]:
    st.session_state['language'] = lang_options[selected_lang_display]
    st.rerun()

if st.session_state['user']:
    # إذا كان المستخدم مسجلاً دخوله، اعرض خيارات التطبيق
    if st.sidebar.button(t('logout')):
        logout_user()
    
    # تحديد أسماء الصفحات المترجمة
    page_options = {
        t('home_page'): show_home_page, 
        t('products_page'): show_products_page, 
        t('admin_page'): show_admin_page, 
        t('water_page'): show_water_calculator_page, 
        t('exercise_page'): show_exercise_page
    }
    
    # البحث عن الاسم المترجم الحالي للصفحة
    current_page_func_name = st.session_state['page'].lower() + '_page'
    current_page_translated_name = next((k for k, v in page_options.items() if v.__name__ == 'show_' + current_page_func_name), t('home_page'))

    # قائمة الـ Radio button تستخدم الأسماء المترجمة
    page_name_translated = st.sidebar.radio(t('navigation'), list(page_options.keys()), index=list(page_options.keys()).index(current_page_translated_name))
    
    # تحديث وتنفيذ الصفحة المختارة
    for name, func in page_options.items():
        if name == page_name_translated:
            # تحديث اسم الصفحة المخزن ليتوافق مع مفتاح الدالة (مثل 'Home')
            st.session_state['page'] = func.__name__.replace('show_', '').replace('_page', '').capitalize()
            func()
            break
else:
    # إذا لم يسجل الدخول، اعرض صفحة المصادقة
    show_auth_page()



