import streamlit as st
from huggingface_hub import InferenceClient

# 1. إعداد الواجهة
st.set_page_config(page_title="Major Finder 3.0", page_icon="🎓", layout="centered")

# خيار المظهر
col_title, col_mode = st.columns([4, 1])
with col_mode:
    mode = st.selectbox("🌓 المظهر", ["الوضع الغامق", "الوضع الفاتح"], label_visibility="collapsed")

# تعريف الألوان
if mode == "الوضع الغامق":
    main_bg, content_text, card_bg, accent = "#0e1117", "#ffffff", "#1e293b", "#3b82f6"
    res_box, res_text = "#112233", "#3399ff"
else:
    main_bg, content_text, card_bg, accent = "#ffffff", "#1a1a1a", "#f0f2f6", "#2e7d32"
    res_box, res_text = "#f1f8e9", "#1E3A8A"

st.markdown(f"""
    <style>
    /* --- إخفاء العلامة المائية وجميع زوائد ستريمليت --- */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stDeployButton, [data-testid="stDecoration"] {{ display:none; visibility: hidden; }}
    
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    .stApp {{ background-color: {main_bg}; }}

    /* تنسيق النصوص */
    h1, h2, h3, p, div {{
        color: {content_text} !important;
        font-family: 'Cairo', sans-serif !important;
        direction: rtl; text-align: center;
    }}

    /* تنسيق أزرار الخيارات */
    .stButton > button {{
        width: 100% !important;
        background-color: {card_bg} !important;
        color: {content_text} !important;
        border: 1px solid {accent} !important;
        padding: 15px !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
        transition: 0.3s;
        font-size: 18px !important;
    }}

    .stButton > button:hover {{
        background-color: {accent} !important;
        color: white !important;
        transform: scale(1.02);
    }}

    /* تلوين شريط التقدم */
    .stProgress > div > div > div > div {{ background-color: {accent} !important; }}

    /* صندوق النتيجة */
    .result-container {{
        background-color: {res_box} !important;
        color: {res_text} !important;
        padding: 30px; border-radius: 15px;
        text-align: center; direction: rtl; line-height: 2.2;
        border: 2px solid {accent};
    }}

    .main-major {{
        font-size: 35px !important; font-weight: 800;
        color: {accent} !important; display: block; 
        margin-bottom: 20px; text-decoration: underline;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. منطق الأسئلة
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.answers = []

questions = [
    "1. ما هو نوع النشاط الذي يثير شغفك؟",
    "2. كيف تفضل حل المشكلات المعقدة؟",
    "3. ما هو المجال الذي تجد نفسك مبدعاً فيه؟",
    "4. في أي بيئة عمل ترى نفسك مستقبلاً؟",
    "5. ما هو الدافع الأكبر لنجاحك المهني؟"
]
options = [
    ["بناء الأنظمة والبرمجة", "الرعاية الطبية والعلوم", "القيادة وإدارة الأعمال", "الفنون والتصميم الإبداعي", "الأبحاث والاكتشافات العلمية"],
    ["التحليل المنطقي والبيانات", "التواصل المباشر والتعاطف", "التخطيط الاستراتيجي والتنظيم", "التجربة العملية والابتكار", "التفكير الفلسفي والنقدي"],
    ["الرياضيات والتقنيات", "اللغات والعلوم الإنسانية", "الاقتصاد والعلوم السياسية", "الفيزياء والهندسة", "القانون والمرافعة"],
    ["خلف الشاشات والخوارزميات", "في المستشفيات أو المختبرات", "في المكاتب والاجتماعات", "في الميدان أو المواقع الإنشائية", "في مراكز التدريب والتعليم"],
    ["إحداث ثورة تقنية", "مساعدة البشرية وتحسين الصحة", "تحقيق الريادة والمال", "ترك بصمة إبداعية ملهمة", "الوصول لحقائق علمية جديدة"]
]

st.title("🎓 اكتشف تخصصك الجامعي")

if st.session_state.step < 5:
    step = st.session_state.step
    st.write(f"### {questions[step]}")
    st.progress((step + 1) / 5)
    
    # عرض الخيارات كأزرار بدلاً من Radio
    for idx, opt in enumerate(options[step]):
        if st.button(opt, key=f"btn_{step}_{idx}"):
            st.session_state.answers.append(opt)
            st.session_state.step += 1
            st.rerun()

else:
    st.balloons()
    HF_TOKEN = st.secrets["HF_TOKEN"]
    
    st.write("### اكتملت الإجابات! اضغط للتحليل")
    if st.button("🔍 تحليل النتائج الآن", type="primary"):
        try:
            client = InferenceClient(api_key=HF_TOKEN)
            user_data = " | ".join(st.session_state.answers)
            messages = [
                {"role": "system", "content": "أنت مستشار أكاديمي. اعرض التخصص في أول سطر داخل <span class='main-major'>[التخصص]</span> ثم الأسباب والبدائل بشكل مرتب."},
                {"role": "user", "content": f"الميول: {user_data}"}
            ]
            with st.spinner("🧠 جاري التفكير..."):
                response = client.chat_completion(model="Qwen/Qwen2.5-72B-Instruct", messages=messages, max_tokens=800)
                output = response.choices[0].message.content
                st.markdown(f'<div class="result-container">{output.replace("- ", "• ").replace("\n", "<br>")}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"خطأ في الاتصال: {e}")

    if st.button("🔄 إعادة المحاولة"):
        st.session_state.step = 0
        st.session_state.answers = []
        st.rerun()