import streamlit as st
import os
# ... (بقية الـ imports) ...
from dotenv import load_dotenv

# --- تعريف نصوص التطبيق لخاصية الترجمة ---
# (تم حذف القاموس اختصاراً، لكنه موجود في ملفك الأصلي)
TEXTS = {
    # ... (محتوى قاموس TEXTS) ...
}
# --- دالة مساعدة للحصول على النص المترجم ---
def get_text(key):
    # افتراض اللغة العربية (ar) كخيار افتراضي
    lang = st.session_state.get('language', 'ar')
    return TEXTS[lang].get(key, key) 

# --- إعدادات الصفحة (يجب أن يكون هذا أول استدعاء لـ Streamlit) ---
st.set_page_config(
    page_title="SMART DA .COM", 
    page_icon="🩺", 
    layout="wide",       
    initial_sidebar_state="expanded"
)
# -----------------------------------------------------------------

# ... (بقية الدوال والتهيئة: init_supabase_client, init_session_state, login_user, etc. لم تتغير) ...

# --- صفحات التطبيق (تم تحديث دالة الصفحة الرئيسية) ---

# ... (بقية دوال الصفحات لم تتغير) ...

def show_home_page():
    # وظيفة عرض الصفحة الرئيسية
    st.title(get_text("welcome_title"))
    
    # 🌟🌟🌟 التعديل الحاسم هنا 🌟🌟🌟
    image_name = "smartda.jpg" 
    
    # استخدام المسار النسبي (اسم الملف فقط). 
    # يجب التأكد من وضع الصورة "smartda.jpg" في نفس مجلد ملف البايثون.
    st.image(image_name, width=400) 
    # 🌟🌟🌟 نهاية التعديل 🌟🌟🌟
    
    st.write(get_text("welcome_msg_1"))
    st.write(get_text("welcome_msg_2"))

# ... (بقية دوال الصفحات والدوال المساعدة لم تتغير) ...


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




