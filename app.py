import streamlit as st
import pandas as pd
import json
import os
import streamlit.components.v1 as components
import plotly.express as px

# إعداد الصفحة
st.set_page_config(
    page_title="المساعد الذكي - ميزانية السفر للإمارات",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- تصميم الشات العصري المريح للموبايل -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

    body, p, h1, h2, h3, h4, .stMarkdown, .stTextInput, .stButton, .stChatInput {
        font-family: 'Cairo', sans-serif !important;
    }

    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }

    /* رأس الصفحة البسيط */
    .chat-header {
        background: rgba(30, 41, 59, 0.9);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 12px 18px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        direction: rtl;
    }
    
    .chat-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #38bdf8;
    }

    .data-badge {
        background: #1e3a8a;
        color: #93c5fd;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        border: 1px solid #3b82f6;
    }

    .stChatMessage {
        direction: rtl !important;
        text-align: right !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }

    .stChatInputContainer textarea {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- الاتصال بالذكاء الاصطناعي -----------------
def generate_ai_response(prompt_text, user_api_key):
    try:
        from google import genai
        client = genai.Client(api_key=user_api_key)
        
        models_to_try = ['gemini-3.8-flash', 'gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
        last_error = None
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_text,
                )
                if response and response.text:
                    return response.text
            except Exception as err:
                last_error = err
                continue
        raise last_error if last_error else Exception("تعذر الاتصال بالنموذج")
    except Exception as e:
        raise e

# ----------------- تهيئة ذاكرة الشات والترحيب -----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "أهلاً بك! 🇦🇪 تم تحميل **ملف ميزانية السفر للإمارات** بنجاح. يمكنك سؤالي الآن بالصوت أو النص عن أي بند من بنود الرحلة (المصاريف، التذاكر، الفنادق، إجمالي التكلفة، أو نصائح وخطط لتوفير الميزانية).",
            "speech": "أهلاً بك! تم ربط ملف ميزانية السفر للإمارات بنجاح. اسألني عن أي بند وسأجيبك فوراً.",
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
    st.markdown("### 📁 إدارة الملفات")
    uploaded_file = st.file_uploader("رفع ملف آخر (اختياري):", type=["xlsx", "xls", "csv"])

    if st.button("🗑️ مسح المحادثة والبدء من جديد"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# ----------------- تحميل وقراءة ملف ميزانية السفر للإمارات تلقائياً -----------------
df = None
all_sheets_data = {}
data_label = "جاري التحميل..."

# البحث التلقائي عن ملف ميزانية الإمارات في المجلد
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
            sheet_choice = st.sidebar.selectbox("اختر الورقة للعرض:", xl.sheet_names)
            df = all_sheets_data[sheet_choice]
        data_label = f"ملف مرفوع: {uploaded_file.name}"
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
else:
    # تحميل الملف التلقائي
    for fname in default_files:
        if os.path.exists(fname):
            try:
                if fname.endswith('.csv'):
                    df = pd.read_csv(fname)
                    all_sheets_data["الرئيسية"] = df
                    data_label = "بيانات مبيعات تجريبية"
                else:
                    xl = pd.ExcelFile(fname)
                    for sname in xl.sheet_names:
                        all_sheets_data[sname] = pd.read_excel(fname, sheet_name=sname)
                    
                    if len(xl.sheet_names) > 1:
                        sheet_choice = st.sidebar.selectbox("اختر ورقة الميزانية:", xl.sheet_names)
                        df = all_sheets_data[sheet_choice]
                    else:
                        df = all_sheets_data[xl.sheet_names[0]]
                    data_label = "✈️ ميزانية السفر للإمارات"
                break
            except Exception as e:
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
<div style="direction: rtl; text-align: center; margin-bottom: 12px;">
    <button id="micBtn" onclick="toggleVoice()" style="
        background: #ef4444;
        color: white;
        border: none;
        border-radius: 30px;
        padding: 8px 18px;
        font-size: 14px;
        font-family: sans-serif;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 10px rgba(239, 68, 68, 0.3);
    ">
        <span>🎙️</span>
        <span id="btnText">تحدث بالصوت</span>
    </button>
    <span id="micStatus" style="color: #94a3b8; font-size: 13px; margin-right: 10px;">
        اضغط وتحدث، وسينسخ سؤالك للصقه في خانة المحادثة
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
            document.getElementById('btnText').innerText = 'نستمع إليك الآن...';
            document.getElementById('micBtn').style.background = '#16a34a';
            document.getElementById('micStatus').innerText = 'تحدث الآن، نسمع صوتك...';
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
            alert('متصفحك لا يدعم التعرف الصوتي، استخدم صندوق الشات للكتابة.');
            return;
        }
        if (!isRecording) recognition.start();
        else recognition.stop();
    }
