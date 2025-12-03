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
        'forgot_password_button': "نسيت كلمة المرور؟",

        'enter_email_password_warning': "الرجاء إدخال البريد الإلكتروني وكلمة المرور.",
        'password_length_error': "خطأ: كلمة المرور يجب أن تكون 6 أحرف على الأقل.",

        'signup_success': "تم التسجيل بنجاح! يرجى الآن تسجيل الدخول (سيُطلب منك رمز تحقق).",
        'signup_error': "خطأ في التسجيل:",

        'verification_success': "تم تسجيل الدخول بنجاح! لقد سجلت دخولك الآن.",
        'login_invalid': "بيانات تسجيل الدخول غير صحيحة. يرجى التحقق من البريد الإلكتروني وكلمة المرور.",
        'verification_error': "خطأ في تسجيل الدخول:",

        'enter_email_for_reset': "أدخل بريدك الإلكتروني لإعادة تعيين كلمة المرور",
        'send_reset_link_button': "إرسال رابط إعادة التعيين",
        'password_reset_sent': "تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني. **يجب تفعيل رابط التأكيد في إعدادات Supabase/Auth/Email Templates.**",
        'password_reset_error': "خطأ في إعادة تعيين كلمة المرور:",

        # مفاتيح OTP الجديدة
        'verify_otp_title': "التحقق بخطوتين (OTP)",
        'otp_sent_info': "تم إرسال رمز تحقق مكون من 6 أرقام إلى بريدك الإلكتروني. يرجى التحقق من صندوق الوارد (وقد تجده في البريد غير الهام).",
        'enter_otp': "أدخل رمز التحقق (OTP)",
        'verify_otp_button': "تحقق من الرمز",
        'otp_invalid': "رمز التحقق غير صحيح أو انتهت صلاحيته.",
        'otp_error': "خطأ في التحقق من الرمز:",

        # **مفاتيح تغيير كلمة المرور الجديدة**
        'change_password_title': "تغيير كلمة المرور",
        'new_password_label': "كلمة المرور الجديدة (6 أحرف أو أكثر)",
        'change_password_button': "تأكيد تغيير كلمة المرور",
        'password_change_success': "تم تحديث كلمة المرور بنجاح! سيتم تسجيل خروجك الآن.",
        'password_change_error': "خطأ في تغيير كلمة المرور:",
        'password_update_form': "تغيير كلمة المرور", # للتنقل
        
        # مفاتيح عامة
        'logout': "تسجيل الخروج",
        'logged_out': "تم تسجيل خروجك.",
@@ -163,6 +171,14 @@
        'otp_invalid': "Invalid or expired OTP code.",
        'otp_error': "OTP Verification Error:",

        # **New Password Change Keys**
        'change_password_title': "Change Password",
        'new_password_label': "New Password (6 characters or more)",
        'change_password_button': "Confirm Password Change",
        'password_change_success': "Password updated successfully! You will be logged out now.",
        'password_change_error': "Error changing password:",
        'password_update_form': "Change Password", # For navigation
        
        # General Keys
        'logout': "Logout",
        'logged_out': "You have been logged out.",
@@ -336,7 +352,7 @@
    except Exception as e:
        error_message = str(e)
        # محاولة تحديد إذا كان الخطأ متعلقاً ببيانات الاعتماد
        if "Invalid login credentials" in error_message or "Invalid login credentials" in error_message or "AuthApiError" in error_message:
        if "Invalid login credentials" in error_message or "AuthApiError" in error_message:
             st.error(t('login_invalid'))
        else:
            st.error(f"{t('verification_error')} {e}")
@@ -365,19 +381,37 @@
            st.error(f"{t('otp_error')} {e}")

def reset_password(email):
    """إرسال رابط إعادة تعيين كلمة المرور. (التحقق من الإعدادات الخارجية مهم جداً)"""
    """إرسال رابط إعادة تعيين كلمة المرور."""
    if not supabase: return
    try:
        # استخدام الدالة الصحيحة لإرسال رابط إعادة التعيين
        # **ملاحظة هامة:** لكي تعمل هذه الخاصية، يجب عليك:
        # 1. الذهاب إلى Supabase -> Authentication -> Email Templates.
        # 2. التأكد من تفعيل قالب "Password Recovery" وتحديد "Confirmation URL" صحيح.
        supabase.auth.reset_password_for_email(email)
        st.success(t('password_reset_sent'))
        st.session_state['auth_mode'] = 'login' # العودة لنموذج الدخول بعد الإرسال
    except Exception as e:
        st.error(f"{t('password_reset_error')} {e}")

