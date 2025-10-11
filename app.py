import streamlit as st
import os
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv

# --- إعدادات الصفحة (يجب أن يكون هذا أول استدعاء لـ Streamlit) ---
st.set_page_config(
    page_title="SMART DA .COM", # الاسم الجديد في شريط المتصفح
    page_icon="🩺", # تم تغيير الشعار إلى إيموجي طبي (لتأكيد عمل الدالة)
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

# --- التهيئة العامة ---
supabase = init_supabase_client()
init_session_state()

# --- وظائف المصادقة ---

def signup_user(email, password):
    # وظيفة تسجيل مستخدم جديد
    if not supabase: return
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            # تمت إزالة تسجيل الدخول التلقائي. يجب على المستخدم الآن استخدام خانة 'Login'
            # st.session_state['user'] = response.user 
            # st.session_state['page'] = 'Home'
            st.success("Registration successful! Please use the 'Login' option to proceed with verification and access the application.")
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

# --- وظائف إدارة المنتجات والملفات ---

def upload_image_to_storage(image_file):
    # وظيفة رفع صورة إلى مساحة التخزين
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
    # وظيفة إضافة منتج جديد إلى قاعدة البيانات
    if not supabase: return
    try:
        supabase.table("products").insert({"name": name, "calories": calories, "sugar": sugar, "protein": protein, "fats": fats, "carbs": carbs, "suitability": suitability, "image_url": image_url}).execute()
        st.success("Product added successfully!")
    except Exception as e:
        st.error(f"Failed to add product: {e}")

def update_product_in_db(product_id, data_to_update):
    # وظيفة تحديث بيانات منتج
    if not supabase: return
    try:
        supabase.table("products").update(data_to_update).eq("id", product_id).execute()
        st.success("Product updated successfully!")
    except Exception as e:
        st.error(f"Failed to update product: {e}")

def delete_product_from_db(product_id):
    # وظيفة حذف منتج من قاعدة البيانات
    if not supabase: return
    try:
        supabase.table("products").delete().eq("id", product_id).execute()
        st.success("Product deleted successfully!")
    except Exception as e:
        st.error(f"Failed to delete product: {e}")

# --- وظائف مساعدة ---

def calculate_water_intake(weight_kg, age_years):
    # وظيفة حساب كمية الماء الموصى بها
    if weight_kg <= 15 or age_years <= 5: return 0 
    if 18 <= age_years <= 30: recommended_ml = weight_kg * 35
    elif 31 <= age_years <= 55: recommended_ml = weight_kg * 30
    else: recommended_ml = weight_kg * 25
    return recommended_ml / 1000

def get_exercise_recommendation(age, weight):
    # وظيفة تقديم توصيات التمارين
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
    # وظيفة تحويل قيمة المنتج إلى رقم عشري آمن
    value = product.get(key)
    return float(value) if value is not None else 0.0

# --- صفحات التطبيق ---

def show_auth_page():
    # وظيفة عرض صفحة المصادقة
    st.title("Login and Authentication")

    current_otp_email = st.session_state.get('user_email', "")
    is_otp_sent = st.session_state.get('otp_sent', False)
    
    # 1. Show OTP verification if a code has been sent (Mandatory after password)
    if is_otp_sent:
        with st.container():
            st.subheader("One-Time Password (OTP) Verification")
            with st.form(key="verify_otp_form_key_main"):
                st.info(f"An OTP code has been sent to **{current_otp_email}**. Please enter it below to complete login.")
                token = st.text_input("Enter OTP Code from your Email", key="otp_token_input_main")
                col_verify, col_resend = st.columns(2)
                
                with col_verify:
                    verify_button = st.form_submit_button("Verify Code")
                
                with col_resend:
                    if st.form_submit_button("Cancel Login"): 
                        st.session_state['otp_sent'] = False
                        st.session_state['user_email'] = ""
                        st.rerun() 

                if verify_button and token:
                    verify_otp(current_otp_email, token)
                elif verify_button:
                    st.warning("Please enter the OTP code.")
        return

    # 2. Show standard authentication flow (Password-based only)
    st.subheader("Password Authentication")
    
    # Note: We enforce the flow: Password -> OTP, so we only need one set of options here.
    auth_mode = st.radio("Select Mode", ["Login (Email & Password Required)", "Signup", "Forgot Password?"], key="password_auth_mode")

    if auth_mode == "Login (Email & Password Required)":
        st.info("Note: Successful login requires the **correct password** followed by **OTP verification**.")
        with st.form(key="login_form_key"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            if submit_button and email and password:
                login_user(email, password) 
            elif submit_button:
                st.warning("Please enter both Email and Password.")

    elif auth_mode == "Signup":
        with st.form(key="register_form_key"):
            email = st.text_input("Email")
            password = st.text_input("Password (Min 6 Characters)", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit_button = st.form_submit_button("Signup")
            if submit_button and email and password and confirm_password:
                if password == confirm_password:
                    signup_user(email, password)
                else:
                    st.error("Passwords do not match.")
            elif submit_button:
                st.warning("Please fill in all fields.")
    
    elif auth_mode == "Forgot Password?":
        with st.form(key="forgot_password_form_key"):
            email = st.text_input("Enter your Email to receive a password reset link")
            submit_button = st.form_submit_button("Send Reset Link")
            if submit_button and email:
                reset_password(email)
            elif submit_button:
                st.warning("Please enter your Email.")


def show_home_page():
    # وظيفة عرض الصفحة الرئيسية
    st.title("Welcome to the Smart Diabetes Assistant")
    st.write("This application is designed to help you manage your health and diet.")
    st.write("Use the navigation menu to explore the different features.")

def show_products_page():
    # وظيفة عرض كتالوج المنتجات
    st.title("Product Catalog")
    st.image("https://placehold.co/600x200/50C878/FFFFFF?text=Healthy+Foods")
    search_query = st.text_input("Search for a product...")
    try:
        query = supabase.table("products").select("*")
        if search_query:
            query = query.like("name", f"%{search_query}%")
        products = query.execute().data
        if products:
            for product in products:
                st.subheader(f"{product['name']} - Suitability: {product['suitability']}")
                st.image(product['image_url'], width=200)
                st.write(f"**Calories:** {product['calories']}")
                carbs_value = product.get('carbs')
                st.write(f"**Carbs (g):** {carbs_value if carbs_value is not None else 'N/A'}")
                st.write(f"**Sugar:** {product['sugar']}g")
                st.write(f"**Protein:** {product['protein']}g")
                st.write(f"**Fats:** {product['fats']}g")
                st.write("---")
        else:
            st.info("No products found.")
    except Exception as e:
        st.error(f"Error fetching products: {e}")

def show_admin_page():
    # وظيفة عرض لوحة تحكم المسؤول
    st.title("Admin Dashboard")
    admin_password = st.text_input("Enter Admin Password", type="password")
    SECRET_CODE = "Nn1122334455"
    if admin_password == SECRET_CODE:
        show_add_product_form()
        st.markdown("---")
        show_edit_delete_form()
    else:
        st.warning("Incorrect password. Access denied.")

def show_add_product_form():
    # وظيفة عرض نموذج إضافة منتج
    st.subheader("Add New Product")
    with st.form(key="add_product_form_key"):
        product_name = st.text_input("Product Name")
        calories = st.number_input("Calories", min_value=0)
        sugar = st.number_input("Sugar (g)", min_value=0.0)
        carbs = st.number_input("Carbs (g)", min_value=0.0)
        protein = st.number_input("Protein (g)", min_value=0.0)
        fats = st.number_input("Fats (g)", min_value=0.0)
        suitability = st.selectbox("Is this product suitable for diabetics?", ("Suitable", "Moderately Suitable", "Not Suitable"))
        uploaded_image = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"])
        submit_button = st.form_submit_button("Add Product")
        if submit_button:
            if uploaded_image and product_name:
                with st.spinner('Adding product...'):
                    image_url = upload_image_to_storage(uploaded_image)
                    if image_url:
                        add_new_product(product_name, calories, sugar, protein, fats, carbs, suitability, image_url)
            else:
                st.warning("Please fill in all required fields and upload an image.")

def show_edit_delete_form():
    # وظيفة عرض نموذج تعديل/حذف منتج
    st.subheader("Edit or Delete Existing Product")
    try:
        products = supabase.table("products").select("*").execute().data
        if not products:
            st.info("No products available for editing or deletion.")
            return

        product_names = {product['name']: product for product in products}
        selected_product_name = st.selectbox("Select a product to edit", list(product_names.keys()))

        if selected_product_name:
            selected_product = product_names[selected_product_name]
            with st.form(key="edit_product_form_key"):
                st.image(selected_product.get('image_url'), width=200)
                
                # Input fields pre-filled with current data
                new_name = st.text_input("Product Name", value=selected_product['name'])
                new_calories = st.number_input("Calories", value=selected_product['calories'], min_value=0)
                new_sugar = st.number_input("Sugar (g)", value=safe_number('sugar', selected_product), min_value=0.0)
                new_carbs = st.number_input("Carbs (g)", value=safe_number('carbs', selected_product), min_value=0.0)
                new_protein = st.number_input("Protein (g)", value=safe_number('protein', selected_product), min_value=0.0)
                new_fats = st.number_input("Fats (g)", value=safe_number('fats', selected_product), min_value=0.0)
                
                suitability_options = ("Suitable", "Moderately Suitable", "Not Suitable")
                current_suitability = selected_product.get('suitability', suitability_options[0])
                new_suitability = st.selectbox("Is this product suitable for diabetics?", suitability_options, index=suitability_options.index(current_suitability))
                new_image = st.file_uploader("Upload New Image (Optional)", type=["png", "jpg", "jpeg"])

                col1, col2 = st.columns(2)
                with col1: update_button = st.form_submit_button("Update Product")
                with col2: delete_button = st.form_submit_button("Delete Product")

                if update_button:
                    image_url_to_update = selected_product.get('image_url')
                    if new_image:
                        with st.spinner('Uploading new image...'):
                            image_url_to_update = upload_image_to_storage(new_image)
                    if image_url_to_update:
                        data_to_update = {"name": new_name, "calories": new_calories, "sugar": new_sugar, "carbs": new_carbs, "protein": new_protein, "fats": new_fats, "suitability": new_suitability, "image_url": image_url_to_update}
                        update_product_in_db(selected_product['id'], data_to_update)

                if delete_button:
                    delete_product_from_db(selected_product['id'])
    except Exception as e:
        st.error(f"Error loading products for edit/delete: {e}")

def show_water_calculator_page():
    # وظيفة عرض صفحة حاسبة الماء
    st.title("Water Intake Calculator")
    st.write("Calculate your recommended daily water intake based on your weight and age.")
    st.image("https://placehold.co/600x200/ADD8E6/000000?text=Stay+Hydrated")
    with st.expander("General Advice for Diabetics"):
        st.write("- **Balanced Diet:** Focus on whole foods, fruits, vegetables, and lean proteins.")
        st.write("- **Regular Exercise:** Aim for at least 30 minutes of moderate exercise most days of the week.")
        st.write("- **Monitor Blood Sugar:** Check your blood sugar levels regularly as advised by your doctor.")
        st.write("- **Stay Hydrated:** Drinking enough water helps manage blood sugar levels.")
    with st.form(key="water_form_key"):
        weight_kg = st.number_input("Your Weight (kg)", min_value=15.0, value=70.0) 
        age_years = st.number_input("Your Age (years)", min_value=5, value=30) 
        calculate_button = st.form_submit_button("Calculate")
    if calculate_button:
        if weight_kg < 15 or age_years < 5:
            st.warning("Please enter a realistic weight and age (over 15 kg and 5 years) for a reliable recommendation.")
        else:
            recommended_liters = calculate_water_intake(weight_kg, age_years)
            st.success(f"Your recommended daily water intake is **{recommended_liters:.2f} liters**.")


def show_exercise_page():
    # وظيفة عرض توصيات التمارين
    st.title("Exercise Recommendations")
    st.write("Find a suitable exercise based on your age and weight.")
    st.image("https://placehold.co/600x200/98FB98/000000?text=Exercise+and+Health")
    with st.form(key="exercise_form_key"):
        age = st.number_input("Your Age (years)", min_value=5, value=30) 
        weight = st.number_input("Your Weight (kg)", min_value=15.0, value=70.0) 
        get_rec_button = st.form_submit_button("Get Recommendation")
    if get_rec_button:
        if age < 5 or weight < 15:
            st.warning("Please enter a realistic age and weight (over 5 years and 15 kg) for a reliable recommendation.")
        else:
            st.info(get_exercise_recommendation(age, weight))
    with st.expander("Tips for Exercising with Diabetes"):
        st.write("- **Consult a Doctor:** Always talk to your doctor before starting any new exercise program.")
        st.write("- **Check Blood Sugar:** Test your blood sugar before and after exercise to know how your body responds.")
        st.write("- **Stay Hydrated:** Drink plenty of water before, during, and after your workout.")
        st.write("- **Carry a Snack:** Keep a fast-acting source of glucose with you in case of a sudden sugar drop.")

# --- منطق التنقل ---

def setup_navigation():
    # وظيفة إعداد شريط التنقل الجانبي
    # Define mapping from internal key (English) to function and English display name
    page_map = {
        "Home": {"func": show_home_page, "name": "Home Page"}, 
        "Products": {"func": show_products_page, "name": "Product Catalog"}, 
        "Admin": {"func": show_admin_page, "name": "Admin Dashboard"}, 
        "Water Calculator": {"func": show_water_calculator_page, "name": "Water Calculator"}, 
        "Exercise": {"func": show_exercise_page, "name": "Exercise Recommendations"}
    }
    
    # Get all display names and map them back to internal keys
    display_names = [data["name"] for data in page_map.values()]
    name_to_key = {data["name"]: key for key, data in page_map.items()}
    
    st.sidebar.title("Navigation")
    st.sidebar.button("Logout", on_click=logout_user)
    
    # Get current page name for radio default selection
    current_page_name = page_map.get(st.session_state['page'], page_map["Home"])["name"]
    initial_index = display_names.index(current_page_name) if current_page_name in display_names else 0

    selected_display_name = st.sidebar.radio("Go to", display_names, index=initial_index)
    
    # Update session state with the internal key and execute function
    selected_key = name_to_key.get(selected_display_name, "Home")
    st.session_state['page'] = selected_key
    
    page_map[selected_key]["func"]()

# --- تنفيذ التطبيق الرئيسي ---

if st.session_state['user']:
    setup_navigation()
else:
    show_auth_page()




