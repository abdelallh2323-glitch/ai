import streamlit as st
import pandas as pd
import json
import os
import re
import time
from datetime import datetime
import streamlit.components.v1 as components
import plotly.express as px

# ضبط الصفحة
st.set_page_config(
    page_title="Aura • ميزانية الإمارات",
    page_icon="🇦🇪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------- تصميم نقي ومضغوط للموبايل والكمبيوتر (Mobile-First Minimalist) -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@500;700&display=swap');

    /* إخفاء زوائد ستريمليت */
    #MainMenu, header, footer { display: none !important; height: 0 !important; }

    * { box-sizing: border-box; }

    body, .stApp {
        background: #090714 !important;
        color: #f1f5f9;
        font-family: 'Cairo', sans-serif !important;
    }

    /* الحاوية الرئيسية مدمجة ونحيفة */
    .main .block-container {
        max-width: 680px !important;
        padding: 0.5rem 0.8rem 5rem 0.8rem !important;
        margin: 0 auto !important;
    }

    /* شريط علوي نحيف جداً (46px فقط) مثل Telegram و ChatGPT */
    .compact-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(22, 14, 40, 0.95);
        border: 1px solid rgba(168, 85, 247, 0.2);
        border-radius: 14px;
        padding: 8px 14px;
        margin-bottom: 12px;
        direction: rtl;
    }

    .topbar-title {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .orb-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #a855f7;
        box-shadow: 0 0 10px #a855f7;
        flex-shrink: 0;
    }

    .title-text {
        font-weight: 700;
        font-size: 0.9rem;
        color: #f8fafc;
        margin: 0;
    }

    .badge-tag {
        background: rgba(168, 85, 247, 0.15);
        border: 1px solid rgba(168, 85, 247, 0.3);
        color: #d8b4fe;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 600;
    }

    /* ----------------- فقاعات الشات ----------------- */
    .chat-bubble-user {
        direction: rtl;
        text-align: right;
        background: #3b1464;
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 16px 16px 4px 16px;
        padding: 10px 14px;
        margin: 8px 0;
        max-width: 88%;
        font-size: 0.92rem;
        line-height: 1.55;
        color: #f8fafc;
        align-self: flex-start;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    .chat-bubble-ai {
        direction: rtl;
        text-align: right;
        background: #130d24;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 12px 14px;
        margin: 8px 0;
        font-size: 0.92rem;
        line-height: 1.65;
        color: #f1f5f9;
        box-shadow: 0 4px 14px rgba(0,0,0,0.3);
    }

    /* تلوين البنود والأرقام بدقة متناهية وبدون بروز مزعج */
    .item-badge {
        color: #38bdf8 !important;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 1px 6px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.88em;
        display: inline-block;
        margin: 0 2px;
    }

    .calc-badge {
        color: #4ade80 !important;
        background: rgba(74, 222, 128, 0.12);
        border: 1px solid rgba(74, 222, 128, 0.3);
        padding: 1px 6px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.88em;
        display: inline-block;
        margin: 0 2px;
        direction: ltr !important;
        font-family: 'Plus Jakarta Sans', monospace !important;
    }

    /* الشريط السفلي البسيط لكل رسالة */
    .msg-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 8px;
        padding-top: 6px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 0.7rem;
        color: #64748b;
        direction: rtl;
    }

    .btn-action {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #94a3b8;
        padding: 2px 7px;
        border-radius: 6px;
        font-size: 0.7rem;
        cursor: pointer;
        font-family: 'Cairo', sans-serif;
    }

    .btn-action:hover {
        background: rgba(168, 85, 247, 0.2);
        color: #fff;
    }

    /* تحسين صندوق الإدخال السفلي */
    .stChatInputContainer textarea {
        background: #170f2a !important;
        border: 1px solid rgba(168, 85, 247, 0.3) !important;
        border-radius: 20px !important;
        color: #f8fafc !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
        direction: rtl !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- وظائف معالجة النصوص والـ JSON -----------------
def apply_custom_styling(text):
    if not text: return ""
    text = re.sub(r'\[\[(.*?)\]\]', r'<span class="item-badge">\1</span>', text)
    text = re.sub(r'\{\{(.*?)\}\}', r'<span class="calc-badge">\1</span>', text)
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

# ----------------- محرك الاتصال بـ Google Gemini -----------------
def generate_ai_response(prompt_text, user_api_key):
    from google import genai
    client = genai.Client(api_key=user_api_key)
    
    models = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-3.8-flash', 'gemini-1.5-pro']
    for m in models:
        try:
            t0 = time.time()
            resp = client.models.generate_content(model=m, contents=prompt_text)
            if resp and resp.text:
                return resp.text, round(time.time() - t0, 1)
        except Exception:
            continue
    raise Exception("تعذر الاتصال بالذكاء الاصطناعي، يرجى فحص مفتاح الـ API.")

# ----------------- تحميل بيانات ميزانية الإمارات -----------------
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
                for s in xl.sheet_names:
                    all_sheets_data[s] = pd.read_excel(fname, sheet_name=s)
                df = all_sheets_data[xl.sheet_names[0]]
            break
        except Exception:
            continue

# ----------------- القائمة الجانبية (Sidebar) للإعدادات وعرض الجدول -----------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات والبيانات")
    if not api_key:
        api_key = st.text_input("مفتاح Gemini API Key:", type="password", placeholder="AIzaSy...")
    else:
        st.success("✅ مفتاح API متصل")
        
    st.markdown("---")
    if df is not None:
        st.markdown(f"**📊 ملف الميزانية: ({len(df)} بند)**")
        st.dataframe(df, use_container_width=True)
        
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# ----------------- ذاكرة المحادثة -----------------
now_time = datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م")
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "id": 0,
            "role": "assistant",
            "content": apply_custom_styling("""أهلاً بك! تم ربط [[ميزانية السفر للإمارات]].
اسألني عن أي بند، مقارنة، أو تكلفة وسأحسبها لك بدقة:
- [[البنود والأعمدة]] باللون الأزرق.
- {{الأرقام والحسابات}} باللون الأخضر."""),
            "speech": "أهلاً بك! تم ربط ميزانية السفر للإمارات. اسألني عن أي بند وسأحسبه لك فوراً.",
            "time": now_time,
            "latency": 0.3,
            "chart": None,
            "mindmap": None,
            "raw_query": None
        }
    ]

