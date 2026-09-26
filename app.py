import streamlit as st
import pandas as pd
import json
import os
import re
import time
from datetime import datetime
import streamlit.components.v1 as components
import plotly.express as px

# إعداد الصفحة العامة
st.set_page_config(
    page_title="Gemini Data AI",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------- تصميم Gemini الراقي بالأيقونات المتجهية (SVG) وبدون إيموجي شعبي -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&family=Google+Sans:wght@400;500;700&display=swap');

    body, .stApp {
        background-color: #131314 !important;
        color: #e3e3e3 !important;
        font-family: 'Cairo', 'Google Sans', sans-serif !important;
    }

    header[data-testid="stHeader"] { background-color: transparent !important; }
    #MainMenu, footer { display: none !important; }

    .main .block-container {
        max-width: 740px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 7.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin: 0 auto !important;
    }

    /* شريط علوي أنيق وديناميكي يوضح الملف الفعال */
    .top-meta-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background: #1e1f20;
        border-radius: 16px;
        margin-bottom: 22px;
        direction: rtl;
        font-size: 13px;
        color: #c4c7c5;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .active-file-tag {
        color: #a8c7fa;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* رسائل المستخدم */
    .chat-row-user {
        display: flex;
        justify-content: flex-start;
        direction: rtl;
        margin-bottom: 22px;
    }

    .gemini-user-pill {
        background-color: #282a2c;
        color: #e3e3e3;
        border-radius: 22px;
        padding: 10px 20px;
        font-size: 15px;
        font-weight: 500;
        line-height: 1.6;
        direction: rtl;
        text-align: right;
        display: inline-block;
        max-width: 85%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }

    /* إجابة الذكاء الاصطناعي بنمط نصي حر وناعم */
    .gemini-ai-container {
        direction: rtl;
        text-align: right;
        margin-bottom: 28px;
        color: #e3e3e3;
        font-size: 15.5px;
        line-height: 1.85;
    }

    .gemini-ai-text {
        color: #e3e3e3;
        font-size: 15.5px;
        line-height: 1.85;
        margin-bottom: 10px;
    }

    /* التمييز اللوني الراقي بدون بهرجة */
    .item-highlight {
        color: #a8c7fa !important;
        font-weight: 700;
    }

    .calc-highlight {
        color: #6dd58c !important;
        font-weight: 700;
        font-family: 'Google Sans', monospace !important;
        direction: ltr !important;
        display: inline-block;
    }

    /* شريط الأيقونات الراقي (SVG Icons) */
    .gemini-actions {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 10px;
        direction: ltr;
        justify-content: flex-end;
    }

    .svg-icon-btn {
        background: transparent;
        border: none;
        color: #8e918f;
        cursor: pointer;
        padding: 6px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }

    .svg-icon-btn:hover {
        color: #e3e3e3;
        background: rgba(255, 255, 255, 0.08);
    }

    .latency-pill {
        font-size: 11px;
        color: #8e918f;
        margin-right: 6px;
        font-family: sans-serif;
    }

    /* صندوق الإدخال المثبت في الأسفل بنمط Gemini */
    .stChatInputContainer {
        position: fixed !important;
        bottom: 18px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        max-width: 740px !important;
        width: calc(100% - 24px) !important;
        z-index: 999 !important;
    }

    .stChatInputContainer textarea {
        background-color: #1e1f20 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 28px !important;
        color: #e3e3e3 !important;
        font-family: 'Cairo', sans-serif !important;
        font-size: 15px !important;
        padding: 14px 22px !important;
        direction: rtl !important;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.5) !important;
    }

    .stChatInputContainer textarea:focus {
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    /* القائمة الجانبية (سهم الإعدادات) */
    section[data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-left: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- أيقونات SVG مرسومة فائقة الدقة -----------------
SVG_COPY = '''<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'''
SVG_REGEN = '''<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>'''
SVG_EDIT = '''<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>'''
SVG_SPARKLE = '''<svg width="16" height="16" viewBox="0 0 24 24" fill="#a8c7fa"><path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z"/></svg>'''
SVG_DATABASE = '''<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a8c7fa" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>'''

# ----------------- دوال التنسيق -----------------
def apply_gemini_styling(text):
    if not text: return ""
    text = re.sub(r'\[\[(.*?)\]\]', r'<span class="item-highlight">\1</span>', text)
    text = re.sub(r'\{\{(.*?)\}\}', r'<span class="calc-highlight">\1</span>', text)
    return text

def parse_safe_json(raw_text):
    clean = raw_text.strip()
    if clean.startswith("```json"): clean = clean[7:]
    elif clean.startswith("```"): clean = clean[3:]
    if clean.endswith("```"): clean = clean[:-3]
    clean = clean.strip()
    try: return json.loads(clean)
    except Exception: pass

    try:
        ans_match = re.search(r'"answer_arabic"\s*:\s*"(.*?)"(\s*,\s*"|\s*})', clean, re.DOTALL)
        if ans_match:
            ans = ans_match.group(1).replace('\\"', '"').replace('\\n', '\n')
            return {"answer_arabic": ans, "chart": None, "mindmap": None}
    except Exception: pass

    return {"answer_arabic": clean, "chart": None, "mindmap": None}

# ----------------- محرك الاتصال بـ Google Gemini -----------------
def generate_ai_response(prompt_text, user_api_key):
    from google import genai
    client = genai.Client(api_key=user_api_key)
    models = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-3.8-flash', 'gemini-1.5-pro']
    
    last_err = None
    for m in models:
        try:
            t0 = time.time()
            resp = client.models.generate_content(model=m, contents=prompt_text)
            if resp and resp.text:
                return resp.text, round(time.time() - t0, 1)
        except Exception as err:
            last_err = err
            continue
    raise Exception(f"خطأ في الاتصال: {last_err}")

# ----------------- إدارة الملفات ديناميكياً (أي ملف إكسل أو CSV) -----------------
df = None
all_sheets = {}
active_file_name = "لا يوجد ملف محدد"

# 1. فحص القائمة الجانبية إذا قام المستخدم برفع ملف جديد
if "api_key" not in st.session_state:
    st.session_state.api_key = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.markdown("### ⚙️ إعدادات Gemini والملفات")
    input_key = st.text_input(
        "مفتاح Google Gemini API Key:",
        value=st.session_state.api_key,
        type="password",
        placeholder="AIzaSy..."
    )
    if input_key != st.session_state.api_key:
        st.session_state.api_key = input_key
        st.success("✅ تم حفظ المفتاح")
        
    st.markdown("---")
    st.markdown("### 📁 إدارة مصادر البيانات")
    uploaded_file = st.file_uploader("ارفع أي ملف Excel أو CSV:", type=["xlsx", "xls", "csv"])
    
    if st.button("🗑️ مسح المحادثة بالكامل"):
        st.session_state.messages = []
        st.rerun()

# تحديد مصدر البيانات إما المرفوع حديثاً أو ملفات المجلد
if uploaded_file is not None:
    try:
        active_file_name = uploaded_file.name
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            all_sheets["البيانات"] = df
        else:
            xl = pd.ExcelFile(uploaded_file)
            for s in xl.sheet_names:
                all_sheets[s] = pd.read_excel(uploaded_file, sheet_name=s)
            df = all_sheets[xl.sheet_names[0]]
    except Exception as e:
        st.sidebar.error(f"خطأ في قراءة الملف: {e}")
else:
    # البحث التلقائي عن أي ملف إكسل موجود في المشروع
    available_files = [f for f in os.listdir(".") if f.endswith(('.xlsx', '.csv')) and not f.startswith('.')]
    if available_files:
        chosen_file = available_files[0]
        # إعطاء أولوية لأي ملف إكسل متاح
        active_file_name = chosen_file
        try:
            if chosen_file.endswith('.csv'):
                df = pd.read_csv(chosen_file)
                all_sheets["البيانات"] = df
            else:
                xl = pd.ExcelFile(chosen_file)
                for s in xl.sheet_names:
                    all_sheets[s] = pd.read_excel(chosen_file, sheet_name=s)
                df = all_sheets[xl.sheet_names[0]]
        except Exception:
            pass

# عرض عينة الجدول داخل القائمة الجانبية
with st.sidebar:
    if df is not None:
        st.markdown(f"**البيانات النشطة: {active_file_name}** ({len(df)} صف)")
        st.dataframe(df.head(10), use_container_width=True)

# ----------------- تهيئة ذاكرة الشات -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# إذا كانت المحادثة فارغة، عرض رسالة ترحيبية ذكية ومتكيفة مع اسم الملف
if len(st.session_state.messages) == 0:
    welcome_text = apply_gemini_styling(f"""أهلاً بك! أنا **Gemini**، محلل البيانات الذكي.
تم ربط ملف [[{active_file_name}]] بنجاح.
اسألني عن أي تفاصيل، تحليلات، مقارنات إحصائية، أو خطط عمل واستراتيجيات مبنية على بياناتك.""")
    st.session_state.messages.append({
        "id": 0,
        "role": "assistant",
        "content": welcome_text,
        "latency": 0.3,
        "chart": None,
        "mindmap": None,
        "raw_query": None
    })

# ----------------- شريط الحالة العلوي النظيف -----------------
st.markdown(f"""
<div class="top-meta-bar">
    <div class="active-file-tag">
        {SVG_DATABASE}
        <span>الملف الحالي: {active_file_name}</span>
    </div>
    <div style="display: flex; align-items: center; gap: 6px; font-size: 12px; color: #8e918f;">
        <span>{len(df) if df is not None else 0} صف</span>
        <span>•</span>
        <span>{SVG_SPARKLE} Gemini</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- عرض رسائل الشات -----------------
for idx, msg in enumerate(st.session_state.messages):
    msg_id = msg.get("id", idx)

    if msg["role"] == "user":
        u_content = msg['content']
        st.markdown(f"""
        <div class="chat-row-user">
            <div class="gemini-user-pill">
                {u_content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        clean_text_copy = json.dumps(re.sub(r'<.*?>', '', msg['content']))
        latency_val = msg.get('latency', 0.5)
        raw_q = msg.get('raw_query', '')

        st.markdown(f"""
        <div class="gemini-ai-container">
            <div class="gemini-ai-text">{msg['content']}</div>
            <div class="gemini-actions">
                <span class="latency-pill">{latency_val}s</span>
                <button class="svg-icon-btn" onclick='navigator.clipboard.writeText({clean_text_copy}); this.innerHTML="✓";' title="نسخ">{SVG_COPY}</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # زر إعادة الرد وزر تعديل السؤال بأيقونات راقية
        if raw_q:
            c_r1, c_r2, _ = st.columns([1.5, 1.5, 7])
            with c_r1:
                if st.button("🔄 إعادة الرد", key=f"btn_regen_{msg_id}"):
                    st.session_state.trigger_query = raw_q
                    st.session_state.messages = [m for m in st.session_state.messages if m.get("id") != msg_id]
                    st.rerun()
            with c_r2:
                if st.button("✏️ تحرير السؤال", key=f"btn_edit_{msg_id}"):
                    st.session_state.edit_draft = raw_q
                    st.rerun()

        # الرسم البياني
        if msg.get("chart") and df is not None:
            c = msg["chart"]
            xc, yc = c.get("x_col"), c.get("y_col")
            if xc in df.columns and yc in df.columns:
                pdf = df.groupby(xc)[yc].sum().reset_index()
                fig = px.pie(pdf, names=xc, values=yc, title=c.get("title", ""), template="plotly_dark", color_discrete_sequence=['#a8c7fa', '#6dd58c', '#d3bbff', '#f8d866'])
                fig.update_layout(paper_bgcolor="#131314", plot_bgcolor="#131314", font=dict(family="Cairo", size=12, color="#e3e3e3"), margin=dict(l=10, r=10, t=35, b=10))
                st.plotly_chart(fig, use_container_width=True, key=f"c_{msg_id}")

        # الخريطة الذهنية
        if msg.get("mindmap") and msg["mindmap"].get("mermaid_code"):
            mcode = msg["mindmap"]["mermaid_code"]
            components.html(f"""
            <div style="direction: ltr; background: #1e1f20; border-radius: 12px; padding: 12px; margin-bottom: 20px; text-align: center;">
                <pre class="mermaid" style="background: transparent;">{mcode}</pre>
            </div>
            <script type="module">
                import m from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                m.initialize({{ startOnLoad: true, theme: 'dark' }});
            </script>
            """, height=280)

# ----------------- شريط السؤال السفلي مع زر الإرسال المدمج -----------------
# استعادة السؤال عند الضغط على "تحرير السؤال"
default_placeholder = "اسأل Gemini عن أي معلومة في بياناتك ✦"
if "edit_draft" in st.session_state:
    st.info(f"✏️ جاري تحرير سؤالك: {st.session_state.edit_draft}")

user_input = st.chat_input(placeholder=default_placeholder)

active_prompt = None
if user_input:
    active_prompt = user_input
    if "edit_draft" in st.session_state:
        del st.session_state.edit_draft
elif "trigger_query" in st.session_state:
    active_prompt = st.session_state.trigger_query
    del st.session_state.trigger_query

if active_prompt:
    st.session_state.messages.append({
        "id": len(st.session_state.messages),
        "role": "user",
        "content": active_prompt
    })

    if not st.session_state.api_key:
        st.session_state.messages.append({
            "id": len(st.session_state.messages),
            "role": "assistant",
            "content": "⚠️ يرجى إدخال مفتاح Google Gemini API Key من سهم الإعدادات الجانبي أولاً للبدء.",
            "latency": 0.0,
            "chart": None,
            "mindmap": None,
            "raw_query": active_prompt
        })
        st.rerun()
    else:
        with st.spinner("..."):
            try:
                # تلخيص بيانات الملف الفعال بدقة أياً كان نوعه (ميزانية، مبيعات، موظفين...)
                summary_parts = []
                for s_name, s_df in all_sheets.items():
                    summary_parts.append(f"ورقة/جدول: {s_name}\nالأعمدة: {list(s_df.columns)}\nعينة من البيانات:\n{s_df.head(15).to_string()}")
                    num_c = s_df.select_dtypes(include=['number']).columns.tolist()
                    if num_c: summary_parts.append(f"إجماليات وإحصائيات:\n{s_df[num_c].describe().to_string()}")
                data_summary = "\n\n".join(summary_parts)

                hist = []
                for h in st.session_state.messages[-5:-1]:
                    hist.append(f"{h['role']}: {re.sub(r'<.*?>', '', h['content'])}")
                history_text = "\n".join(hist)

                prompt = f"""
أنت Gemini، مساعد ذكي ومحلل بيانات محترف متخصص في قراءة وتحليل أي جدول بيانات.
البيانات المتاحة من ملف ({active_file_name}):
{data_summary}

المحادثة السابقة:
{history_text}

سؤال المستخدم: "{active_prompt}"

قواعد التلوين:
- أي اسم عمود أو بند: ضعه بين [[اسم البند]] (سيتحول تلقائياً إلى اللون الأزرق السماوي).
- أي رقم أو حساب مالي: ضعه بين {{{{الرقم أو المعادلة}}}} (سيتحول تلقائياً إلى اللون الأخضر الهادئ).

أجب حصراً بصيغة JSON نظيفة بدون أي نص خارجي:
{{
    "answer_arabic": "الإجابة التلقائية المباشرة بأسلوب شات Gemini مع [[البنود]] و {{{{الأرقام}}}}.",
    "chart": {{ "has_chart": false, "type": "bar", "title": "", "x_col": "", "y_col": "" }},
    "mindmap": {{ "has_mindmap": false, "mermaid_code": "" }}
}}
"""
                raw_ans, latency = generate_ai_response(prompt, st.session_state.api_key)
                parsed = parse_safe_json(raw_ans)

                st.session_state.messages.append({
                    "id": len(st.session_state.messages),
                    "role": "assistant",
                    "content": apply_gemini_styling(parsed.get("answer_arabic", "")),
                    "latency": latency,
                    "chart": parsed.get("chart") if parsed.get("chart", {}).get("has_chart") else None,
                    "mindmap": parsed.get("mindmap") if parsed.get("mindmap", {}).get("has_mindmap") else None,
                    "raw_query": active_prompt
                })

            except Exception as e:
                st.session_state.messages.append({
                    "id": len(st.session_state.messages),
                    "role": "assistant",
                    "content": f"حدث خطأ أثناء معالجة السؤال: {e}",
                    "latency": 0.0,
                    "chart": None,
                    "mindmap": None,
                    "raw_query": active_prompt
                })

        st.rerun()
