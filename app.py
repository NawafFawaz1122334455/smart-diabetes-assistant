import streamlit as st
import os
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv

# --- تعريف نصوص التطبيق لخاصية الترجمة ---
# (تم حذف القاموس اختصاراً، لكنه موجود في ملفك الأصلي)
TEXTS = {
    "ar": {
        # Navigation & Page Titles
        "home_page": "الصفحة الرئيسية",
        "products_catalog": "كتالوج المنتجات",
        "admin_dashboard": "لوحة تحكم المسؤول",
        "water_calculator": "حاسبة الماء",
        "exercise_recs": "توصيات التمارين",
        "navigation": "التنقل",
        "logout": "تسجيل الخروج",
        "lang_selector": "اختر اللغة",

        # Home Page
        "welcome_title": "مرحباً بك في مساعد السكري الذكي",
        "welcome_msg_1": "هذا التطبيق مصمم لمساعدتك في إدارة صحتك ونظامك الغذائي.",
        "welcome_msg_2": "استخدم قائمة التنقل لاستكشاف الميزات المختلفة.",

        # Auth Page
        "auth_title": "تسجيل الدخول والمصادقة",
        "pass_auth_title": "مصادقة كلمة المرور",
        "mode_login": "تسجيل الدخول (يتطلب إيميل وكلمة مرور)",
        "mode_signup": "التسجيل",
        "mode_forgot": "نسيت كلمة المرور؟",
        "login_info": "ملاحظة: يتطلب تسجيل الدخول الناجح **كلمة المرور الصحيحة** يتبعها **التحقق برمز OTP**.",
        "email": "البريد الإلكتروني",
        "password": "كلمة المرور",
        "confirm_password": "تأكيد كلمة المرور",
        "login_btn": "تسجيل الدخول",
        "signup_btn": "التسجيل",
        "signup_success": "تم التسجيل بنجاح! الرجاء استخدام خيار 'تسجيل الدخول' للمتابعة والتحقق والوصول إلى التطبيق.",
        "otp_verification": "التحقق برمز (OTP)",
        "otp_sent_info": "تم إرسال رمز OTP إلى **{}**. الرجاء إدخاله أدناه لإكمال تسجيل الدخول.",
        "enter_otp": "أدخل رمز OTP من بريدك الإلكتروني",
        "verify_btn": "التحقق من الرمز",
        "cancel_login": "إلغاء تسجيل الدخول",
        "send_reset_link": "إرسال رابط إعادة التعيين",
        "enter_reset_email": "أدخل بريدك الإلكتروني لاستلام رابط إعادة تعيين كلمة المرور",
        
        # Products Page
        "products_title": "كتالوج المنتجات",
        "products_placeholder": "Healthy Foods",
        "search_product": "ابحث عن منتج...",
        "suitability": "ملائمة المنتج",
        "calories": "السعرات الحرارية",
        "carbs": "الكربوهيدرات (غ)",
        "sugar": "السكر (غ)",
        "protein": "البروتين (غ)",
        "fats": "الدهون (غ)",
        "not_available": "غير متاح",
        "no_products": "لم يتم العثور على منتجات.",
        
        # Water Calculator
        "water_calc_title": "حاسبة استهلاك الماء",
        "water_calc_msg": "احسب كمية الماء اليومية الموصى بها بناءً على وزنك وعمرك.",
        "water_placeholder": "Stay Hydrated",
        "general_advice": "نصائح عامة لمرضى السكري",
        "advice_1": "- **نظام غذائي متوازن:** ركز على الأطعمة الكاملة والخضروات والبروتينات الخالية من الدهون.",
        "advice_2": "- **تمارين منتظمة:** استهدف 30 دقيقة على الأقل من التمارين المعتدلة معظم أيام الأسبوع.",
        "advice_3": "- **مراقبة السكر:** افحص مستويات السكر في الدم بانتظام حسب إرشادات طبيبك.",
        "advice_4": "- **حافظ على رطوبتك:** شرب كمية كافية من الماء يساعد في إدارة مستويات السكر في الدم.",
        "weight_kg": "وزنك (كجم)",
        "age_years": "عمرك (سنوات)",
        "calculate_btn": "احسب",
        "reliable_warning": "الرجاء إدخال وزن وعمر واقعيين (أكثر من 15 كجم و 5 سنوات) للحصول على توصية موثوقة.",
        "recommended_intake": "الكمية الموصى بها من الماء يوميًا هي **{:.2f} لتر**.",

        # Exercise Recommendations
        "exercise_title": "توصيات التمارين",
        "exercise_msg": "ابحث عن تمرين مناسب بناءً على عمرك ووزنك.",
        "exercise_placeholder": "Exercise and Health",
        "get_rec_btn": "احصل على توصية",
        "tips_exercise": "نصائح لممارسة الرياضة مع مرض السكري",
        "tip_1": "- **استشر الطبيب:** تحدث دائمًا مع طبيبك قبل البدء بأي برنامج رياضي جديد.",
        "tip_2": "- **افحص سكر الدم:** اختبر سكر الدم قبل وبعد التمرين لمعرفة كيفية استجابة جسمك.",
        "tip_3": "- **حافظ على رطوبتك:** اشرب الكثير من الماء قبل وأثناء وبعد التمرين.",
        "tip_4": "- **احمل وجبة خفيفة:** احتفظ بمصدر جلوكوز سريع المفعول معك في حال حدوث انخفاض مفاجئ في السكر.",

        # Admin Page
        "admin_title": "لوحة تحكم المسؤول",
        "admin_password": "أدخل كلمة مرور المسؤول",
        "admin_denied": "كلمة مرور غير صحيحة. تم رفض الوصول.",
        "add_product_title": "إضافة منتج جديد",
        "product_name": "اسم المنتج",
        "upload_image": "تحميل صورة المنتج",
        "add_product_btn": "إضافة المنتج",
        "edit_delete_title": "تعديل أو حذف منتج موجود",
        "select_product_edit": "اختر منتجًا للتعديل",
        "update_btn": "تحديث المنتج",
        "delete_btn": "حذف المنتج",
        "upload_new_image": "تحميل صورة جديدة (اختياري)",
        "suitability_options": ["ملائم", "ملائم باعتدال", "غير ملائم"],
    },
    "en": {
        # Navigation & Page Titles
        "home_page": "Home Page",
        "products_catalog": "Product Catalog",
        "admin_dashboard": "Admin Dashboard",
        "water_calculator": "Water Calculator",
        "exercise_recs": "Exercise Recommendations",
        "navigation": "Navigation",
        "logout": "Logout",
        "lang_selector": "Select Language",

        # Home Page
        "welcome_title": "Welcome to the Smart Diabetes Assistant",
        "welcome_msg_1": "This application is designed to help you manage your health and diet.",
        "welcome_msg_2": "Use the navigation menu to explore the different features.",

        # Auth Page
        "auth_title": "Login and Authentication",
        "pass_auth_title": "Password Authentication",
        "mode_login": "Login (Email & Password Required)",
        "mode_signup": "Signup",
        "mode_forgot": "Forgot Password?",
        "login_info": "Note: Successful login requires the **correct password** followed by **OTP verification**.",
        "email": "Email",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "login_btn": "Login",
        "signup_btn": "Signup",
        "signup_success": "Registration successful! Please use the 'Login' option to proceed with verification and access the application.",
        "otp_verification": "One-Time Password (OTP) Verification",
        "otp_sent_info": "An OTP code has been sent to **{}**. Please enter it below to complete login.",
        "enter_otp": "Enter OTP Code from your Email",
        "verify_btn": "Verify Code",
        "cancel_login": "Cancel Login",
        "send_reset_link": "Send Reset Link",
        "enter_reset_email": "Enter your Email to receive a password reset link",

        # Products Page
        "products_title": "Product Catalog",
        "products_placeholder": "Healthy Foods",
        "search_product": "Search for a product...",
        "suitability": "Suitability",
        "calories": "Calories",
        "carbs": "Carbs (g)",
        "sugar": "Sugar (g)",
        "protein": "Protein (g)",
        "fats": "Fats (g)",
        "not_available": "N/A",
        "no_products": "No products found.",
        
        # Water Calculator
        "water_calc_title": "Water Intake Calculator",
        "water_calc_msg": "Calculate your recommended daily water intake based on your weight and age.",
        "water_placeholder": "Stay Hydrated",
        "general_advice": "General Advice for Diabetics",
        "advice_1": "- **Balanced Diet:** Focus on whole foods, fruits, vegetables, and lean proteins.",
        "advice_2": "- **Regular Exercise:** Aim for at least 30 minutes of moderate exercise most days of the week.",
        "advice_3": "- **Monitor Blood Sugar:** Check your blood sugar levels regularly as advised by your doctor.",
        "advice_4": "- **Stay Hydrated:** Drinking enough water helps manage blood sugar levels.",
        "weight_kg": "Your Weight (kg)",
        "age_years": "Your Age (years)",
        "calculate_btn": "Calculate",
        "reliable_warning": "Please enter a realistic weight and age (over 15 kg and 5 years) for a reliable recommendation.",
        "recommended_intake": "Your recommended daily water intake is **{:.2f} liters**.",

        # Exercise Recommendations
        "exercise_title": "Exercise Recommendations",
        "exercise_msg": "Find a suitable exercise based on your age and weight.",
        "exercise_placeholder": "Exercise and Health",
        "get_rec_btn": "Get Recommendation",
        "tips_exercise": "Tips for Exercising with Diabetes",
        "tip_1": "- **Consult a Doctor:** Always talk to your doctor before starting any new exercise program.",
        "tip_2": "- **Check Blood Sugar:** Test your blood sugar before and after exercise to know how your body responds.",
        "tip_3": "- **Stay Hydrated:** Drink plenty of water before, during, and after your workout.",
        "tip_4": "- **Carry a Snack:** Keep a fast-acting source of glucose with you in case of a sudden sugar drop.",

        # Admin Page
        "admin_title": "Admin Dashboard",
        "admin_password": "Enter Admin Password",
        "admin_denied": "Incorrect password. Access denied.",
        "add_product_title": "Add New Product",
        "product_name": "Product Name",
        "upload_image": "Upload Product Image",
        "add_product_btn": "Add Product",
        "edit_delete_title": "Edit or Delete Existing Product",
        "select_product_edit": "Select a product to edit",
        "update_btn": "Update Product",
        "delete_btn": "Delete Product",
        "upload_new_image": "Upload New Image (Optional)",
        "suitability_options": ["Suitable", "Moderately Suitable", "Not Suitable"],
    }
}
# --- دالة مساعدة للحصول على النص المترجم ---
def get_text(key):
    # افتراض اللغة العربية (ar) كخيار افتراضي
    lang = st.session_state.get('language', 'ar')
    return TEXTS[lang].get(key, key) # يعود بالنص نفسه إذا لم يتم العثور على المفتاح

