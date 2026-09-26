import streamlit as st
import pandas as pd
import json
import os
import re
import time
from datetime import datetime
import streamlit.components.v1 as components
import plotly.express as px

# إعداد الصفحة لتطابق واجهة Gemini
st.set_page_config(
    page_title="Gemini",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------- تصميم مطابق تماماً لـ Google Gemini -----------------
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
        padding-bottom: 7rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin: 0 auto !important;
    }

    /* كبسولة رسالة المستخدم */
    .chat-row-user {
        display: flex;
        justify-content: flex-start;
        direction: rtl;
        margin-bottom: 22px;
    }

    .gemini-user-pill {
        background-color: #282a2c;
        color: #e3e3e3;
        border-radius: 24px;
        padding: 10px 20px;
        font-size: 15px;
        font-weight: 500;
        line-height: 1.6;
        direction: rtl;
        text-align: right;
        display: inline-block;
        max-width: 85%;
        box-shadow: 0 1px 4px rgba(0,0,0,0.25);
    }

    /* رد الذكاء الاصطناعي بنمط Gemini الحر */
    .gemini-ai-container {
        direction: rtl;
        text-align: right;
        margin-bottom: 30px;
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

    /* شريط أدوات Gemini الخفيف */
    .gemini-actions {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 8px;
        direction: ltr;
        justify-content: flex-end;
    }

    .gemini-icon-btn {
        background: transparent;
        border: none;
        color: #8e918f;
        cursor: pointer;
        padding: 4px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        transition: color 0.2s;
    }

    .gemini-icon-btn:hover { color: #e3e3e3; }

    .latency-pill {
        font-size: 11px;
        color: #8e918f;
        margin-right: 4px;
    }

    /* صندوق الإدخال العائم */
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
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
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
        ans_match = re.search(r'"answer_arabic"\s*:\s*"(.*?)"\s*,\s*"speech_summary"', clean, re.DOTALL)
        if ans_match:
            ans = ans_match.group(1).replace('\\"', '"').replace('\\n', '\n')
            return {"answer_arabic": ans, "speech_summary": ans[:80], "chart": None, "mindmap": None}
    except Exception: pass

    return {"answer_arabic": clean, "speech_summary": clean[:80], "chart": None, "mindmap": None}

# ----------------- دالة الاتصال بـ Google Gemini -----------------
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

# ----------------- قراءة ميزانية الإمارات -----------------
df = None
all_sheets = {}
default_files = ["ميزانيه السفر للامارات.xlsx", "budget_uae.xlsx", "sample_data.csv"]

for fname in default_files:
    if os.path.exists(fname):
        try:
            if fname.endswith('.csv'):
                df = pd.read_csv(fname)
                all_sheets["الرئيسية"] = df
            else:
                xl = pd.ExcelFile(fname)
                for s in xl.sheet_names:
                    all_sheets[s] = pd.read_excel(fname, sheet_name=s)
                df = all_sheets[xl.sheet_names[0]]
            break
        except Exception:
            continue

# ----------------- إدارة المفتاح والجلسة بأمان -----------------
if "api_key" not in st.session_state:
    st.session_state.api_key = st.secrets.get("GEMINI_API_KEY", "")

# القائمة الجانبية (سهم الإعدادات)
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
    if df is not None:
        st.markdown(f"**📊 ملف ميزانية الإمارات ({len(df)} بند):**")
        st.dataframe(df, use_container_width=True)
        
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# ----------------- تهيئة ذاكرة الشات -----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "id": 0,
            "role": "assistant",
            "content": apply_gemini_styling("""أهلاً بك! تم ربط [[ميزانية السفر للإمارات]] بالكامل.
يمكنك سؤالي عن أي مقارنة، تفاصيل التكاليف، أو خطط التوفير:
- تظهر [[أسماء البنود]] بلون أزرق خفيف.
- وتظهر {{المعادلات والأرقام}} بلون أخضر هادئ."""),
            "speech": "أهلاً بك! تم ربط ميزانية السفر للإمارات. اسألني عن أي بند وسأحسبه لك فوراً.",
            "latency": 0.4,
            "chart": None,
            "mindmap": None,
            "raw_query": None
        }
    ]

# ----------------- ودجت الصوت النحيف -----------------
voice_widget = """
<div style="direction: rtl; text-align: center; margin-bottom: 16px;">
    <button id="micBtn" onclick="toggleMic()" style="
        background: #1e1f20;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #c4c7c5;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 13px;
        font-family: 'Cairo', sans-serif;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    ">
        <span>🎙️</span>
        <span id="micLabel">تحدث بالصوت</span>
    </button>
    <span id="micStatus" style="color: #8e918f; font-size: 12px; margin-right: 8px;"></span>
</div>
<script>
    let rec = null, isR = false;
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        rec = new SR(); rec.lang = 'ar-SA';
        rec.onstart = () => { document.getElementById('micLabel').innerText = 'نسمع صوتك...'; };
        rec.onresult = (e) => {
            navigator.clipboard.writeText(e.results[0][0].transcript);
            document.getElementById('micStatus').innerText = 'تم نسخ كلامك للصقه في الشات ✓';
        };
        rec.onend = () => { document.getElementById('micLabel').innerText = 'تحدث بالصوت'; };
    }
    function toggleMic() {
        if (!rec) { alert('المتصفح لا يدعم المايك'); return; }
        if (!isR) { rec.start(); isR = true; } else { rec.stop(); isR = false; }
    }
</script>
"""
components.html(voice_widget, height=36)

