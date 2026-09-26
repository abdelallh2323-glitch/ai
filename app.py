import streamlit as st
import pandas as pd
import json
import os
import streamlit.components.v1 as components
import plotly.express as px

# إعداد الصفحة مع الحفاظ على تناسق العرض
st.set_page_config(
    page_title="المساعد الذكي - ميزانية السفر للإمارات",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- تصميم عصري ومنسق للكمبيوتر والموبايل -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

    /* توحيد خط التطبيق بشكل أنيق ومريح */
    body, p, span, .stMarkdown, .stTextInput, .stButton, .stChatInput {
        font-family: 'Cairo', sans-serif !important;
        font-size: 15px !important;
        line-height: 1.7 !important;
    }

    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }

    /* حل مشكلة الشاشة الممتدة على الكمبيوتر: تحديد عرض مريح ومحاذاة في المنتصف مثل ChatGPT */
    .main .block-container {
        max-width: 840px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin: 0 auto !important;
    }

    /* رأس الصفحة المتناسق */
    .chat-header {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        direction: rtl;
    }
    
    .chat-title {
        font-size: 1.15rem !important;
        font-weight: 800;
        color: #38bdf8;
    }

    .data-badge {
        background: #1e3a8a;
        color: #93c5fd;
        padding: 3px 10px;
        border-radius: 16px;
        font-size: 0.8rem !important;
        font-weight: 700;
        border: 1px solid #3b82f6;
    }

    /* فقاعات الشات */
    .stChatMessage {
        direction: rtl !important;
        text-align: right !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        padding: 12px !important;
        background-color: #162032 !important;
        border: 1px solid #1e293b !important;
    }

    /* 🎨 تلوين بنود الإكسل، المعادلات، والأرقام داخل النص */
    .item-badge {
        color: #38bdf8 !important;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.35);
        padding: 2px 7px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
        margin: 0 2px;
    }

    .calc-badge {
        color: #4ade80 !important;
        background: rgba(74, 222, 128, 0.12);
        border: 1px solid rgba(74, 222, 128, 0.35);
        padding: 2px 7px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
        margin: 0 2px;
        font-family: monospace, sans-serif !important;
        direction: ltr !important;
    }

    .num-highlight {
        color: #fbbf24 !important;
        font-weight: 700;
    }

    /* صندوق إدخال الشات المتناسق */
    .stChatInputContainer textarea {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
        font-size: 15px !important;
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- دالة ذكية للاتصال واكتشاف النماذج المتاحة -----------------
def get_available_models(client):
    try:
        model_names = []
        for m in client.models.list():
            name = m.name.replace("models/", "")
            if "embed" not in name.lower():
                model_names.append(name)
        return model_names
    except Exception:
        return []

def generate_ai_response(prompt_text, user_api_key, preferred_model=None):
    from google import genai
    client = genai.Client(api_key=user_api_key)
    
    # 1. إذا حدد المستخدم نموذجاً أو تم اكتشافه
    candidates = []
    if preferred_model:
        candidates.append(preferred_model)
        
    # 2. محاولة جلب النماذج المدعومة من حساب المستخدم مباشرة لتجنب خطأ 404
    discovered = get_available_models(client)
    if discovered:
        # ترتيب النماذج بحيث تأتي الأحدث والأسرع أولاً
        flash_models = [m for m in discovered if "flash" in m.lower()]
        other_models = [m for m in discovered if "flash" not in m.lower()]
        candidates.extend(flash_models + other_models)
    
    # 3. قائمة افتراضية احتياطية
    fallback_defaults = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-3.8-flash', 'gemini-1.5-pro']
    for fb in fallback_defaults:
        if fb not in candidates:
            candidates.append(fb)

    # تجربة النماذج حتى ينجح أحدها
    errors = []
    for model_name in candidates:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
            )
            if response and response.text:
                return response.text, model_name
        except Exception as err:
            errors.append(f"{model_name}: {err}")
            continue

    raise Exception(f"تعذر الاتصال بالنماذج المتاحة. الأخطاء:\n" + "\n".join(errors[:3]))