# --- إعدادات الصفحة (يجب أن يكون هذا أول استدعاء لـ Streamlit) ---
st.set_page_config(
    page_title="SMART DA .COM", 
    page_icon="🩺", 
    layout="wide",       
    initial_sidebar_state="expanded"
)
# -----------------------------------------------------------------

# --- الإعداد والتخزين المؤقت ---

load_dotenv()

# Initialize Supabase client once
@st.cache_resource
def init_supabase_client() -> Client | None:
    # Fetch environment keys
    supabase_url: str = os.environ.get("SUPABASE_URL")
    supabase_key: str = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        st.error("Error: Supabase environment variables are not set. Please check your .env file.")
        return None
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Error connecting to Supabase: {e}")
        return None

def init_session_state():
    # Initialize session states
    if 'user' not in st.session_state: st.session_state['user'] = None
    if 'otp_sent' not in st.session_state: st.session_state['otp_sent'] = False
    if 'user_email' not in st.session_state: st.session_state['user_email'] = ""
    if 'page' not in st.session_state: st.session_state['page'] = 'Home'
    if 'language' not in st.session_state: st.session_state['language'] = 'ar' # اللغة الافتراضية

# --- التهيئة العامة ---
supabase = init_supabase_client()
init_session_state()

# --- وظائف المصادقة (لم تتغير) ---

