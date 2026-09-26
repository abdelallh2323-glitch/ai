import streamlit as st
import pandas as pd
import json
import os
import re
import time
from datetime import datetime
import streamlit.components.v1 as components
import plotly.express as px

# إعداد الصفحة لتكون متجاوبة 100% بتصميم عصري راقٍ
st.set_page_config(
    page_title="Aura Travel AI • ميزانية الإمارات",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- تصميم فائق الفخامة مستوحى من كبرى شركات الذكاء الاصطناعي (Aura Theme) -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Cairo:wght@400;600;700;800;900&display=swap');

    /* إخفاء عناصر ستريمليت الافتراضية المزعجة */
    #MainMenu, header, footer { visibility: hidden !important; height: 0 !important; }
    
    * {
        box-sizing: border-box;
    }

    body, .stApp {
        background: radial-gradient(circle at 50% 0%, #170d2c 0%, #0a0614 70%, #05030a 100%) !important;
        color: #f1f5f9;
        font-family: 'Cairo', 'Plus Jakarta Sans', sans-serif !important;
    }

    /* حاوية المحادثة المركزية - متناسقة ومريحة جداً للعين على الكمبيوتر والموبايل */
    .main .block-container {
        max-width: 780px !important;
        padding-top: 1rem !important;
        padding-bottom: 6rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin: 0 auto !important;
    }

    /* شريط العنوان العلوي (Aura Top Bar) */
    .aura-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(23, 14, 44, 0.65);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(168, 85, 247, 0.2);
        border-radius: 20px;
        padding: 10px 18px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px -10px rgba(147, 51, 234, 0.2);
        direction: rtl;
    }

    .brand-section {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* الأيقونة الدائرية المتوهجة (The Glowing Orb) */
    .glowing-orb {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #ec4899, #8b5cf6 60%, #3b82f6 100%);
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.6), inset 0 0 10px rgba(255, 255, 255, 0.5);
        animation: orbPulse 4s ease-in-out infinite alternate;
        flex-shrink: 0;
    }

    @keyframes orbPulse {
        0% { transform: scale(0.97); box-shadow: 0 0 15px rgba(168, 85, 247, 0.4); }
        100% { transform: scale(1.05); box-shadow: 0 0 25px rgba(236, 72, 153, 0.7); }
    }

    .brand-title {
        font-weight: 800;
        font-size: 1.05rem;
        background: linear-gradient(135deg, #ffffff 0%, #d8b4fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .brand-subtitle {
        font-size: 0.75rem;
        color: #a855f7;
        font-weight: 600;
        margin: 0;
    }

    .model-badge {
        background: rgba(168, 85, 247, 0.15);
        border: 1px solid rgba(168, 85, 247, 0.35);
        color: #e9d5ff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* ----------------- فقاعات الرسائل (Chat Bubbles) ----------------- */
    .msg-wrapper {
        margin-bottom: 22px;
        display: flex;
        flex-direction: column;
        direction: rtl;
        text-align: right;
    }

    /* رسالة المستخدم: كبسولة أرجوانية زجاجية فاخرة */
    .msg-user {
        align-self: flex-start;
        background: linear-gradient(135deg, rgba(88, 28, 135, 0.45) 0%, rgba(126, 34, 206, 0.3) 100%);
        border: 1px solid rgba(168, 85, 247, 0.35);
        border-radius: 20px 20px 4px 20px;
        padding: 14px 18px;
        max-width: 85%;
        color: #f3e8ff;
        font-size: 0.96rem;
        line-height: 1.6;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
    }

    /* رسالة المساعد الذكي: بطاقة سوداء ناعمة مع لمسة نيون خفيفة */
    .msg-assistant-card {
        align-self: stretch;
        background: rgba(18, 12, 33, 0.75);
        border: 1px solid rgba(147, 51, 234, 0.2);
        border-radius: 22px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(16px);
        margin-top: 4px;
    }

    .assistant-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }

    .assistant-body {
        font-size: 0.98rem;
        line-height: 1.85;
        color: #f1f5f9;
    }

    /* تفاصيل البيانات الملونة: شارات فائقة الجمال */
    .item-badge {
        color: #38bdf8 !important;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 2px 9px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.9em;
        display: inline-block;
        margin: 0 3px;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.15);
    }

    .calc-badge {
        color: #4ade80 !important;
        background: rgba(74, 222, 128, 0.12);
        border: 1px solid rgba(74, 222, 128, 0.4);
        padding: 2px 9px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.9em;
        display: inline-block;
        margin: 0 3px;
        font-family: 'Plus Jakarta Sans', monospace !important;
        direction: ltr !important;
        box-shadow: 0 0 10px rgba(74, 222, 128, 0.15);
    }

    /* شريط أدوات أسفل كل رسالة (النسخ، إعادة التوليد، الوقت، الاستماع) */
    .msg-meta-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 14px;
        padding-top: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        font-size: 0.76rem;
        color: #94a3b8;
        direction: rtl;
    }

    .meta-tags {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .action-btn {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #cbd5e1;
        padding: 4px 10px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.75rem;
        font-family: 'Cairo', sans-serif;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        transition: all 0.2s;
    }

    .action-btn:hover {
        background: rgba(168, 85, 247, 0.25);
        color: #ffffff;
        border-color: #a855f7;
    }

    /* ----------------- شريط الإدخال السفلي (Floating Dock) ----------------- */
    .stChatInputContainer {
        border-radius: 28px !important;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.6) !important;
    }

    .stChatInputContainer textarea {
        background: rgba(22, 14, 40, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(168, 85, 247, 0.35) !important;
        border-radius: 24px !important;
        color: #f8fafc !important;
        font-family: 'Cairo', sans-serif !important;
        font-size: 15px !important;
        padding: 12px 18px !important;
        direction: rtl !important;
        text-align: right !important;
    }

    .stChatInputContainer textarea:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 18px rgba(168, 85, 247, 0.35) !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- دوال معالجة النصوص الذكية -----------------
def apply_custom_styling(text):
    if not text:
        return ""
    # تحويل [[اسم البند]] لشارة زرقاء متوهجة
    text = re.sub(r'\[\[(.*?)\]\]', r'<span class="item-badge">\1</span>', text)
    # تحويل {{المعادلة أو الرقم}} لشارة خضراء متوهجة
    text = re.sub(r'\{\{(.*?)\}\}', r'<span class="calc-badge">\1</span>', text)
    return text

def parse_safe_json(raw_text):
    clean = raw_text.strip()
    if clean.startswith("```json"):
        clean = clean[7:]
    elif clean.startswith("```"):
        clean = clean[3:]
    if clean.endswith("```"):
        clean = clean[:-3]
    clean = clean.strip()
    
    try:
        return json.loads(clean)
    except Exception:
        pass

    # استخراج الإجابة النمطية بحماية تامة
    try:
        ans_match = re.search(r'"answer_arabic"\s*:\s*"(.*?)"\s*,\s*"speech_summary"', clean, re.DOTALL)
        if ans_match:
            ans_content = ans_match.group(1).replace('\\"', '"').replace('\\n', '\n')
            return {
                "answer_arabic": ans_content,
                "speech_summary": ans_content[:90],
                "chart": {"has_chart": False},
                "mindmap": {"has_mindmap": False}
            }
    except Exception:
        pass

    return {
        "answer_arabic": clean,
        "speech_summary": clean[:90],
        "chart": {"has_chart": False},
        "mindmap": {"has_mindmap": False}
    }

# ----------------- محرك الاتصال بـ Google Gemini الذكي -----------------
def generate_ai_response(prompt_text, user_api_key):
    from google import genai
    client = genai.Client(api_key=user_api_key)
    
    # استكشاف النماذج النشطة في حساب المستخدم
    active_models = []
    try:
        for m in client.models.list():
            name = m.name.replace("models/", "")
            if "embed" not in name.lower():
                active_models.append(name)
    except Exception:
        pass

    defaults = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-3.8-flash', 'gemini-1.5-pro']
    for d in defaults:
        if d not in active_models:
            active_models.append(d)

    for model_name in active_models:
        try:
            start_t = time.time()
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
            )
            if response and response.text:
                latency = round(time.time() - start_t, 2)
                return response.text, model_name, latency
        except Exception:
            continue

    raise Exception("تعذر الاتصال بالنماذج السحابية، يرجى مراجعة مفتاح الـ API.")