# ----------------- الشريط العلوي المدمج (46px) -----------------
num_items = len(df) if df is not None else 0
st.markdown(f"""
<div class="compact-topbar">
    <div class="topbar-title">
        <div class="orb-dot"></div>
        <span class="title-text">Aura • ميزانية الإمارات</span>
    </div>
    <div class="badge-tag">📊 {num_items} بند متوفر</div>
</div>
""", unsafe_allow_html=True)

# ----------------- زر صوت نحيف وأنيق -----------------
voice_compact = """
<div style="direction: rtl; text-align: center; margin-bottom: 8px;">
    <button id="micBtn" onclick="toggleMic()" style="
        background: rgba(168, 85, 247, 0.2);
        border: 1px solid rgba(168, 85, 247, 0.4);
        color: #d8b4fe;
        border-radius: 14px;
        padding: 4px 12px;
        font-size: 12px;
        font-family: 'Cairo', sans-serif;
        cursor: pointer;
    ">🎙️ تحدث بالصوت</button>
    <span id="micTxt" style="color: #64748b; font-size: 11px; margin-right: 6px;"></span>
</div>
<script>
    let r = null, isRec = false;
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const S = window.SpeechRecognition || window.webkitSpeechRecognition;
        r = new S(); r.lang = 'ar-SA';
        r.onstart = () => { document.getElementById('micTxt').innerText = 'نسمع صوتك...'; document.getElementById('micBtn').style.background = '#9333ea'; };
        r.onresult = (e) => {
            navigator.clipboard.writeText(e.results[0][0].transcript);
            document.getElementById('micTxt').innerText = 'تم نسخ كلامك للشات ✓';
        };
        r.onend = () => { document.getElementById('micBtn').style.background = 'rgba(168, 85, 247, 0.2)'; };
    }
    function toggleMic() {
        if (!r) { alert('المتصفح لا يدعم المايك المباشر'); return; }
        if (!isRec) { r.start(); isRec = true; } else { r.stop(); isRec = false; }
    }
</script>
"""
components.html(voice_compact, height=32)