def signup_user(email, password):
    # وظيفة تسجيل مستخدم جديد
    if not supabase: return
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            st.success(get_text("signup_success"))
            return True
        else:
            st.error("Registration failed. Email might already exist or password is weak.")
            return False
    except Exception as e:
        st.error(f"Error during registration: {e}")
        return False

def login_user(email, password):
    # وظيفة تسجيل الدخول (تبدأ بخطوة التحقق من كلمة المرور تليها OTP)
    if not supabase: return
    try:
        # 1. Verify password
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            # 2. Sign out immediately to enforce OTP, then send OTP
            supabase.auth.sign_out() 
            st.session_state['user'] = None
            st.success("Password verified! Sending One-Time Password (OTP) to your email...")
            send_otp(email)
            st.rerun()
            return True
        else:
            st.error("Incorrect email or password.")
            return False
    except Exception as e:
        st.error(f"Error during login verification: {e}")
        return False

def reset_password(email):
    # وظيفة إعادة تعيين كلمة المرور
    if not supabase: return
    try:
        supabase.auth.reset_password_for_email(email)
        st.session_state['user_email'] = email
        st.success("A password reset link has been sent to your email. Please check your inbox.")
    except Exception as e:
        st.error(f"Error sending password reset link: {e}")

def send_otp(email):
    # وظيفة إرسال رمز OTP
    if not supabase: return
    try:
        supabase.auth.sign_in_with_otp({"email": email})
        st.session_state['otp_sent'] = True
        st.session_state['user_email'] = email
        st.toast("Code sent!")
    except Exception as e:
        st.error(f"Error sending OTP code: {e}")