</script>
"""
components.html(voice_html, height=55)

# معاينة سريعة قابلة للطي للبيانات
if df is not None:
    with st.expander("👁️ استعراض جدول الميزانية (اضغط للإظهار)", expanded=False):
        c1, c2 = st.columns(2)
        c1.metric("عدد البنود / الصفوف", len(df))
        c2.metric("عدد الأعمدة", len(df.columns))
        st.dataframe(df, use_container_width=True)

# ----------------- عرض رسائل الشات السابقة -----------------
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # زر الاستماع الصوتي
        if msg.get("speech"):
            speech_js = f"""
            <div style="direction: rtl; margin-top: 6px;">
                <button onclick="speakMsg_{idx}()" style="
                    background: rgba(59, 130, 246, 0.15);
                    border: 1px solid #3b82f6;
                    color: #93c5fd;
                    padding: 4px 12px;
                    border-radius: 15px;
                    cursor: pointer;
                    font-size: 13px;
                ">🔊 استمع للصوت</button>
            </div>
            <script>
                function speakMsg_{idx}() {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        const utterance = new SpeechSynthesisUtterance({json.dumps(msg["speech"])});
                        utterance.lang = 'ar-SA';
                        window.speechSynthesis.speak(utterance);
                    }}
                }}
            </script>
            """
            components.html(speech_js, height=38)

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

                fig.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font=dict(family="Cairo", size=13))
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{idx}")

        # الخريطة الذهنية
        if msg.get("mindmap"):
            m_code = msg["mindmap"].get("mermaid_code", "")
            if m_code:
                mermaid_html = f"""
                <div style="direction: ltr; background: #1e293b; border-radius: 10px; padding: 12px; margin-top: 10px; text-align: center;">
                    <pre class="mermaid" style="background: transparent;">{m_code}</pre>
                </div>
                <script type="module">
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                    mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
                </script>
                """
                components.html(mermaid_html, height=330, scrolling=True)

# ----------------- إرسال سؤال جديد -----------------
user_input = st.chat_input("اسأل عن ميزانية السفر (مثال: كم إجمالي التكلفة؟ أو وزع لي المصاريف في رسم بياني...)")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if df is None and not all_sheets_data:
        error_msg = "لم يتم العثور على ملف الميزانية، يرجى رفعه من القائمة الجانبية."
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

                    # السياق السابق
                    history_context = []
                    for h_msg in st.session_state.messages[-5:-1]:
                        history_context.append(f"{h_msg['role']}: {h_msg['content']}")
                    history_text = "\n".join(history_context)

                    prompt = f"""
أنت مستشار مالي ومخطط رحلات ذكي وخبير في ميزانيات السفر إلى الإمارات.
لديك البيانات الكاملة لملف ميزانية السفر للإمارات:
{data_summary}

سياق المحادثة السابقة:
{history_text}

سؤال المستخدم: "{user_input}"

المطلوب: أجب بدقة بالغة باللغة العربية بأسلوب محادثة مالي ذكي وسلس.
قم بحساب التكاليف بدقة من الأرقام، وقدم نصائح ذكية إذا تطلب الأمر.

أجب حصراً بصيغة JSON نظيفة بدون أي كلام خارج الـ JSON:
{{
    "answer_arabic": "الإجابة التحليلية الذكية المباشرة مع الحسابات والأرقام بأسلوب محادثة شات.",
    "speech_summary": "ملخص صوتي سريع ومختصر في سطر واحد للقراءة الصوتية.",
    "chart": {{
        "has_chart": true or false,
        "type": "bar" | "line" | "pie",
        "title": "عنوان الرسم بالعربية",
        "x_col": "اسم العمود لمجموعات البنود",
        "y_col": "اسم عمود التكلفة/المبلغ",
        "agg": "sum"
    }},
    "mindmap": {{
        "has_mindmap": true or false,
        "mermaid_code": "graph TD\\n A[ميزانية الإمارات] --> B[السكن]\\n A --> C[الطيران]"
    }}
}}
قواعد:
1. إذا طلب توزيع المصاريف أو مقارنة بنود الصرف، اجعل has_chart = true (الرسم الدائري pie رائع للميزانية).
2. إذا طلب خطة سفر، استراتيجية توفير، أو جدول زمني، اجعل has_mindmap = true.
"""

                    raw_response = generate_ai_response(prompt, api_key)
                    clean_json = raw_response.strip()
                    if clean_json.startswith("```json"):
                        clean_json = clean_json[7:]
                    if clean_json.endswith("```"):
                        clean_json = clean_json[:-3]
                    clean_json = clean_json.strip()

                    res_data = json.loads(clean_json)

                    answer_text = res_data.get("answer_arabic", "")
                    speech_text = res_data.get("speech_summary", answer_text[:120])
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
