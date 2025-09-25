import streamlit as st
import bcrypt
import os
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv

# --- إعداد البيئة والاتصال بـ Supabase ---
load_dotenv()
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    st.error("Error: Supabase environment variables are not set. Please check your .env file.")
    supabase = None
else:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Error connecting to Supabase: {e}")
        supabase = None

# تهيئة حالة الجلسة للمستخدم
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'otp_sent' not in st.session_state:
    st.session_state['otp_sent'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ""
if 'page' not in st.session_state:
    st.session_state['page'] = 'Home'

# --- دوال المصادقة (Auth Functions) ---

def send_otp(email):
    if not supabase: return
    try:
        supabase.auth.sign_in_with_otp({"email": email})
        st.session_state['otp_sent'] = True
        st.session_state['user_email'] = email
        st.success("OTP has been sent to your email. Please check your inbox.")
    except Exception as e:
        st.error(f"Error sending OTP: {e}")

def verify_otp(email, token):
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
            st.error("Invalid OTP. Please try again.")
    except Exception as e:
        st.error(f"Error verifying OTP: {e}")

def logout_user():
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

# --- دوال إدارة المنتجات ---

def upload_image_to_storage(image_file):
    if not supabase: return None
    try:
        file_name = f"products/{uuid.uuid4()}-{image_file.name}"
        supabase.storage.from_("product-images").upload(file_name, image_file.getvalue())
        return supabase.storage.from_("product-images").get_public_url(file_name)
    except Exception as e:
        st.error(f"Failed to upload image: {e}")
        return None

def add_new_product(name, calories, sugar, protein, fats, suitability, image_url):
    if not supabase: return
    try:
        supabase.table("products").insert({"name": name, "calories": calories, "sugar": sugar, "protein": protein, "fats": fats, "suitability": suitability, "image_url": image_url}).execute()
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

# --- دوال حاسبة المياه (Water Calculator Functions) ---

def calculate_water_intake(weight_kg, age_years):
    if 18 <= age_years <= 30:
        recommended_ml = weight_kg * 35
    elif 31 <= age_years <= 55:
        recommended_ml = weight_kg * 30
    else:
        recommended_ml = weight_kg * 25
    return recommended_ml / 1000

# --- دوال صفحة الرياضة ---
def get_exercise_recommendation(age, weight):
    if age < 18:
        return "You are in a great age for physical activity! Focus on playful activities like running, swimming, or team sports."
    elif age <= 40:
        if weight < 70:
            return "Good weight for your age! Try to maintain it with activities like running, cycling, and weight training."
        else:
            return "Consider moderate-intensity cardio like brisk walking, jogging, or swimming to manage weight. Consult a trainer for a suitable plan."
    else:
        return "Focus on low-impact exercises like walking, swimming, or yoga. These activities are gentle on joints and great for blood sugar control."

# --- صفحات التطبيق (App Pages) ---

def show_auth_page():
    st.title("Login or Register")
    if not st.session_state['otp_sent']:
        with st.form(key="send_otp_form_key"):
            email = st.text_input("Enter your email to receive a login code")
            submit_button = st.form_submit_button("Send Code")
            if submit_button and email:
                send_otp(email)
            elif submit_button:
                st.warning("Please enter your email.")
    else:
        with st.form(key="verify_otp_form_key"):
            st.write(f"A code has been sent to {st.session_state['user_email']}")
            token = st.text_input("Enter the code from your email")
            submit_button = st.form_submit_button("Verify Code")
            if submit_button and token:
                verify_otp(st.session_state['user_email'], token)
            elif submit_button:
                st.warning("Please enter the code.")

def show_home_page():
    st.title("Welcome to the Smart Diabetes Assistent")
    st.write("This app is designed to help you manage your health.")
    st.write("Use the navigation menu to explore different features.")

def show_products_page():
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
                st.write(f"**Sugar:** {product['sugar']}g")
                st.write(f"**Protein:** {product['protein']}g")
                st.write(f"**Fats:** {product['fats']}g")
                st.write("---")
        else:
            st.info("No products found.")
    except Exception as e:
        st.error(f"Error fetching products: {e}")

def show_admin_page():
    st.title("Admin Dashboard")
    admin_password = st.text_input("Enter Admin Password", type="password")
    SECRET_CODE = "admin123"
    if admin_password == SECRET_CODE:
        show_add_product_form()
        st.markdown("---")
        show_edit_delete_form()
    else:
        st.warning("Incorrect password. Access denied.")

def show_add_product_form():
    st.subheader("Add a New Product")
    with st.form(key="add_product_form_key"):
        product_name = st.text_input("Product Name")
        calories = st.number_input("Calories", min_value=0)
        sugar = st.number_input("Sugar (g)", min_value=0.0)
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
                        add_new_product(product_name, calories, sugar, protein, fats, suitability, image_url)
            else:
                st.warning("Please fill in all required fields and upload an image.")

def show_edit_delete_form():
    st.subheader("Edit or Delete Existing Product")
    try:
        products = supabase.table("products").select("*").execute().data
        if products:
            product_names = {product['name']: product for product in products}
            selected_product_name = st.selectbox("Select a product to edit", list(product_names.keys()))
            selected_product = product_names[selected_product_name]
            with st.form(key="edit_product_form_key"):
                st.image(selected_product['image_url'], width=200)
                new_name = st.text_input("Product Name", value=selected_product['name'])
                new_calories = st.number_input("Calories", value=selected_product['calories'], min_value=0)
                new_sugar = st.number_input("Sugar (g)", value=float(selected_product['sugar']), min_value=0.0)
                new_protein = st.number_input("Protein (g)", value=float(selected_product['protein']), min_value=0.0)
                new_fats = st.number_input("Fats (g)", value=float(selected_product['fats']), min_value=0.0)
                
                suitability_options = ("Suitable", "Moderately Suitable", "Not Suitable")
                try:
                    current_suitability_index = suitability_options.index(selected_product['suitability'])
                except ValueError:
                    # Handle case where value from DB is not in options
                    current_suitability_index = 0
                
                new_suitability = st.selectbox("Is this product suitable for diabetics?", suitability_options, index=current_suitability_index)
                new_image = st.file_uploader("Upload new image (optional)", type=["png", "jpg", "jpeg"])
                
                col1, col2 = st.columns(2)
                with col1:
                    update_button = st.form_submit_button("Update Product")
                with col2:
                    delete_button = st.form_submit_button("Delete Product")
                
                if update_button:
                    image_url_to_update = selected_product['image_url']
                    if new_image:
                        with st.spinner('Uploading new image...'):
                            image_url_to_update = upload_image_to_storage(new_image)
                    if image_url_to_update:
                        data_to_update = {"name": new_name, "calories": new_calories, "sugar": new_sugar, "protein": new_protein, "fats": new_fats, "suitability": new_suitability}
                        if new_image: data_to_update["image_url"] = image_url_to_update
                        update_product_in_db(selected_product['id'], data_to_update)
                
                if delete_button:
                    delete_product_from_db(selected_product['id'])
        else:
            st.info("No products available to edit or delete.")
    except Exception as e:
        st.error(f"Error loading products for edit/delete: {e}")

def show_water_calculator_page():
    st.title("Water Intake Calculator")
    st.write("Calculate your recommended daily water intake based on your weight and age.")
    st.image("https://placehold.co/600x200/ADD8E6/000000?text=Stay+Hydrated")
    with st.expander("General Tips for Diabetics"):
        st.write("- **Balanced Diet:** Focus on whole foods, fruits, vegetables, and lean proteins.")
        st.write("- **Regular Exercise:** Aim for at least 30 minutes of moderate exercise most days of the week.")
        st.write("- **Monitor Blood Sugar:** Check your blood sugar levels regularly as advised by your doctor.")
        st.write("- **Stay Hydrated:** Drinking enough water helps manage blood sugar levels.")
    with st.form(key="water_form_key"):
        weight_kg = st.number_input("Your Weight (in kg)", min_value=1.0)
        age_years = st.number_input("Your Age (in years)", min_value=1)
        calculate_button = st.form_submit_button("Calculate")
    if calculate_button:
        if weight_kg and age_years:
            recommended_liters = calculate_water_intake(weight_kg, age_years)
            st.success(f"Your recommended daily water intake is **{recommended_liters:.2f} liters**.")
        else:
            st.warning("Please enter your weight and age.")

def show_exercise_page():
    st.title("Exercise Recommendations")
    st.write("Find a sport that's suitable for you based on your age and weight.")
    st.image("https://placehold.co/600x200/98FB98/000000?text=Exercise+and+Health")
    with st.form(key="exercise_form_key"):
        age = st.number_input("Your Age (in years)", min_value=1)
        weight = st.number_input("Your Weight (in kg)", min_value=1.0)
        get_rec_button = st.form_submit_button("Get Recommendation")
    if get_rec_button:
        if age and weight:
            st.info(get_exercise_recommendation(age, weight))
        else:
            st.warning("Please enter your age and weight.")
    with st.expander("Tips on Exercising with Diabetes"):
        st.write("- **Consult a Doctor:** Always talk to your doctor before starting a new exercise program.")
        st.write("- **Check Blood Sugar:** Check your blood sugar before and after exercise to see how your body responds.")
        st.write("- **Stay Hydrated:** Drink plenty of water before, during, and after your workout.")
        st.write("- **Carry a Snack:** Keep a quick source of glucose with you in case of a low blood sugar episode.")

# --- منطق التنقل الرئيسي ---
st.sidebar.title("Navigation")
if st.session_state['user']:
    st.sidebar.button("Logout", on_click=logout_user)
    page_options = {"Home": show_home_page, "Products": show_products_page, "Admin": show_admin_page, "Water Calculator": show_water_calculator_page, "Exercise": show_exercise_page}
    page_name = st.sidebar.radio("Go to", list(page_options.keys()), index=list(page_options.keys()).index(st.session_state['page']))
    st.session_state['page'] = page_name
    page_options[page_name]()
else:
    show_auth_page()