def verify_otp(email, token):
    # وظيفة التحقق من رمز OTP
    if not supabase: return
    try:
        response = supabase.auth.verify_otp({"email": email, "token": token, "type": "email"})
        if response.user:
            st.session_state['user'] = response.user
            st.session_state['otp_sent'] = False
            st.session_state['user_email'] = ""
            st.session_state['page'] = 'Home'
            st.success("Verification successful! You are now logged in.")
        else:
            st.error("Invalid OTP code. Please try again.")
    except Exception as e:
        st.error(f"Error verifying OTP code: {e}")

def logout_user():
    # وظيفة تسجيل الخروج
    if not supabase: return
    try:
        supabase.auth.sign_out()
        st.session_state['user'] = None
        st.session_state['otp_sent'] = False
        st.session_state['user_email'] = ""
        st.session_state['page'] = 'Home'
        st.info("You have been logged out.")
    except Exception as e:
        st.error(f"Error during logout: {e}")

# --- وظائف إدارة المنتجات والملفات (لم تتغير) ---

def upload_image_to_storage(image_file):
    if not supabase: return None
    try:
        file_extension = image_file.name.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_extension}"
        bucket_name = "product_images" 
        file_bytes = image_file.read()
        supabase.storage.from_(bucket_name).upload(
            file=file_bytes,
            path=file_name,
            file_options={"content-type": image_file.type}
        )
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        return public_url
    except Exception as e:
        st.error(f"Error uploading image: {e}")
        return None

def add_new_product(name, calories, sugar, protein, fats, carbs, suitability, image_url):
    if not supabase: return
    try:
        supabase.table("products").insert({"name": name, "calories": calories, "sugar": sugar, "protein": protein, "fats": fats, "carbs": carbs, "suitability": suitability, "image_url": image_url}).execute()
        st.success("Product added successfully!")
    except Exception as e:
        st.error(f"Failed to add product: {e}")

def update_product_in_db(product_id, data_to_update):
    if not supabase: return
    try:
        supabase.table("products").update(data_to_update).eq("id", product_id).execute()
        st.success("Product updated successfully!")
    except Exception as e:
        st.error(f"Failed to update product: {e}")

def delete_product_from_db(product_id):
    if not supabase: return
    try:
        supabase.table("products").delete().eq("id", product_id).execute()
        st.success("Product deleted successfully!")
    except Exception as e:
        st.error(f"Failed to delete product: {e}")

# --- وظائف مساعدة (لم تتغير) ---
def calculate_water_intake(weight_kg, age_years):
    if weight_kg <= 15 or age_years <= 5: return 0 
    if 18 <= age_years <= 30: recommended_ml = weight_kg * 35
    elif 31 <= age_years <= 55: recommended_ml = weight_kg * 30
    else: recommended_ml = weight_kg * 25
    return recommended_ml / 1000