# ----------------- قراءة ملف ميزانية الإمارات -----------------
df = None
all_sheets_data = {}
default_files = ["ميزانيه السفر للامارات.xlsx", "budget_uae.xlsx", "sample_data.csv"]

for fname in default_files:
    if os.path.exists(fname):
        try:
            if fname.endswith('.csv'):
                df = pd.read_csv(fname)
                all_sheets_data["الرئيسية"] = df
            else:
                xl = pd.ExcelFile(fname)
                for sname in xl.sheet_names:
                    all_sheets_data[sname] = pd.read_excel(fname, sheet_name=sname)
                df = all_sheets_data[xl.sheet_names[0]]
            break
        except Exception:
            continue

# ----------------- إدارة الجلسة والذاكرة -----------------
now_time = datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "id": 0,
            "role": "assistant",
            "content": apply_custom_styling("""أهلاً بك في **Aura Travel AI** 🇦🇪
تم اعتماد وتحليل [[ميزانية السفر للإمارات]].

أنا جاهز للإجابة بدقة وحساب أي تكاليف ومقارنات لك:
- [[أسماء البنود والأقسام]] مميزة بالأزرق السماوي.
- {{الأرقام والحسابات والأسعار}} مميزة بالأخضر الزمردي.
- رسوم بيانية وتوزيعات مالية وخرائط عمل بصرية فورية عند الطلب."""),
            "speech": "أهلاً بك! تم ربط ميزانية السفر للإمارات. اسألني عن أي بند أو تكلفة وسأحسبها لك فوراً.",
            "time": now_time,
            "latency": 0.4,
            "chart": None,
            "mindmap": None,
            "raw_user_query": None
        }
    ]