# **الدالة الجديدة لتغيير كلمة المرور للمستخدم المسجل دخوله**
def update_password_function(new_password):
    """
    تغيير كلمة المرور للمستخدم المسجل دخوله حالياً باستخدام update_user.
    """
    if not supabase: return
    try:
        # استخدام update_user مع مفتاح 'password'
        response = supabase.auth.update_user({"password": new_password})
        
        if response.user:
            st.success(t('password_change_success'))
            # Supabase يوصي بتسجيل الخروج بعد تحديث كلمة المرور لأسباب أمنية
            logout_user() 
        else:
            st.error(t('password_change_error') + " No response data.")
            
    except Exception as e:
        st.error(f"{t('password_change_error')} {e}")


def logout_user():
    """تسجيل خروج المستخدم ومسح حالة الجلسة."""
    if not supabase: return
@@ -577,6 +611,34 @@

    st.write(t('app_purpose'))
    st.write(t('explore_features'))
    
# **الدالة الجديدة لعرض نموذج تغيير كلمة المرور**
def show_password_change_form():
    """عرض نموذج لتغيير كلمة المرور للمستخدم المسجل دخوله."""
    st.title(t('change_password_title'))
    
    if not st.session_state['user']:
        st.warning("You must be logged in to change your password.")
        return

    with st.form(key="password_change_form_key"):
        st.subheader(t('password_update_form'))
        
        # لا نحتاج لكلمة المرور القديمة هنا، Supabase يتطلب فقط أن يكون المستخدم مسجلاً الدخول (جزء من الجلسة)
        new_password = st.text_input(t('new_password_label'), 
                                     type='password', 
                                     key='new_password_input')
        
        submit_button = st.form_submit_button(t('change_password_button'))
        
        if submit_button:
            if new_password and len(new_password) >= 6:
                update_password_function(new_password)
            elif new_password:
                st.error(t('password_length_error'))
            else:
                st.warning(t('enter_email_password_warning'))


def show_products_page():
    st.title(t('products_page'))
@@ -669,196 +731,205 @@
                suitability_options_keys = ['suitable', 'moderately_suitable', 'not_suitable']
                suitability_options_translated = [t(key) for key in suitability_options_keys]

                with st.form(key="edit_product_form_key"):
                    st.image(selected_product.get('image_url', 'https://placehold.co/200x200'), width=200) 
                # تحديد القيمة الافتراضية المترجمة بناءً على المفتاح المخزن
                current_suitability_key = selected_product.get('suitability', 'not_suitable')
                try:
                    default_index = suitability_options_keys.index(current_suitability_key)
                except ValueError:
                    default_index = 0
                
                with st.form(key=f"edit_product_form_{selected_product['id']}"):
                    product_name = st.text_input(t('product_name'), value=selected_product['name'], key='edit_name')
                    calories = st.number_input(t('calories'), value=selected_product['calories'], min_value=0, key='edit_calories')
                    sugar = st.number_input(t('sugar_g'), value=selected_product['sugar'], min_value=0.0, key='edit_sugar')
                    carbs = st.number_input(t('carbs_g'), value=selected_product['carbs'], min_value=0.0, key='edit_carbs')
                    protein = st.number_input(t('protein_g'), value=selected_product['protein'], min_value=0.0, key='edit_protein')
                    fats = st.number_input(t('fats_g'), value=selected_product['fats'], min_value=0.0, key='edit_fats')

                    new_name = st.text_input(t('product_name'), value=selected_product['name'])
                    new_calories = st.number_input(t('calories'), value=selected_product['calories'], min_value=0)

                    def safe_number(key, product):
                        value = product.get(key)
                        return float(value) if value is not None else 0.0

                    new_sugar = st.number_input(t('sugar_g'), value=safe_number('sugar', selected_product), min_value=0.0)
                    new_carbs = st.number_input(t('carbs_g'), value=safe_number('carbs', selected_product), min_value=0.0)
                    new_protein = st.number_input(t('protein_g'), value=safe_number('protein', selected_product), min_value=0.0)
                    new_fats = st.number_input(t('fats_g'), value=safe_number('fats', selected_product), min_value=0.0)
                    # حقل الملائمة مع القيمة الافتراضية المترجمة
                    suitability_translated = st.selectbox(
                        t('suitability_question'), 
                        options=suitability_options_translated, 
                        index=default_index, 
                        key='edit_suitability'
                    )

                    # تحديد القيمة الافتراضية المترجمة (القيمة المخزنة هي المفتاح الإنجليزي)
                    db_suitability_key = selected_product['suitability'] if selected_product['suitability'] in suitability_options_keys else suitability_options_keys[0]
                    current_translated_value = t(db_suitability_key)
                    st.image(selected_product['image_url'], width=100)
                    uploaded_image = st.file_uploader(t('upload_new_image'), type=["png", "jpg", "jpeg"], key='edit_image_upload')

                    # تحديد الفهرس للـ selectbox
                    current_index = suitability_options_translated.index(current_translated_value)

                    new_suitability_translated = st.selectbox(t('suitability_question'), suitability_options_translated, index=current_index)
                    new_image = st.file_uploader(t('upload_new_image'), type=["png", "jpg", "jpeg"])

                    col1, col2 = st.columns(2)
                    with col1:
                        update_button = st.form_submit_button(t('update_product'))
                    with col2:
                        delete_button = st.form_submit_button(t('delete_product'))

                    update_button = col1.form_submit_button(t('update_product'))
                    delete_button = col2.form_submit_button(t('delete_product'))
                    
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
                        if product_name:
                            data_to_update = {
                                "name": product_name,
                                "calories": calories,
                                "sugar": sugar,
                                "protein": protein,
                                "fats": fats,
                                "carbs": carbs,
                                # نحول القيمة المترجمة إلى المفتاح الإنجليزي للحفظ في قاعدة البيانات
                                "suitability": suitability_options_keys[suitability_options_translated.index(suitability_translated)]
                            }
                            
                            # معالجة رفع الصورة الجديدة
                            if uploaded_image:
                                with st.spinner(t('updating_image_spinner')):
                                    new_image_url = upload_image_to_storage(uploaded_image)
                                    if new_image_url:
                                        data_to_update["image_url"] = new_image_url
                            
                            update_product_in_db(selected_product['id'], data_to_update)
                            st.rerun()
                        else:
                            st.warning(t('fill_all_fields'))

                        update_product_in_db(selected_product['id'], data_to_update)
                        st.rerun()

                    if delete_button:
                        delete_product_from_db(selected_product['id'])
                        st.rerun() 
                        st.rerun()

        else:
            st.info(t('no_products_available'))
            
    except Exception as e:
        st.error(f"{t('error_loading_products')} {e}")