def get_exercise_recommendation(age, weight):
    # هذه النصوص لم يتم وضعها في القاموس لأنها ديناميكية ويجب ترجمتها هنا
    lang = st.session_state.get('language', 'ar')
    if lang == 'ar':
        if age <= 5 or weight <= 15:
            return "الرجاء إدخال عمر ووزن واقعيين للحصول على توصية موثوقة. بالنسبة للأطفال الصغار جدًا، يجب أن تركز الأنشطة البدنية على اللعب الحر."
        if age < 18:
            return "أنت في عمر ممتاز للنشاط البدني! ركز على الأنشطة الممتعة مثل الجري أو السباحة أو الرياضات الجماعية."
        elif age <= 40:
            if weight < 70:
                return "وزن جيد لعمرك! حاول الحفاظ عليه من خلال أنشطة مثل الجري وركوب الدراجات وتمارين القوة."
            else:
                return "فكر في تمارين الكارديو المعتدلة الشدة مثل المشي السريع أو الهرولة أو السباحة لإدارة الوزن. استشر مدربًا للحصول على خطة مناسبة."
        else:
            return "ركز على التمارين منخفضة التأثير مثل المشي أو السباحة أو اليوجا. هذه لطيفة على المفاصل وممتازة للتحكم في سكر الدم."
    else: # English
        if age <= 5 or weight <= 15:
            return "Please enter a realistic age and weight for a trusted recommendation. For very young children, physical activities should focus on free play."
        if age < 18:
            return "You're at a great age for physical activity! Focus on fun activities like running, swimming, or team sports."
        elif age <= 40:
            if weight < 70:
                return "Good weight for your age! Try to maintain it with activities like running, cycling, and strength training."
            else:
                return "Consider moderate-intensity cardio exercises like brisk walking, jogging, or swimming for weight management. Consult a trainer for a suitable plan."
        else:
            return "Focus on low-impact exercises like walking, swimming, or yoga. These are gentle on joints and excellent for blood sugar control."
        
def safe_number(key, product):
    value = product.get(key)
    return float(value) if value is not None else 0.0

# --- صفحات التطبيق (تم تحديث دالة الصفحة الرئيسية) ---

def show_auth_page():
    # وظيفة عرض صفحة المصادقة
    st.title(get_text("auth_title"))

    current_otp_email = st.session_state.get('user_email', "")
    is_otp_sent = st.session_state.get('otp_sent', False)
    
    # 1. Show OTP verification 
    if is_otp_sent:
        with st.container():
            st.subheader(get_text("otp_verification"))
            with st.form(key="verify_otp_form_key_main"):
                st.info(get_text("otp_sent_info").format(current_otp_email))
                token = st.text_input(get_text("enter_otp"), key="otp_token_input_main")
                col_verify, col_resend = st.columns(2)
                
                with col_verify:
                    verify_button = st.form_submit_button(get_text("verify_btn"))
                
                with col_resend:
                    if st.form_submit_button(get_text("cancel_login")): 
                        st.session_state['otp_sent'] = False
                        st.session_state['user_email'] = ""
                        st.rerun() 

                if verify_button and token:
                    verify_otp(current_otp_email, token)
                elif verify_button:
                    st.warning("Please enter the OTP code.")
        return

    # 2. Show standard authentication flow
    st.subheader(get_text("pass_auth_title"))
    
    auth_mode_options = [get_text("mode_login"), get_text("mode_signup"), get_text("mode_forgot")]
    auth_mode = st.radio(get_text("lang_selector"), auth_mode_options, key="password_auth_mode")

    if auth_mode == get_text("mode_login"):
        st.info(get_text("login_info"))
        with st.form(key="login_form_key"):
            email = st.text_input(get_text("email"))
            password = st.text_input(get_text("password"), type="password")
            submit_button = st.form_submit_button(get_text("login_btn"))
            if submit_button and email and password:
                login_user(email, password) 
            elif submit_button:
                st.warning("Please enter both Email and Password.")

    elif auth_mode == get_text("mode_signup"):
        with st.form(key="register_form_key"):
            email = st.text_input(get_text("email"))
            password = st.text_input(f"{get_text('password')} (Min 6 Characters)", type="password")
            confirm_password = st.text_input(get_text("confirm_password"), type="password")
            submit_button = st.form_submit_button(get_text("signup_btn"))
            if submit_button and email and password and confirm_password:
                if password == confirm_password:
                    signup_user(email, password)
                else:
                    st.error("Passwords do not match.")
            elif submit_button:
                st.warning("Please fill in all fields.")
    
    elif auth_mode == get_text("mode_forgot"):
        with st.form(key="forgot_password_form_key"):
            email = st.text_input(get_text("enter_reset_email"))
            submit_button = st.form_submit_button(get_text("send_reset_link"))
            if submit_button and email:
                reset_password(email)
            elif submit_button:
                st.warning("Please enter your Email.")



       