# ----------------- الشريط العلوي الفاخر (Aura Top Bar) -----------------
st.markdown(f"""
<div class="aura-topbar">
    <div class="brand-section">
        <div class="glowing-orb"></div>
        <div>
            <h1 class="brand-title">Aura 2.0 • مساعد الإمارات</h1>
            <p class="brand-subtitle">مستشار مالي ذكي لميزانية السفر</p>
        </div>
    </div>
    <div class="model-badge">
        <span>✨ Gemini 3.8</span>
        <span style="color: #4ade80;">●</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- ودجت الصوت النظيف والأنيق -----------------
voice_code = """
<div style="direction: rtl; display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 15px;">
    <button id="micBtn" onclick="toggleVoice()" style="
        background: radial-gradient(circle, #8b5cf6, #6d28d9);
        border: 1px solid rgba(168, 85, 247, 0.4);
        color: white;
        border-radius: 30px;
        padding: 7px 18px;
        font-size: 13px;
        font-family: 'Cairo', sans-serif;
        font-weight: 700;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
        transition: 0.3s;
    ">
        <span id="micIcon">🎙️</span>
        <span id="btnText">تحدث بالصوت</span>
    </button>
    <span id="micStatus" style="color: #94a3b8; font-size: 12px; font-family: 'Cairo', sans-serif;">
        اضغط وتحدث بالعربية، وسيتم تجهيز كلامك في الصندوق أدناه
    </span>
</div>

<script>
    let rec = null;
    let recording = false;
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        rec = new SRec();
        rec.lang = 'ar-SA';
        rec.continuous = false;

        rec.onstart = function() {
            recording = true;
            document.getElementById('btnText').innerText = 'نستمع إليك الآن...';
            document.getElementById('micBtn').style.background = 'radial-gradient(circle, #ec4899, #be185d)';
            document.getElementById('micStatus').innerText = 'تحدث الآن، نسمع صوتك...';
            document.getElementById('micStatus').style.color = '#f472b6';
        };
        rec.onresult = function(e) {
            const txt = e.results[0][0].transcript;
            navigator.clipboard.writeText(txt).then(() => {
                document.getElementById('micStatus').innerText = '✅ تم التعرف: "' + txt + '" (تم نسخه للصقه في الشات)';
                document.getElementById('micStatus').style.color = '#38bdf8';
            });
        };
        rec.onerror = function() {
            recording = false;
            document.getElementById('btnText').innerText = 'تحدث بالصوت';
            document.getElementById('micBtn').style.background = 'radial-gradient(circle, #8b5cf6, #6d28d9)';
            document.getElementById('micStatus').innerText = 'تعذر التقاط الصوت، يمكنك الكتابة في الأسفل.';
        };
        rec.onend = function() {
            recording = false;
            document.getElementById('btnText').innerText = 'تحدث بالصوت';
            document.getElementById('micBtn').style.background = 'radial-gradient(circle, #8b5cf6, #6d28d9)';
        };
    }
    function toggleVoice() {
        if (!rec) { alert('المتصفح لا يدعم التسجيل المباشر'); return; }
        if (!recording) rec.start(); else rec.stop();
    }
</script>
"""
components.html(voice_code, height=45)

# معاينة ميزانية الإمارات في كبسولة أنيقة
if df is not None:
    with st.expander(f"📊 استعراض جدول ميزانية الإمارات ({len(df)} بند) • اضغط هنا", expanded=False):
        st.dataframe(df, use_container_width=True)

# ----------------- مفتاح الـ API من Secrets أو Sidebar -----------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
with st.sidebar:
    st.markdown("### ⚙️ إعدادات Aura")
    if not api_key:
        api_key = st.text_input("مفتاح Gemini API Key:", type="password", placeholder="AIzaSy...")
    else:
        st.success("✅ مفتاح الـ API متصل بنجاح")
    
    if st.button("🗑️ مسح المحادثة بالكامل"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# ----------------- عرض رسائل الشات بتصميم الشركات الكبرى -----------------
for idx, msg in enumerate(st.session_state.messages):
    msg_id = msg.get("id", idx)
    
    if msg["role"] == "user":
        # كبسولة رسالة المستخدم
        user_escaped = json.dumps(msg['content'])
        st.markdown(f"""
        <div class="msg-wrapper">
            <div class="msg-user">
                {msg['content']}
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px; font-size: 0.72rem; color: #d8b4fe;">
                    <span>{msg.get('time', '')}</span>
                    <button class="action-btn" onclick='navigator.clipboard.writeText({user_escaped}); this.innerText="تم النسخ ✓";' style="padding: 2px 7px; font-size: 0.7rem;">📋 نسخ</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # كرت رسالة المساعد الذكي (Aura Card)
        clean_text_for_copy = json.dumps(re.sub(r'<.*?>', '', msg['content']))
        latency_str = f"⏱️ {msg.get('latency', 0.8)}s"
        time_str = msg.get('time', '')
        
        st.markdown(f"""
        <div class="msg-wrapper">
            <div class="msg-assistant-card">
                <div class="assistant-header">
                    <div class="glowing-orb" style="width: 26px; height: 26px;"></div>
                    <span style="font-weight: 700; font-size: 0.9rem; color: #e2e8f0;">Aura Assistant</span>
                </div>
                <div class="assistant-body">
                    {msg['content']}
                </div>
                <div class="msg-meta-bar">
                    <div class="meta-tags">
                        <span>{time_str}</span>
                        <span style="color: #64748b;">•</span>
                        <span>{latency_str}</span>
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <button class="action-btn" onclick='navigator.clipboard.writeText({clean_text_for_copy}); this.innerText="تم النسخ ✓";'>📋 نسخ</button>
                        <button class="action-btn" onclick='speakText_{msg_id}()'>🔊 استماع</button>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # مشغل الصوت التفاعلي للرسالة
        if msg.get("speech"):
            clean_speech = json.dumps(re.sub(r'<.*?>', '', msg["speech"]))
            audio_script = f"""
            <script>
                function speakText_{msg_id}() {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        const utt = new SpeechSynthesisUtterance({clean_speech});
                        utt.lang = 'ar-SA';
                        utt.rate = 1.0;
                        window.speechSynthesis.speak(utt);
                    }}
                }}
            </script>
            """
            components.html(audio_script, height=0)

        # عرض الرسم البياني إذا وجد بتنسيق أرجواني شفاف متناسق
        if msg.get("chart") and df is not None:
            c_info = msg["chart"]
            x_c = c_info.get("x_col")
            y_c = c_info.get("y_col")
            c_type = c_info.get("type", "bar")
            title = c_info.get("title", "رسم بياني")

            if x_c in df.columns and y_c in df.columns:
                agg = c_info.get("agg", "sum")
                if agg == "sum": plot_df = df.groupby(x_c)[y_c].sum().reset_index()
                elif agg == "mean": plot_df = df.groupby(x_c)[y_c].mean().reset_index()
                else: plot_df = df.groupby(x_c)[y_c].count().reset_index()

                if c_type == "pie":
                    fig = px.pie(plot_df, names=x_c, values=y_c, title=title, template="plotly_dark", color_discrete_sequence=['#a855f7', '#38bdf8', '#ec4899', '#34d399', '#f59e0b'])
                elif c_type == "line":
                    fig = px.line(plot_df, x=x_c, y=y_c, title=title, template="plotly_dark", color_discrete_sequence=['#a855f7'])
                else:
                    fig = px.bar(plot_df, x=x_c, y=y_c, title=title, template="plotly_dark", color_discrete_sequence=['#a855f7'])

                fig.update_layout(
                    paper_bgcolor="rgba(18, 12, 33, 0.6)",
                    plot_bgcolor="rgba(18, 12, 33, 0.6)",
                    font=dict(family="Cairo", size=12, color="#cbd5e1"),
                    margin=dict(l=10, r=10, t=35, b=10)
                )
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{msg_id}")

        # عرض الخريطة الذهنية
        if msg.get("mindmap"):
            m_code = msg["mindmap"].get("mermaid_code", "")
            if m_code:
                mermaid_html = f"""
                <div style="direction: ltr; background: rgba(18, 12, 33, 0.8); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 14px; padding: 12px; margin-top: 10px; text-align: center;">
                    <pre class="mermaid" style="background: transparent;">{m_code}</pre>
                </div>
                <script type="module">
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                    mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
                </script>
                """
                components.html(mermaid_html, height=300, scrolling=True)

        # زر إعادة التوليد لنفس السؤال
        if msg.get("raw_user_query"):
            if st.button("🔄 إعادة بناء الرد", key=f"regen_{msg_id}"):
                user_retry_query = msg["raw_user_query"]
                # حذف الإجابة السابقة وإعادة المحاولة
                st.session_state.messages = [m for m in st.session_state.messages if m.get("id") != msg_id]
                # تجهيز التوليد فوراً
                st.session_state.trigger_query = user_retry_query
                st.rerun()

# ----------------- معالجة السؤال المدخل -----------------
user_input = st.chat_input("اسأل Aura عن ميزانية السفر للإمارات...")

# التحقق من وجود إعادة توليد أو سؤال جديد
active_query = None
if user_input:
    active_query = user_input
elif "trigger_query" in st.session_state and st.session_state.trigger_query:
    active_query = st.session_state.trigger_query
    del st.session_state.trigger_query

if active_query:
    user_time = datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م")
    
    # إذا لم تكن إعادة توليد مسجلة مسبقاً
    if not any(m["role"] == "user" and m["content"] == active_query for m in st.session_state.messages[-1:]):
        st.session_state.messages.append({
            "id": len(st.session_state.messages),
            "role": "user",
            "content": active_query,
            "time": user_time
        })
        st.rerun()

    if not api_key:
        st.warning("⚠️ يرجى إدخال مفتاح Gemini API Key في القائمة الجانبية.")
    else:
        with st.spinner("🔮 جاري التحليل وصياغة الرد..."):
            try:
                # تلخيص بيانات ميزانية الإمارات
                summary_parts = []
                for s_name, s_df in all_sheets_data.items():
                    summary_parts.append(f"ورقة: {s_name}\nالأعمدة: {list(s_df.columns)}\n{s_df.to_string()}")
                    num_c = s_df.select_dtypes(include=['number']).columns.tolist()
                    if num_c:
                        summary_parts.append(f"المجاميع:\n{s_df[num_c].sum().to_string()}")
                data_summary = "\n\n".join(summary_parts)

                # سياق المحادثة السابقة
                history_list = []
                for h in st.session_state.messages[-5:-1]:
                    c_clean = re.sub(r'<.*?>', '', h['content'])
                    history_list.append(f"{h['role']}: {c_clean}")
                history_text = "\n".join(history_list)

                prompt = f"""