def show_water_calculator_page():
# ... (بقية صفحات التطبيق)
def show_water_page():
    st.title(t('water_calc_title'))
    st.write(t('water_calc_desc'))

    # نموذج إدخال الوزن والعمر لحساب الهدف
    with st.form(key="water_goal_form_key"):
        weight_kg = st.number_input(t('weight_kg'), min_value=15.0, value=70.0, key='water_weight') 
        age_years = st.number_input(t('age_years'), min_value=5, value=30, key='water_age') 
    with st.form(key="water_calc_form"):
        weight = st.number_input(t('weight_kg'), min_value=1.0, value=70.0, step=1.0)
        age = st.number_input(t('age_years'), min_value=1, value=30, step=1)
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
    
    # FIX: تعريف المتغيرات المحلية من حالة الجلسة وتجهيزها
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
        
        if calculate_button:
            if weight > 15 and age > 5:
                goal = calculate_water_intake(weight, age)
                st.session_state['water_goal_liters'] = goal
            else:
                st.warning(t('realistic_input_warning'))

    # عرض التقدم 
    # FIX: تهريب (\) لضمان عرض الـ LaTeX بشكل صحيح في f-string
    st.markdown(f"**{t('current_consumption')}:** $${consumed_ml} \\text{{ml}} / {water_goal_ml:.0f} \\text{{ml}}$$")
    st.progress(progress_ratio, text=f"{progress_percent}%")
    if st.session_state['water_goal_liters'] > 0:
        goal = st.session_state['water_goal_liters']
        consumed_liters = st.session_state['water_consumed_ml'] / 1000
        
        st.subheader(t('recommended_intake'))
        st.info(f"**{goal:.2f} {t('liters')}**")

    if progress_ratio >= 1.0:
        st.balloons()
        st.success(t('goal_reached'))
        st.subheader(t('current_consumption'))
        st.write(f"**{consumed_liters:.2f} {t('liters')} / {goal:.2f} {t('liters')}**")
        
        # شريط التقدم
        progress_ratio = min(consumed_liters / goal, 1.0)
        st.progress(progress_ratio)

    # أزرار التفاعل
    col1, col2 = st.columns(2)
    
    # زر إضافة كأس ماء
    with col1:
        st.button(t('log_glass'), on_click=log_water_intake, use_container_width=True, type='primary')
    
    # زر إعادة التعيين
    with col2:
        st.button(t('reset_water'), on_click=reset_water_intake, use_container_width=True)
        if consumed_liters >= goal:
            st.balloons()
            st.success(t('goal_reached'))
            
        col_log, col_reset = st.columns(2)
        col_log.button(t('log_glass'), on_click=log_water_intake)
        col_reset.button(t('reset_water'), on_click=reset_water_intake)

    # نصائح عامة (لم تتغير)
    st.markdown("---")
    with st.expander(t('water_tips_title')):
        st.write(f"- **{t('water_tips_title')}:** {t('water_tip1')}")
        st.write(f"- **{t('water_tips_title')}:** {t('water_tip2')}")
        st.write(f"- **{t('water_tips_title')}:** {t('water_tip3')}")
        st.write(f"- **{t('water_tips_title')}:** {t('water_tip4')}")

    st.subheader(t('water_tips_title'))
    st.info(f"*{t('water_tip1')}*")
    st.info(f"*{t('water_tip2')}*")
    st.info(f"*{t('water_tip3')}*")
    st.info(f"*{t('water_tip4')}*")