# يجب أن تكون جملة import في بداية ملف app.py بالكامل، خارج أي دالة

def show_home_page():
    # وظيفة عرض الصفحة الرئيسية
    st.title(get_text("welcome_title"))
    
    # 🌟 استخدام اسم الملف المحلي (المسار النسبي) 🌟
    # تأكد من تسمية الصورة بهذا الاسم ووضعها في نفس المجلد
    image_name = "smart_da_logo"
    
    try:
        # عرض صورة Canva الخاصة بك من الملف المحلي
        st.image(image_name, width=400) 
        
    except Exception:
        # هذه الرسالة ستظهر إذا لم يتم العثور على الملف
        st.warning(f"تحذير: لم يتم العثور على الملف '{image_name}'. يرجى التأكد من تسمية الملف ووضعه في نفس مجلد ملف البايثون.")
    
    st.write(get_text("welcome_msg_1"))
    st.write(get_text("welcome_msg_2"))
    
    # قسم تشجيعي
    st.info("💪 ابدأ يومك بنشاط، واشرب كمية كافية من الماء، وتناول طعامًا صحيًا!")
def show_products_page():
    # وظيفة عرض كتالوج المنتجات
    st.title(get_text("products_title"))
    st.image(f"https://placehold.co/600x200/50C878/FFFFFF?text={get_text('products_placeholder')}")
    search_query = st.text_input(get_text("search_product"))
    try:
        query = supabase.table("products").select("*")
        if search_query:
            query = query.like("name", f"%{search_query}%")
        products = query.execute().data
        if products:
            for product in products:
                # نحتاج إلى التعامل مع Suitability (الملائمة) بترجمتها هنا
                suitability_text = get_text("suitability_options")[
                    ["Suitable", "Moderately Suitable", "Not Suitable"].index(product['suitability'])
                ] if product['suitability'] in ["Suitable", "Moderately Suitable", "Not Suitable"] else product['suitability']

                st.subheader(f"{product['name']} - {get_text('suitability')}: {suitability_text}")
                st.image(product['image_url'], width=200)
                st.write(f"**{get_text('calories')}:** {product['calories']}")
                carbs_value = product.get('carbs')
                st.write(f"**{get_text('carbs')}:** {carbs_value if carbs_value is not None else get_text('not_available')}")
                st.write(f"**{get_text('sugar')}:** {product['sugar']}g")
                st.write(f"**{get_text('protein')}:** {product['protein']}g")
                st.write(f"**{get_text('fats')}:** {product['fats']}g")
                st.write("---")
        else:
            st.info(get_text("no_products"))
    except Exception as e:
        st.error(f"Error fetching products: {e}")

def show_admin_page():
    # وظيفة عرض لوحة تحكم المسؤول
    st.title(get_text("admin_title"))
    admin_password = st.text_input(get_text("admin_password"), type="password")
    SECRET_CODE = "Nn1122334455"
    if admin_password == SECRET_CODE:
        show_add_product_form()
        st.markdown("---")
        show_edit_delete_form()
    else:
        st.warning(get_text("admin_denied"))

def show_add_product_form():
    # وظيفة عرض نموذج إضافة منتج
    st.subheader(get_text("add_product_title"))
    with st.form(key="add_product_form_key"):
        product_name = st.text_input(get_text("product_name"))
        calories = st.number_input(get_text("calories"), min_value=0)
        sugar = st.number_input(get_text("sugar"), min_value=0.0)
        carbs = st.number_input(get_text("carbs"), min_value=0.0)
        protein = st.number_input(get_text("protein"), min_value=0.0)
        fats = st.number_input(get_text("fats"), min_value=0.0)
        
        # استخدام الخيارات المترجمة
        suitability_options = get_text("suitability_options")
        suitability = st.selectbox(f"Is this product suitable for diabetics? ({get_text('suitability')})", suitability_options)
        
        uploaded_image = st.file_uploader(get_text("upload_image"), type=["png", "jpg", "jpeg"])
        submit_button = st.form_submit_button(get_text("add_product_btn"))
        if submit_button:
            if uploaded_image and product_name:
                with st.spinner('Adding product...'):
                    image_url = upload_image_to_storage(uploaded_image)
                    if image_url:
                        # نحتاج إلى تخزين القيمة الإنجليزية في قاعدة البيانات لضمان التناسق
                        db_suitability = ["Suitable", "Moderately Suitable", "Not Suitable"][suitability_options.index(suitability)]
                        add_new_product(product_name, calories, sugar, protein, fats, carbs, db_suitability, image_url)
            else:
                st.warning("Please fill in all required fields and upload an image.")