أنت Aura 2.0، مساعد مالي ذكي وخبير في ميزانية السفر للإمارات، بأسلوب عصري، راقٍ، وممتع.
بيانات الميزانية:
{data_summary}

سياق المحادثة السابقة:
{history_text}

سؤال المستخدم: "{active_query}"

قواعد تنسيق الألوان الإلزامية:
- ضع أي اسم بند أو عمود بين قوسين مربعين مثل: [[اسم البند]] (سيظهر بلون أزرق سماوي متوهج).
- ضع أي معادلة أو رقم أو تكلفة مالية بين قوسين مثل: {{{{المعادلة أو المبلغ}}}} (سيظهر بلون أخضر زمردي متوهج).
- لا تكتب أي كود HTML نهائياً، فقط استخدم [[...]] و {{{{...}}}}.

أجب حصراً بصيغة JSON نظيفة:
{{
    "answer_arabic": "الإجابة التحليلية الذكية باللغة العربية مع تطبيق [[البنود]] و {{{{المعادلات}}}}.",
    "speech_summary": "ملخص صوتي سريع خالي من أي رموز أو أقواس.",
    "chart": {{
        "has_chart": false,
        "type": "bar",
        "title": "عنوان",
        "x_col": "",
        "y_col": "",
        "agg": "sum"
    }},
    "mindmap": {{
        "has_mindmap": false,
        "mermaid_code": ""
    }}
}}
"""
                raw_resp, used_model, resp_latency = generate_ai_response(prompt, api_key)
                res_data = parse_safe_json(raw_resp)

                styled_ans = apply_custom_styling(res_data.get("answer_arabic", ""))
                speech_ans = res_data.get("speech_summary", "")
                chart_ans = res_data.get("chart") if res_data.get("chart", {}).get("has_chart") else None
                mindmap_ans = res_data.get("mindmap") if res_data.get("mindmap", {}).get("has_mindmap") else None

                ans_time = datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م")
                new_id = len(st.session_state.messages)

                st.session_state.messages.append({
                    "id": new_id,
                    "role": "assistant",
                    "content": styled_ans,
                    "speech": speech_ans,
                    "time": ans_time,
                    "latency": resp_latency,
                    "chart": chart_ans,
                    "mindmap": mindmap_ans,
                    "raw_user_query": active_query
                })

                st.rerun()

            except Exception as e:
                st.error(f"حدث خطأ أثناء معالجة السؤال: {e}")