# ----------------- تهيئة ذاكرة الشات والرسائل -----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """أهلاً بك! 🇦🇪 تم ربط <span class="item-badge">ميزانية السفر للإمارات</span> بنجاح.
يمكنك سؤالي عن أي بند أو تكلفة، وسأعرض لك:
- <span class="item-badge">أسماء البنود والأعمدة</span> باللون الأزرق.
- <span class="calc-badge">الحسابات والأرقام والمعادلات</span> باللون الأخضر.
- التحليل المالي والنصائح باللون المعتاد، مع رسوم بيانية وخرائط ذهنية عند الحاجة.""",
            "speech": "أهلاً بك! تم ربط ميزانية السفر للإمارات. اسألني عن أي بند وسأحسب لك التكاليف فوراً.",
            "chart": None,
            "mindmap": None
        }
    ]

# ----------------- القائمة الجانبية (Sidebar) -----------------
api_key = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.markdown("### ⚙️ الإعدادات والبيانات")
    
    if not api_key:
        api_key = st.text_input(
            "مفتاح Google Gemini API Key:",
            type="password",
            placeholder="AIzaSy...",
            help="احصل عليه مجاناً في دقيقة من Google AI Studio"
        )
        if not api_key:
            st.info("💡 [احصل على مفتاح API مجاناً](https://aistudio.google.com/app/apikey)")
    else:
        st.success("✅ مفتاح الـ API مسجل بنجاح")

    st.markdown("---")
    st.markdown("### 📁 إدارة ملفات الميزانية")
    uploaded_file = st.file_uploader("رفع ملف ميزانية آخر (اختياري):", type=["xlsx", "xls", "csv"])

    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# ----------------- قراءة بيانات ميزانية الإمارات -----------------
df = None
all_sheets_data = {}
data_label = "جاري التحميل..."

default_files = [
    "ميزانيه السفر للامارات.xlsx",
    "budget_uae.xlsx",
    "sample_data.csv"
]

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            all_sheets_data["الرئيسية"] = df
        else:
            xl = pd.ExcelFile(uploaded_file)
            for sname in xl.sheet_names:
                all_sheets_data[sname] = pd.read_excel(uploaded_file, sheet_name=sname)
            sheet_choice = st.sidebar.selectbox("اختر الورقة:", xl.sheet_names)
            df = all_sheets_data[sheet_choice]
        data_label = f"ملف مرفوع: {uploaded_file.name}"
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
else:
    for fname in default_files:
        if os.path.exists(fname):
            try:
                if fname.endswith('.csv'):
                    df = pd.read_csv(fname)
                    all_sheets_data["الرئيسية"] = df
                    data_label = "بيانات تجريبية"
                else:
                    xl = pd.ExcelFile(fname)
                    for sname in xl.sheet_names:
                        all_sheets_data[sname] = pd.read_excel(fname, sheet_name=sname)
                    
                    if len(xl.sheet_names) > 1:
                        sheet_choice = st.sidebar.selectbox("ورقة العمل المعروضة:", xl.sheet_names)
                        df = all_sheets_data[sheet_choice]
                    else:
                        df = all_sheets_data[xl.sheet_names[0]]
                    data_label = "✈️ ميزانية السفر للإمارات"
                break
            except Exception:
                continue

# ----------------- رأس الشات -----------------
st.markdown(f"""
<div class="chat-header">
    <div class="chat-title">💬 مساعد ميزانية السفر للإمارات</div>
    <div class="data-badge">{data_label}</div>
</div>
""", unsafe_allow_html=True)

# ----------------- ودجت الصوت النظيف -----------------
voice_html = """
<div style="direction: rtl; text-align: center; margin-bottom: 10px;">
    <button id="micBtn" onclick="toggleVoice()" style="
        background: #ef4444;
        color: white;
        border: none;
        border-radius: 25px;
        padding: 6px 16px;
        font-size: 13px;
        font-family: sans-serif;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
    ">
        <span>🎙️</span>
        <span id="btnText">تحدث بالصوت</span>
    </button>
    <span id="micStatus" style="color: #94a3b8; font-size: 12px; margin-right: 8px;">
        اضغط وتحدث، وسيتم نسخ كلامك للصقه في خانة السؤال
    </span>
</div>