def show_edit_delete_form():
    # وظيفة عرض نموذج تعديل/حذف منتج
    st.subheader(get_text("edit_delete_title"))
    try:
        products = supabase.table("products").select("*").execute().data
        if not products:
            st.info("No products available for editing or deletion.")
            return

        product_names = {product['name']: product for product in products}
        selected_product_name = st.selectbox(get_text("select_product_edit"), list(product_names.keys()))

        if selected_product_name:
            selected_product = product_names[selected_product_name]
            with st.form(key="edit_product_form_key"):
                st.image(selected_product.get('image_url'), width=200)
                
                # Input fields pre-filled with current data
                new_name = st.text_input(get_text("product_name"), value=selected_product['name'])
                new_calories = st.number_input(get_text("calories"), value=selected_product['calories'], min_value=0)
                new_sugar = st.number_input(get_text("sugar"), value=safe_number('sugar', selected_product), min_value=0.0)
                new_carbs = st.number_input(get_text("carbs"), value=safe_number('carbs', selected_product), min_value=0.0)
                new_protein = st.number_input(get_text("protein"), value=safe_number('protein', selected_product), min_value=0.0)
                new_fats = st.number_input(get_text("fats"), value=safe_number('fats', selected_product), min_value=0.0)
                
                # التعامل مع الملائمة (Suitability)
                english_options = ["Suitable", "Moderately Suitable", "Not Suitable"]
                translated_options = get_text("suitability_options")
                
                current_suitability_en = selected_product.get('suitability', english_options[0])
                current_index = english_options.index(current_suitability_en) if current_suitability_en in english_options else 0
                
                new_suitability_translated = st.selectbox(f"Is this product suitable for diabetics? ({get_text('suitability')})", translated_options, index=current_index)
                
                new_image = st.file_uploader(get_text("upload_new_image"), type=["png", "jpg", "jpeg"])

                col1, col2 = st.columns(2)
                with col1: update_button = st.form_submit_button(get_text("update_btn"))
                with col2: delete_button = st.form_submit_button(get_text("delete_btn"))

                if update_button:
                    # تحويل القيمة المترجمة للملائمة مرة أخرى إلى القيمة الإنجليزية للتخزين في قاعدة البيانات
                    db_suitability = english_options[translated_options.index(new_suitability_translated)]
                    
                    image_url_to_update = selected_product.get('image_url')
                    if new_image:
                        with st.spinner('Uploading new image...'):
                            image_url_to_update = upload_image_to_storage(new_image)
                    if image_url_to_update:
                        data_to_update = {"name": new_name, "calories": new_calories, "sugar": new_sugar, "carbs": new_carbs, "protein": new_protein, "fats": new_fats, "suitability": db_suitability, "image_url": image_url_to_update}
                        update_product_in_db(selected_product['id'], data_to_update)

                if delete_button:
                    delete_product_from_db(selected_product['id'])
    except Exception as e:
        st.error(f"Error loading products for edit/delete: {e}")

def show_water_calculator_page():
    # وظيفة عرض صفحة حاسبة الماء
    st.title(get_text("water_calc_title"))
    st.write(get_text("water_calc_msg"))
    st.image(f"https://placehold.co/600x200/ADD8E6/000000?text={get_text('water_placeholder')}")
    with st.expander(get_text("general_advice")):
        st.write(get_text("advice_1"))
        st.write(get_text("advice_2"))
        st.write(get_text("advice_3"))
        st.write(get_text("advice_4"))
    with st.form(key="water_form_key"):
        weight_kg = st.number_input(get_text("weight_kg"), min_value=15.0, value=70.0) 
        age_years = st.number_input(get_text("age_years"), min_value=5, value=30) 
        calculate_button = st.form_submit_button(get_text("calculate_btn"))
    if calculate_button:
        if weight_kg < 15 or age_years < 5:
            st.warning(get_text("reliable_warning"))
        else:
            recommended_liters = calculate_water_intake(weight_kg, age_years)
            st.success(get_text("recommended_intake").format(recommended_liters))