# ----------------- عرض رسائل الشات بتنسيق مريح ونظيف -----------------
for idx, msg in enumerate(st.session_state.messages):
    msg_id = msg.get("id", idx)
    
    if msg["role"] == "user":
        u_copy = json.dumps(msg['content'])
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-start; direction: rtl;">
            <div class="chat-bubble-user">
                {msg['content']}
                <div class="msg-footer">
                    <span>{msg.get('time', '')}</span>
                    <button class="btn-action" onclick='navigator.clipboard.writeText({u_copy}); this.innerText="تم النسخ";'>📋 نسخ</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        ai_copy = json.dumps(re.sub(r'<.*?>', '', msg['content']))
        latency = msg.get('latency', 0.5)
        
        st.markdown(f"""
        <div class="chat-bubble-ai">
            <div>{msg['content']}</div>
            <div class="msg-footer">
                <div>
                    <span>{msg.get('time', '')}</span> • <span>{latency}s</span>
                </div>
                <div style="display: flex; gap: 4px;">
                    <button class="btn-action" onclick='navigator.clipboard.writeText({ai_copy}); this.innerText="تم";'>📋 نسخ</button>
                    <button class="btn-action" onclick='speak_{msg_id}()'>🔊 استماع</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # مشغل الصوت النظيف
        if msg.get("speech"):
            spk_txt = json.dumps(re.sub(r'<.*?>', '', msg["speech"]))
            components.html(f"""
            <script>
                function speak_{msg_id}() {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        const u = new SpeechSynthesisUtterance({spk_txt});
                        u.lang = 'ar-SA';
                        window.speechSynthesis.speak(u);
                    }}
                }}
            </script>
            """, height=0)

        # الرسم البياني إن وجد
        if msg.get("chart") and df is not None:
            c = msg["chart"]
            xc, yc = c.get("x_col"), c.get("y_col")
            if xc in df.columns and yc in df.columns:
                pdf = df.groupby(xc)[yc].sum().reset_index()
                fig = px.pie(pdf, names=xc, values=yc, title=c.get("title", ""), template="plotly_dark", color_discrete_sequence=['#a855f7', '#38bdf8', '#ec4899', '#34d399'])
                fig.update_layout(paper_bgcolor="rgba(19, 13, 36, 0.6)", plot_bgcolor="rgba(19, 13, 36, 0.6)", font=dict(family="Cairo", size=11), margin=dict(l=5, r=5, t=30, b=5))
                st.plotly_chart(fig, use_container_width=True, key=f"c_{msg_id}")

        # الخريطة الذهنية
        if msg.get("mindmap") and msg["mindmap"].get("mermaid_code"):
            mcode = msg["mindmap"]["mermaid_code"]
            components.html(f"""
            <div style="direction: ltr; background: rgba(22, 14, 40, 0.7); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 10px; padding: 8px; text-align: center;">
                <pre class="mermaid" style="background: transparent;">{mcode}</pre>
            </div>
            <script type="module">
                import m from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                m.initialize({{ startOnLoad: true, theme: 'dark' }});
            </script>
            """, height=260)

        # زر إعادة الرد
        if msg.get("raw_query"):
            if st.button("🔄 إعادة توليد الإجابة", key=f"rg_{msg_id}"):
                rq = msg["raw_query"]
                st.session_state.messages = [m for m in st.session_state.messages if m.get("id") != msg_id]
                st.session_state.run_q = rq
                st.rerun()

# ----------------- استقبال الرسالة الجديدة -----------------
user_input = st.chat_input("اسأل عن ميزانية السفر للإمارات...")

to_run = None
if user_input:
    to_run = user_input
elif "run_q" in st.session_state:
    to_run = st.session_state.run_q
    del st.session_state.run_q

if to_run:
    t_str = datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م")
    
    # إضافة سؤال المستخدم
    if not any(m["role"] == "user" and m["content"] == to_run for m in st.session_state.messages[-1:]):
        st.session_state.messages.append({
            "id": len(st.session_state.messages),
            "role": "user",
            "content": to_run,
            "time": t_str
        })
        st.rerun()

    if not api_key:
        st.warning("يرجى إدخال مفتاح الـ API في القائمة الجانبية.")
    else:
        with st.spinner("جاري التحليل..."):
            try:
                summary_parts = []
                for s, sdf in all_sheets_data.items():
                    summary_parts.append(f"ورقة: {s}\nالأعمدة: {list(sdf.columns)}\n{sdf.to_string()}")
                    num_c = sdf.select_dtypes(include=['number']).columns.tolist()
                    if num_c: summary_parts.append(f"مجموع: {sdf[num_c].sum().to_string()}")
                data_summary = "\n\n".join(summary_parts)

                hist = []
                for h in st.session_state.messages[-5:-1]:
                    hist.append(f"{h['role']}: {re.sub(r'<.*?>', '', h['content'])}")
                history_text = "\n".join(hist)

                prompt = f"""
أنت مساعد مالي ذكي لميزانية السفر للإمارات.
بيانات الميزانية:
{data_summary}

المحادثة السابقة:
{history_text}

السؤال: "{to_run}"

قواعد التلوين البسيطة:
- أي اسم بند أو عمود: ضعه بين [[اسم البند]] (سيصبح أزرق).
- أي رقم أو معادلة: ضعه بين {{{{الرقم أو المعادلة}}}} (سيصبح أخضر).

أجب حصراً بـ JSON نظيف:
{{
    "answer_arabic": "الإجابة مع [[البنود]] و {{{{الأرقام}}}}.",
    "speech_summary": "ملخص صوتي قصير جداً سطر واحد.",
    "chart": {{ "has_chart": false, "type": "bar", "title": "", "x_col": "", "y_col": "" }},
    "mindmap": {{ "has_mindmap": false, "mermaid_code": "" }}
}}
"""
                raw_ans, latency = generate_ai_response(prompt, api_key)
                parsed = parse_safe_json(raw_ans)

                st.session_state.messages.append({
                    "id": len(st.session_state.messages),
                    "role": "assistant",
                    "content": apply_custom_styling(parsed.get("answer_arabic", "")),
                    "speech": parsed.get("speech_summary", ""),
                    "time": datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م"),
                    "latency": latency,
                    "chart": parsed.get("chart") if parsed.get("chart", {}).get("has_chart") else None,
                    "mindmap": parsed.get("mindmap") if parsed.get("mindmap", {}).get("has_mindmap") else None,
                    "raw_query": to_run
                })
                st.rerun()

            except Exception as e:
                st.error(f"خطأ: {e}")