<script>
    let recognition = null;
    let isRecording = false;

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRec();
        recognition.lang = 'ar-SA';
        recognition.continuous = false;

        recognition.onstart = function() {
            isRecording = true;
            document.getElementById('btnText').innerText = 'نستمع لصوتك...';
            document.getElementById('micBtn').style.background = '#16a34a';
            document.getElementById('micStatus').innerText = 'تحدث الآن بالعربية...';
            document.getElementById('micStatus').style.color = '#4ade80';
        };

        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            navigator.clipboard.writeText(text).then(() => {
                document.getElementById('micStatus').innerText = '✅ تم التعرف: "' + text + '" (تم نسخه للصقه أدناه)';
                document.getElementById('micStatus').style.color = '#38bdf8';
            });
        };

        recognition.onerror = function() {
            isRecording = false;
            document.getElementById('btnText').innerText = 'تحدث بالصوت';
            document.getElementById('micBtn').style.background = '#ef4444';
            document.getElementById('micStatus').innerText = 'تعذر التقاط الصوت، يمكنك الكتابة في الأسفل.';
        };

        recognition.onend = function() {
            isRecording = false;
            document.getElementById('btnText').innerText = 'تحدث بالصوت';
            document.getElementById('micBtn').style.background = '#ef4444';
        };
    }

    function toggleVoice() {
        if (!recognition) {
            alert('متصفحك لا يدعم التعرف الصوتي المباشر، يمكنك الكتابة.');
            return;
        }
        if (!isRecording) recognition.start();
        else recognition.stop();
    }
</script>
"""
components.html(voice_html, height=48)

# معاينة سريعة قابلة للطي للجدول
if df is not None:
    with st.expander("👁️ عرض جدول الميزانية (اضغط للإظهار)", expanded=False):
        c1, c2 = st.columns(2)
        c1.metric("عدد البنود", len(df))
        c2.metric("عدد الأعمدة", len(df.columns))
        st.dataframe(df, use_container_width=True)

# ----------------- عرض رسائل الشات مع دعم وسوم التلوين -----------------
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)
        
        # زر الاستماع الصوتي
        if msg.get("speech"):
            clean_speech = msg["speech"].replace("<span class='item-badge'>", "").replace("<span class='calc-badge'>", "").replace("</span>", "")
            speech_js = f"""
            <div style="direction: rtl; margin-top: 5px;">
                <button onclick="speakMsg_{idx}()" style="
                    background: rgba(59, 130, 246, 0.15);
                    border: 1px solid #3b82f6;
                    color: #93c5fd;
                    padding: 3px 12px;
                    border-radius: 12px;
                    cursor: pointer;
                    font-size: 12px;
                ">🔊 استمع</button>
            </div>
            <script>
                function speakMsg_{idx}() {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        const utterance = new SpeechSynthesisUtterance({json.dumps(clean_speech)});
                        utterance.lang = 'ar-SA';
                        window.speechSynthesis.speak(utterance);
                    }}
                }}
            </script>
            """
            components.html(speech_js, height=34)

        # الرسم البياني
        if msg.get("chart") and df is not None:
            chart_info = msg["chart"]
            x_col = chart_info.get("x_col")
            y_col = chart_info.get("y_col")
            c_type = chart_info.get("type", "bar")
            title = chart_info.get("title", "رسم بياني")

            if x_col in df.columns and y_col in df.columns:
                agg = chart_info.get("agg", "sum")
                if agg == "sum":
                    plot_df = df.groupby(x_col)[y_col].sum().reset_index()
                elif agg == "mean":
                    plot_df = df.groupby(x_col)[y_col].mean().reset_index()
                else:
                    plot_df = df.groupby(x_col)[y_col].count().reset_index()

                if c_type == "pie":
                    fig = px.pie(plot_df, names=x_col, values=y_col, title=title, template="plotly_dark")
                elif c_type == "line":
                    fig = px.line(plot_df, x=x_col, y=y_col, title=title, template="plotly_dark")
                else:
                    fig = px.bar(plot_df, x=x_col, y=y_col, title=title, template="plotly_dark")

                fig.update_layout(
                    paper_bgcolor="#1e293b",
                    plot_bgcolor="#1e293b",
                    font=dict(family="Cairo", size=12),
                    margin=dict(l=10, r=10, t=35, b=10)
                )
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{idx}")

        # الخريطة الذهنية
        if msg.get("mindmap"):
            m_code = msg["mindmap"].get("mermaid_code", "")
            if m_code:
                mermaid_html = f"""
                <div style="direction: ltr; background: #1e293b; border-radius: 8px; padding: 10px; margin-top: 8px; text-align: center;">
                    <pre class="mermaid" style="background: transparent;">{m_code}</pre>
                </div>
                <script type="module">
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                    mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
                </script>
                """
                components.html(mermaid_html, height=310, scrolling=True)

# ----------------- إرسال سؤال جديد -----------------
user_input = st.chat_input("اكتب سؤالك هنا عن ميزانية السفر للإمارات...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if not all_sheets_data and df is None:
        error_msg = "لم يتم العثور على ملف الميزانية، يرجى التأكد من رفعه."
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant"):
            st.warning(error_msg)
    elif not api_key:
        error_msg = "⚠️ يرجى إدخال مفتاح Gemini API Key في القائمة الجانبية."
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant"):
            st.warning(error_msg)
    else:
        with st.chat_message("assistant"):
            with st.spinner("🧠 جاري فحص بنود الميزانية وحساب الأرقام..."):
                try:
                    # تلخيص كل أوراق العمل في ملف الميزانية
                    summary_parts = []
                    for sheet_name, s_df in all_sheets_data.items():
                        summary_parts.append(f"--- ورقة الميزانية: {sheet_name} ---")
                        summary_parts.append(f"الأعمدة: {list(s_df.columns)}")
                        summary_parts.append(f"البيانات:\n{s_df.to_string()}")
                        num_cols = s_df.select_dtypes(include=['number']).columns.tolist()
                        if num_cols:
                            summary_parts.append(f"إجماليات الأرقام:\n{s_df[num_cols].sum().to_string()}")

                    data_summary = "\n\n".join(summary_parts)

                    # سياق آخر 4 رسائل سابقة
                    history_context = []
                    for h_msg in st.session_state.messages[-5:-1]:
                        # تنظيف الوسوم من السياق حتى لا تشوش على النموذج
                        c_text = h_msg['content'].replace("<span class='item-badge'>", "").replace("<span class='calc-badge'>", "").replace("</span>", "")
                        history_context.append(f"{h_msg['role']}: {c_text}")
                    history_text = "\n".join(history_context)

                    prompt = f"""