def show_exercise_page():
    # وظيفة عرض توصيات التمارين
    st.title(get_text("exercise_title"))
    st.write(get_text("exercise_msg"))
    st.image(f"https://placehold.co/600x200/98FB98/000000?text={get_text('exercise_placeholder')}")
    with st.form(key="exercise_form_key"):
        age = st.number_input(get_text("age_years"), min_value=5, value=30) 
        weight = st.number_input(get_text("weight_kg"), min_value=15.0, value=70.0) 
        get_rec_button = st.form_submit_button(get_text("get_rec_btn"))
    if get_rec_button:
        if age < 5 or weight < 15:
            st.warning(get_text("reliable_warning"))
        else:
            st.info(get_exercise_recommendation(age, weight))
    with st.expander(get_text("tips_exercise")):
        st.write(get_text("tip_1"))
        st.write(get_text("tip_2"))
        st.write(get_text("tip_3"))
        st.write(get_text("tip_4"))

# --- منطق التنقل ---

def setup_navigation():
    # وظيفة إعداد شريط التنقل الجانبي
    
    # محدد اللغة (Language Selector)
    lang_map = {"العربية": "ar", "English": "en"}
    current_lang_display = "العربية" if st.session_state['language'] == 'ar' else "English"
    
    st.sidebar.subheader(get_text("lang_selector"))
    selected_lang_display = st.sidebar.radio(
        get_text("lang_selector"), 
        list(lang_map.keys()), 
        index=list(lang_map.keys()).index(current_lang_display),
        key="lang_radio"
    )
    
    # تحديث حالة الجلسة باللغة الجديدة وإعادة تشغيل التطبيق لعرض التغييرات
    if lang_map[selected_lang_display] != st.session_state['language']:
        st.session_state['language'] = lang_map[selected_lang_display]
        st.rerun()

    # Define mapping from internal key (English) to translated display name
    page_map_keys = {
        "Home": get_text("home_page"),
        "Products": get_text("products_catalog"), 
        "Admin": get_text("admin_dashboard"), 
        "Water Calculator": get_text("water_calculator"), 
        "Exercise": get_text("exercise_recs")
    }
    
    # Define mapping from translated display name back to internal key
    display_to_key = {v: k for k, v in page_map_keys.items()}
    display_names = list(page_map_keys.values())

    st.sidebar.title(get_text("navigation"))
    st.sidebar.button(get_text("logout"), on_click=logout_user)
    
    # Get current page name for radio default selection
    current_page_name = page_map_keys.get(st.session_state['page'], page_map_keys["Home"])
    initial_index = display_names.index(current_page_name) if current_page_name in display_names else 0

    selected_display_name = st.sidebar.radio(get_text("navigation"), display_names, index=initial_index)
    
    # Update session state with the internal key and execute function
    selected_key = display_to_key.get(selected_display_name, "Home")
    st.session_state['page'] = selected_key
    
    # Execute the selected page function
    page_functions = {
        "Home": show_home_page,
        "Products": show_products_page,
        "Admin": show_admin_page,
        "Water Calculator": show_water_calculator_page,
        "Exercise": show_exercise_page
    }
    page_functions[selected_key]()

# --- تنفيذ التطبيق الرئيسي ---

if st.session_state['user']:
    setup_navigation()
else:
    # يجب إظهار محدد اللغة في صفحة المصادقة أيضًا
    lang_map = {"العربية": "ar", "English": "en"}
    current_lang_display = "العربية" if st.session_state['language'] == 'ar' else "English"
    
    st.sidebar.subheader(get_text("lang_selector"))
    selected_lang_display = st.sidebar.radio(
        get_text("lang_selector"), 
        list(lang_map.keys()), 
        index=list(lang_map.keys()).index(current_lang_display),
        key="lang_radio_auth"
    )
    
    if lang_map[selected_lang_display] != st.session_state['language']:
        st.session_state['language'] = lang_map[selected_lang_display]
        st.rerun()
        
    show_auth_page()


















