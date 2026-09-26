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

# ----------------- تصميم Gemini الراقي والأيقونات المتناسقة -----------------
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
        margin-bottom: 8px;
    }

    /* التمييز اللوني الراقي */
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

    /* شريط الوقت والمعلومات */
    .meta-time-text {
        font-size: 11.5px;
        color: #8e918f;
        direction: rtl;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* تنسيق أزرار الأيقونات لتكون شفافة وأنيقة تماماً كـ Gemini */
    div[data-testid="column"] button {
        background: transparent !important;
        border: none !important;
        color: #8e918f !important;
        padding: 4px 6px !important;
        border-radius: 6px !important;
        font-size: 15px !important;
        line-height: 1 !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="column"] button:hover {
        color: #e3e3e3 !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }

    /* شريط السؤال السفلي المدمج */
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

# ----------------- محرك الاتصال بـ Google Gemini الذكي -----------------
def generate_ai_response(prompt_text, user_api_key):
    from google import genai
    clean_key = user_api_key.strip()
    client = genai.Client(api_key=clean_key)
    
    # 1. فحص النماذج النشطة في حساب المستخدم الفعلي لتفادي خطأ 404
    available_models = []
    try:
        for m in client.models.list():
            clean_name = m.name.replace("models/", "")
            if "embed" not in clean_name.lower():
                available_models.append(clean_name)
    except Exception:
        pass

    # ترتيب أولويات النماذج
    preferred = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-3.8-flash', 'gemini-2.0-flash-exp']
    models_to_try = [p for p in preferred if p in available_models]
    for a in available_models:
        if a not in models_to_try:
            models_to_try.append(a)
            
    # قائمة احتياطية في حال تعذر جلب القائمة
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

# ----------------- تهيئة ذاكرة الشات -----------------
now_time = datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م")

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    welcome_msg = apply_gemini_styling(f"""أهلاً بك! أنا **Gemini**، محلل البيانات الذكي. تم ربط ملف [[{active_file_name}]] بنجاح.
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

# ----------------- عرض رسائل الشات بدون أي وسوم مكسورة -----------------
for idx, msg in enumerate(st.session_state.messages):
    msg_id = msg.get("id", idx)

    if msg["role"] == "user":
        u_content = msg['content']
        u_time = msg.get('time', now_time)

        # 1. كبسولة السؤال
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-start; direction: rtl; margin-bottom: 6px;">
            <div class="gemini-user-pill">{u_content}</div>
        </div>
        """, unsafe_allow_html=True)

        # 2. شريط الوقت وأزرار التحرير والنسخ
        col_t, col_b1, col_b2, _ = st.columns([2.5, 0.6, 0.6, 6.3])
        with col_t:
            st.markdown(f'<span class="meta-time-text">{u_time}</span>', unsafe_allow_html=True)
        with col_b1:
            if st.button("✏️", key=f"edit_btn_{msg_id}", help="تحرير السؤال"):
                st.session_state.edit_draft = u_content
                st.rerun()
        with col_b2:
            if st.button("📋", key=f"copy_u_{msg_id}", help="نسخ السؤال"):
                st.toast(f"تم نسخ السؤال: {u_content[:40]}...")

    else:
        ai_time = msg.get('time', now_time)
        latency_val = msg.get('latency', 0.4)
        raw_q = msg.get('raw_query')

        # 1. نص الإجابة النقي بدون تداخل وسوم
        st.markdown(f"""
        <div class="gemini-ai-text">{msg['content']}</div>
        """, unsafe_allow_html=True)

        # 2. شريط الوقت والأزرار جنب بعضها
        col_t, col_b1, col_b2, _ = st.columns([3.5, 0.6, 0.6, 5.3])
        with col_t:
            st.markdown(f'<span class="meta-time-text">{ai_time} • {latency_val} ثانية</span>', unsafe_allow_html=True)
        with col_b1:
            if raw_q and st.button("🔄", key=f"regen_btn_{msg_id}", help="إعادة بناء الرد"):
                st.session_state.pending_run = raw_q
                st.session_state.messages = [m for m in st.session_state.messages if m.get("id") != msg_id]
                st.rerun()
        with col_b2:
            if st.button("📋", key=f"copy_ai_{msg_id}", help="نسخ الرد"):
                clean_copy = re.sub(r'<.*?>', '', msg['content'])
                st.toast("تم نسخ الإجابة بنجاح ✓")

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

# ----------------- شريط السؤال السفلي -----------------
edit_placeholder = "اسأل Gemini عن أي معلومة في بياناتك ✦"
if "edit_draft" in st.session_state:
    st.info(f"✏️ جارٍ تعديل السؤال: {st.session_state.edit_draft}")

user_input = st.chat_input(placeholder=edit_placeholder)

active_prompt = None
if user_input:
    active_prompt = user_input
    if "edit_draft" in st.session_state:
        del st.session_state.edit_draft
elif "pending_run" in st.session_state:
    active_prompt = st.session_state.pending_run
    del st.session_state.pending_run

if active_prompt:
    current_time_str = datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م")
    
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
        with st.spinner("..."):
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