أنت مستشار مالي ومحلل ذكي ومرح لميزانية السفر للإمارات.
بيانات الميزانية المتاحة:
{data_summary}

سياق المحادثة السابقة:
{history_text}

سؤال المستخدم الحالي: "{user_input}"

قواعد هامة جداً لتنسيق الألوان في إجابتك:
1. عند الإشارة إلى أي اسم عمود أو بند أو تصنيف من الجدول، ضعه داخل: <span class="item-badge">اسم البند</span> (سيظهر بلون أزرق مميز).
2. عند كتابة أي معادلة، عملية حسابية، أو رقم وتكلفة مالية، ضعه داخل: <span class="calc-badge">المعادلة أو الرقم</span> (سيظهر بلون أخضر مميز).
3. باقي الكلام والشرح العادي: اكتبه باللغة العربية الطبيعية بدون وسوم.

أجب حصراً بصيغة JSON نظيفة بدون أي كلام خارج الـ JSON:
{{
    "answer_arabic": "الإجابة التحليلية الذكية باللغة العربية مع تطبيق وسوم التلوين على البنود والمعادلات.",
    "speech_summary": "ملخص صوتي سريع خالي من أي وسوم HTML مناسب للنطق الصوتي.",
    "chart": {{
        "has_chart": true or false,
        "type": "bar" | "line" | "pie",
        "title": "عنوان الرسم بالعربية",
        "x_col": "اسم العمود",
        "y_col": "اسم عمود التكلفة/المبلغ",
        "agg": "sum"
    }},
    "mindmap": {{
        "has_mindmap": true or false,
        "mermaid_code": "graph TD\\n A[الميزانية] --> B[البند 1]"
    }}
}}
"""

                    raw_response, used_model = generate_ai_response(prompt, api_key)
                    clean_json = raw_response.strip()
                    if clean_json.startswith("```json"):
                        clean_json = clean_json[7:]
                    if clean_json.endswith("```"):
                        clean_json = clean_json[:-3]
                    clean_json = clean_json.strip()

                    res_data = json.loads(clean_json)

                    answer_text = res_data.get("answer_arabic", "")
                    speech_text = res_data.get("speech_summary", "")
                    chart_data = res_data.get("chart") if res_data.get("chart", {}).get("has_chart") else None
                    mindmap_data = res_data.get("mindmap") if res_data.get("mindmap", {}).get("has_mindmap") else None

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer_text,
                        "speech": speech_text,
                        "chart": chart_data,
                        "mindmap": mindmap_data
                    })

                    st.rerun()

                except Exception as e:
                    st.error(f"حدث خطأ أثناء معالجة السؤال: {e}")