def show_exercise_page():
    st.title(t('exercise_title'))
    st.write(t('exercise_desc'))
    st.image("https://placehold.co/600x200/98FB98/000000?text=Exercise+and+Health")
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
    with st.form(key="exercise_rec_form"):
        age = st.number_input(t('age_years'), min_value=1, value=30, step=1, key='ex_age')
        weight = st.number_input(t('weight_kg'), min_value=1.0, value=70.0, step=1.0, key='ex_weight')
        get_rec_button = st.form_submit_button(t('get_rec'))
        
        if get_rec_button:
            recommendation = get_exercise_recommendation(age, weight)
            st.success(f"**توصيتنا لك:** {recommendation}")

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
    st.markdown("---")
    st.subheader(t('exercise_tips_title'))
    st.info(f"*{t('exercise_tip1')}*")
    st.info(f"*{t('exercise_tip2')}*")
    st.info(f"*{t('exercise_tip3')}*")
    st.info(f"*{t('exercise_tip4')}*")


# --- الهيكل الرئيسي للتطبيق (Main App Structure) ---

def main():
    # اختيار اللغة في الشريط الجانبي
    st.sidebar.selectbox(
        "Language / اللغة", 
        options=['ar', 'en'], 
        index=['ar', 'en'].index(st.session_state.get('language', 'ar')), 
        key='language_selector',
        on_change=lambda: st.session_state.update(language=st.session_state.language_selector)
    )

    st.sidebar.title(t('navigation'))

    # التنقل للمستخدم غير المسجل
    if not st.session_state['user']:
        if st.sidebar.button(t('login_register')):
            st.session_state['page'] = 'Auth'
            st.session_state['auth_mode'] = 'login'
        if st.sidebar.button(t('home_page')):
            st.session_state['page'] = 'Home'
        if st.sidebar.button(t('products_page')):
            st.session_state['page'] = 'Products'
        if st.sidebar.button(t('admin_page')):
            st.session_state['page'] = 'Admin'

    # التنقل للمستخدم المسجل دخوله
    else:
        st.sidebar.write(f"**مرحباً بك:** {st.session_state['user'].email}")
        
        if st.sidebar.button(t('home_page')):
            st.session_state['page'] = 'Home'
        if st.sidebar.button(t('products_page')):
            st.session_state['page'] = 'Products'
        if st.sidebar.button(t('water_page')):
            st.session_state['page'] = 'Water'
        if st.sidebar.button(t('exercise_page')):
            st.session_state['page'] = 'Exercise'
        if st.sidebar.button(t('admin_page')):
            st.session_state['page'] = 'Admin'
        
        # **خيار تغيير كلمة المرور الجديد**
        if st.sidebar.button(t('password_update_form')):
            st.session_state['page'] = 'ChangePassword'
            
        st.sidebar.markdown("---")
        if st.sidebar.button(t('logout')):
            logout_user()


    # عرض الصفحة المختارة
    if st.session_state['page'] == 'Auth':
        show_auth_page()
    elif st.session_state['page'] == 'Products':
        show_products_page()
    elif st.session_state['page'] == 'Admin':
        show_admin_page()
    elif st.session_state['page'] == 'Water':
        show_water_page()
    elif st.session_state['page'] == 'Exercise':
        show_exercise_page()
    # **استدعاء صفحة تغيير كلمة المرور الجديدة**
    elif st.session_state['page'] == 'ChangePassword':
        show_password_change_form()
    else: # Default is Home
        show_home_page()

# تشغيل التطبيق
if __name__ == "__main__":
    main()
