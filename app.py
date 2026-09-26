import streamlit as st
import pandas as pd
import json
import os
import re
import time
from datetime import datetime
import streamlit.components.v1 as components
import plotly.express as px

# إعداد الصفحة بنمط Google Gemini الرسمي
st.set_page_config(
    page_title="Gemini Data AI",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------- تصميم Gemini الراقي بالأيقونات الفيكتور وبدون أي مربعات -----------------
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

    /* شريط البيانات العلوي */
    .top-meta-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 14px;
        background: #1e1f20;
        border-radius: 14px;
        margin-bottom: 24px;
        direction: rtl;
        font-size: 13px;
        color: #c4c7c5;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* كبسولة سؤال المستخدم */
    .chat-row-user {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
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

    /* نص إجابة الذكاء الاصطناعي بنمط Gemini الحر */
    .gemini-ai-text {
        color: #e3e3e3;
        font-size: 15.5px;
        line-height: 1.85;
        direction: rtl;
        text-align: right;
        margin-bottom: 6px;
    }

    /* التمييز اللوني الراقي للبيانات */
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

    /* شريط الأيقونات والتوقيت المدمج بدون أي مربعات */
    .action-bar-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 4px;
        margin-bottom: 22px;
        direction: rtl;
    }

    .meta-time-text {
        font-size: 11.5px;
        color: #727775;
        direction: rtl;
        font-family: 'Cairo', sans-serif;
    }

    .action-icons-group {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        direction: ltr;
    }

    /* روابط الأيقونات الفيكتور النقية تماماً بدون أي حدود أو خلفيات */
    a.gemini-svg-btn {
        text-decoration: none !important;
        color: #8e918f !important;
        background: transparent !important;
        border: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 3px 6px !important;
        border-radius: 6px !important;
        cursor: pointer !important;
        transition: color 0.15s ease, background 0.15s ease !important;
    }

    a.gemini-svg-btn:hover {
        color: #e3e3e3 !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }

    /* صندوق تعديل السؤال داخل الرسالة */
    .edit-box-container {
        background: #1e1f20;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 12px;
        margin: 8px 0 16px 0;
        direction: rtl;
    }

    /* صندوق الإدخال السفلي المثبت */
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

    section[data-testid="stSidebar"] {
        background-color: #1e1f20 !important;
        border-left: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- أيقونات فيكتور SVG مرسومة فاخرة (Outlines) -----------------
SVG_COPY = '''<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'''
SVG_REGEN = '''<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>'''
SVG_EDIT = '''<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>'''

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
    clean_key = user_api_key.strip()
    client = genai.Client(api_key=clean_key)
    
    # 1. استكشاف النماذج النشطة في حساب المستخدم الفعلي لتفادي خطأ 404
    available_models = []
    try:
        for m in client.models.list():
            clean_name = m.name.replace("models/", "")
            if "embed" not in clean_name.lower():
                available_models.append(clean_name)
    except Exception:
        pass

    preferred = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-3.8-flash', 'gemini-2.0-flash-exp']
    models_to_try = [p for p in preferred if p in available_models]
    for a in available_models:
        if a not in models_to_try:
            models_to_try.append(a)
            
    if not models_to_try:
        models_to_try = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-3.8-flash']

    errors = []
    for model_name in models_to_try:
        try:
            t0 = time.time()
            resp = client.models.generate_content(model=model_name, contents=prompt_text)
            if resp and resp.text:
                return resp.text, round(time.time() - t0, 1)
        except Exception as err:
            errors.append(f"[{model_name}: {err}]")
            continue
            
    raise Exception("تعذر الاتصال بالنماذج:\n" + "\n".join(errors[:2]))

# ----------------- إدارة الملفات ديناميكياً -----------------
df = None
all_sheets = {}
active_file_name = "لا يوجد ملف"

if "api_key" not in st.session_state:
    st.session_state.api_key = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.markdown("### ⚙️ إعدادات Gemini والبيانات")
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

# تحميل الملف الفعال
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
    available_files = [f for f in os.listdir(".") if f.endswith(('.xlsx', '.csv')) and not f.startswith('.')]
    if available_files:
        chosen_file = available_files[0]
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

with st.sidebar:
    if df is not None:
        st.markdown(f"**الملف النشط: {active_file_name}** ({len(df)} صف)")
        st.dataframe(df.head(10), use_container_width=True)

# ----------------- معالجة أوامر الأزرار عبر الرابط (بدون أي تعليق) -----------------
# 1. فحص أمر إعادة الرد
if "action" in st.query_params and st.query_params["action"] == "regen":
    try:
        r_id = int(st.query_params.get("id", 0))
        for i, m in enumerate(st.session_state.get("messages", [])):
            if m.get("id") == r_id and m.get("raw_query"):
                # استخراج السؤال وحذف الإجابة القديمة
                st.session_state.pending_prompt = m["raw_query"]
                st.session_state.messages.pop(i)
                break
    except Exception:
        pass
    st.query_params.clear()
    st.rerun()

# 2. فحص أمر تعديل السؤال
if "action" in st.query_params and st.query_params["action"] == "edit":
    try:
        e_id = int(st.query_params.get("id", 0))
        st.session_state.editing_msg_id = e_id
    except Exception:
        pass
    st.query_params.clear()
    st.rerun()

# 3. فحص أمر النسخ
if "action" in st.query_params and st.query_params["action"] == "copy":
    st.toast("📋 تم تحديد النص للنسخ")
    st.query_params.clear()

# ----------------- تهيئة ذاكرة الشات -----------------
now_time = datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م")

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    welcome_msg = apply_gemini_styling(f"""أهلاً بك! أنا **Gemini**، مساعدك ومحلل بياناتك المحترف. تم ربط ملف [[{active_file_name}]] بنجاح.
اسألني عن أي تفاصيل، مقارنات إحصائية، أو خطط عمل واستراتيجيات مبنية على بياناتك.""")
    st.session_state.messages = [
        {
            "id": 0,
            "role": "assistant",
            "content": welcome_msg,
            "time": now_time,
            "latency": 0.3,
            "chart": None,
            "mindmap": None,
            "raw_query": None
        }
    ]

# ----------------- شريط الحالة العلوي -----------------
num_rows = len(df) if df is not None else 0
st.markdown(f"""
<div class="top-meta-bar">
    <div style="color: #a8c7fa; font-weight: 600;">📁 الملف الحالي: {active_file_name}</div>
    <div style="font-size: 12px; color: #8e918f;">{num_rows} صف • Gemini ✦</div>
</div>
""", unsafe_allow_html=True)

# ----------------- عرض رسائل الشات بالأيقونات الفيكتور وبدون أي مربعات -----------------
for idx, msg in enumerate(st.session_state.messages):
    msg_id = msg.get("id", idx)

    if msg["role"] == "user":
        u_content = msg['content']
        u_time = msg.get('time', now_time)

        # التحقق مما إذا كان المستخدم يحرر هذا السؤال حالياً
        if st.session_state.get("editing_msg_id") == msg_id:
            st.markdown('<div class="edit-box-container">', unsafe_allow_html=True)
            st.markdown(f"**✏️ تعديل السؤال ({u_time}):**")
            edited_text = st.text_area(
                "عدل سؤالك هنا:",
                value=u_content,
                key=f"edit_area_{msg_id}",
                label_visibility="collapsed"
            )
            col_save, col_cancel = st.columns([1, 1])
            with col_save:
                if st.button("حفظ وإرسال ✦", key=f"btn_save_{msg_id}", use_container_width=True):
                    # 1. تحديث نص السؤال
                    msg['content'] = edited_text
                    # 2. حذف الردود السابقة التي تلي هذا السؤال ليبدأ الرد الجديد من هذه النقطة
                    st.session_state.messages = st.session_state.messages[:idx + 1]
                    # 3. إلغاء وضع التعديل
                    st.session_state.editing_msg_id = None
                    # 4. إرسال السؤال الجديد للنموذج
                    st.session_state.pending_prompt = edited_text
                    st.rerun()
            with col_cancel:
                if st.button("إلغاء", key=f"btn_cancel_{msg_id}", use_container_width=True):
                    st.session_state.editing_msg_id = None
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # كبسولة السؤال العادية مع أيقونات النسخ والتحرير
            st.markdown(f"""
            <div class="chat-row-user">
                <div class="gemini-user-pill">{u_content}</div>
                <div class="action-bar-container">
                    <span class="meta-time-text">{u_time}</span>
                    <div class="action-icons-group">
                        <a href="?action=copy&id={msg_id}" target="_self" class="gemini-svg-btn" title="نسخ">{SVG_COPY}</a>
                        <a href="?action=edit&id={msg_id}" target="_self" class="gemini-svg-btn" title="تحرير السؤال">{SVG_EDIT}</a>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        ai_time = msg.get('time', now_time)
        latency_val = msg.get('latency', 0.4)
        raw_q = msg.get('raw_query')

        # إجابة الذكاء الاصطناعي مع أيقونات النسخ وإعادة الرد
        regen_link = f'<a href="?action=regen&id={msg_id}" target="_self" class="gemini-svg-btn" title="إعادة التفكير وبناء الرد">{SVG_REGEN}</a>' if raw_q else ''

        st.markdown(f"""
        <div class="gemini-ai-text">{msg['content']}</div>
        <div class="action-bar-container">
            <span class="meta-time-text">{ai_time} • {latency_val} ثانية</span>
            <div class="action-icons-group">
                <a href="?action=copy&id={msg_id}" target="_self" class="gemini-svg-btn" title="نسخ">{SVG_COPY}</a>
                {regen_link}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # الرسم البياني إن وجد
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

# ----------------- استقبال وتوليد الأسئلة -----------------
user_input = st.chat_input(placeholder="اسأل Gemini عن أي معلومة في بياناتك ✦")

active_prompt = None
if user_input:
    active_prompt = user_input
elif "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    active_prompt = st.session_state.pending_prompt
    del st.session_state.pending_prompt

if active_prompt:
    current_time_str = datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م")
    
    # إضافة السؤال إلى المحادثة إذا لم يكن مضافاً بالفعل
    if not any(m["role"] == "user" and m["content"] == active_prompt for m in st.session_state.messages[-1:]):
        st.session_state.messages.append({
            "id": len(st.session_state.messages),
            "role": "user",
            "content": active_prompt,
            "time": current_time_str
        })

    if not st.session_state.api_key:
        st.session_state.messages.append({
            "id": len(st.session_state.messages),
            "role": "assistant",
            "content": "⚠️ يرجى إدخال مفتاح Google Gemini API Key من سهم الإعدادات الجانبي أولاً للبدء.",
            "time": current_time_str,
            "latency": 0.0,
            "chart": None,
            "mindmap": None,
            "raw_query": active_prompt
        })
        st.rerun()
    else:
        with st.spinner("Gemini يفكر في الإجابة ويحلل البيانات..."):
            try:
                summary_parts = []
                for s_name, s_df in all_sheets.items():
                    summary_parts.append(f"جدول: {s_name}\nالأعمدة: {list(s_df.columns)}\nعينة من البيانات:\n{s_df.head(15).to_string()}")
                    num_c = s_df.select_dtypes(include=['number']).columns.tolist()
                    if num_c: summary_parts.append(f"إجماليات:\n{s_df[num_c].describe().to_string()}")
                data_summary = "\n\n".join(summary_parts)

                hist = []
                for h in st.session_state.messages[-5:-1]:
                    hist.append(f"{h['role']}: {re.sub(r'<.*?>', '', h['content'])}")
                history_text = "\n".join(hist)

                prompt = f"""
أنت Gemini، مساعد ذكي ومحلل بيانات محترف متخصص في قراءة وتحليل أي جدول بيانات بدقة متناهية.
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
                    "time": datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م"),
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
                    "time": datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م"),
                    "latency": 0.0,
                    "chart": None,
                    "mindmap": None,
                    "raw_query": active_prompt
                })

        st.rerun()