# ----------------- عرض رسائل الشات -----------------
for idx, msg in enumerate(st.session_state.messages):
    msg_id = msg.get("id", idx)

    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-row-user">
            <div class="gemini-user-pill">
                {msg['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        clean_text_copy = json.dumps(re.sub(r'<.*?>', '', msg['content']))
        latency_val = msg.get('latency', 0.5)

        st.markdown(f"""
        <div class="gemini-ai-container">
            <div class="gemini-ai-text">{msg['content']}</div>
            <div class="gemini-actions">
                <span class="latency-pill">{latency_val}s</span>
                <button class="gemini-icon-btn" onclick='navigator.clipboard.writeText({clean_text_copy}); this.innerText="✓";' title="نسخ">📋</button>
                <button class="gemini-icon-btn" onclick='speak_{msg_id}()' title="استماع">🔊</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if msg.get("speech"):
            spk_str = json.dumps(re.sub(r'<.*?>', '', msg["speech"]))
            components.html(f"""
            <script>
                function speak_{msg_id}() {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        const u = new SpeechSynthesisUtterance({spk_str});
                        u.lang = 'ar-SA';
                        window.speechSynthesis.speak(u);
                    }}
                }}
            </script>
            """, height=0)

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
            <div style="direction: ltr; background: #1e1f20; border-radius: 12px; padding: 10px; margin-bottom: 20px; text-align: center;">
                <pre class="mermaid" style="background: transparent;">{mcode}</pre>
            </div>
            <script type="module">
                import m from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                m.initialize({{ startOnLoad: true, theme: 'dark' }});
            </script>
            """, height=280)

# ----------------- استقبال وتوليد الرد فوراً بدون توقف -----------------
user_input = st.chat_input("اسأل Gemini عن ميزانية السفر للإمارات ✦")

if user_input:
    # 1. إضافة سؤال المستخدم فوراً للذاكرة
    st.session_state.messages.append({
        "id": len(st.session_state.messages),
        "role": "user",
        "content": user_input
    })

    # 2. التحقق من وجود مفتاح الـ API
    if not st.session_state.api_key:
        st.session_state.messages.append({
            "id": len(st.session_state.messages),
            "role": "assistant",
            "content": "⚠️ يرجى إدخال مفتاح الـ API من سهم الإعدادات الجانبي للبدء في الإجابة.",
            "speech": "يرجى إدخال مفتاح الـ API من سهم الإعدادات الجانبي.",
            "latency": 0.0,
            "chart": None,
            "mindmap": None,
            "raw_query": user_input
        })
        st.rerun()
    else:
        # 3. استدعاء الذكاء الاصطناعي مباشرة دون Rerun مسبق يضيع الإدخال
        with st.spinner("..."):
            try:
                summary_parts = []
                for s, sdf in all_sheets.items():
                    summary_parts.append(f"ورقة: {s}\nالأعمدة: {list(sdf.columns)}\n{sdf.to_string()}")
                    num_c = sdf.select_dtypes(include=['number']).columns.tolist()
                    if num_c: summary_parts.append(f"مجموع: {sdf[num_c].sum().to_string()}")
                data_summary = "\n\n".join(summary_parts)

                hist = []
                for h in st.session_state.messages[-5:-1]:
                    hist.append(f"{h['role']}: {re.sub(r'<.*?>', '', h['content'])}")
                history_text = "\n".join(hist)

                prompt = f"""
أنت Gemini، مساعد ذكي ومحلل لميزانية السفر للإمارات.
بيانات الميزانية:
{data_summary}

المحادثة السابقة:
{history_text}

السؤال: "{user_input}"

قواعد التلوين:
- أي اسم بند أو عمود: ضعه بين [[اسم البند]] (سيصبح أزرق).
- أي رقم أو معادلة: ضعه بين {{{{الرقم أو المعادلة}}}} (سيصبح أخضر).

أجب حصراً بـ JSON نظيف:
{{
    "answer_arabic": "الإجابة التلقائية المباشرة كشات Gemini مع [[البنود]] و {{{{الأرقام}}}}.",
    "speech_summary": "ملخص صوتي قصير جداً سطر واحد.",
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
                    "speech": parsed.get("speech_summary", ""),
                    "latency": latency,
                    "chart": parsed.get("chart") if parsed.get("chart", {}).get("has_chart") else None,
                    "mindmap": parsed.get("mindmap") if parsed.get("mindmap", {}).get("has_mindmap") else None,
                    "raw_query": user_input
                })

            except Exception as e:
                st.session_state.messages.append({
                    "id": len(st.session_state.messages),
                    "role": "assistant",
                    "content": f"حدث خطأ أثناء معالجة السؤال: {e}",
                    "speech": "",
                    "latency": 0.0,
                    "chart": None,
                    "mindmap": None,
                    "raw_query": user_input
                })

        # 4. تحديث الصفحة بعد اكتمال الإجابة لعرضها فوراً
        st.rerun()
