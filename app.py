import streamlit as st
import pandas as pd
import json
import os
import re
import time
import html
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

# ----------------- تصميم Gemini الداكن الراقي بالأيقونات الفيكتور وبدون أي ريفريش -----------------
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
        margin-bottom: 20px;
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
        transition: all 0.2s ease;
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
        margin-bottom: 20px;
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

    /* أزرار الأيقونات الفيكتور النقية بدون أي حدود أو إطارات مربعة */
    .gemini-svg-btn {
        background: transparent !important;
        border: none !important;
        color: #8e918f !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 4px 6px !important;
        border-radius: 6px !important;
        cursor: pointer !important;
        box-shadow: none !important;
        outline: none !important;
        transition: color 0.15s ease, background 0.15s ease !important;
    }

    .gemini-svg-btn:hover {
        color: #e3e3e3 !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }

    .gemini-svg-btn svg {
        pointer-events: none;
    }

    /* صندوق الإدخال السفلي */
    div[data-testid="stChatInput"] textarea {
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
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
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
    stored_key = ""
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            stored_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        stored_key = ""
    st.session_state.api_key = stored_key

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
st.markdown(
    f'<div class="top-meta-bar">'
    f'<div style="color: #a8c7fa; font-weight: 600;">📁 الملف الحالي: {active_file_name}</div>'
    f'<div style="font-size: 12px; color: #8e918f;">{num_rows} صف • Gemini ✦</div>'
    f'</div>',
    unsafe_allow_html=True
)

# ----------------- عرض رسائل الشات -----------------
for idx, msg in enumerate(st.session_state.messages):
    msg_id = msg.get("id", idx)

    if msg["role"] == "user":
        u_content = msg['content']
        u_time = msg.get('time', now_time)
        clean_user_txt = html.escape(u_content, quote=True)

        user_html = (
            f'<div class="chat-row-user">'
            f'<div class="gemini-user-pill" id="user_pill_{msg_id}">{u_content}</div>'
            f'<div class="action-bar-container">'
            f'<span class="meta-time-text">{u_time}</span>'
            f'<div class="action-icons-group">'
            f'<button type="button" class="gemini-svg-btn gemini-copy-btn" data-text="{clean_user_txt}" title="نسخ">{SVG_COPY}</button>'
            f'<button type="button" class="gemini-svg-btn gemini-edit-btn" data-id="{msg_id}" data-text="{clean_user_txt}" title="تحرير السؤال">{SVG_EDIT}</button>'
            f'</div></div></div>'
        )
        st.markdown(user_html, unsafe_allow_html=True)

    else:
        ai_time = msg.get('time', now_time)
        latency_val = msg.get('latency', 0.4)
        raw_q = msg.get('raw_query', '')
        clean_ai_txt = html.escape(re.sub(r'<.*?>', '', msg['content']), quote=True)
        clean_raw_q = html.escape(raw_q or "", quote=True)

        regen_btn_html = f'<button type="button" class="gemini-svg-btn gemini-regen-btn" data-query="{clean_raw_q}" title="إعادة بناء الرد">{SVG_REGEN}</button>' if raw_q else ''

        ai_html = (
            f'<div class="gemini-ai-text">{msg["content"]}</div>'
            f'<div class="action-bar-container">'
            f'<span class="meta-time-text">{ai_time} • {latency_val} ثانية</span>'
            f'<div class="action-icons-group">'
            f'<button type="button" class="gemini-svg-btn gemini-copy-btn" data-text="{clean_ai_txt}" title="نسخ الإجابة">{SVG_COPY}</button>'
            f'{regen_btn_html}'
            f'</div></div>'
        )
        st.markdown(ai_html, unsafe_allow_html=True)

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

# ----------------- مشغل التفاعل اللحظي (Zero-Refresh Event Controller) -----------------
interactive_engine = """
<script>
(function() {
    function initGeminiEngine() {
        let pdoc;
        try {
            pdoc = window.parent.document;
        } catch (e) {
            pdoc = null;
        }
        if (!pdoc) return;

        // إزالة أي مستمع قديم من دورة رندر سابقة لتفادي مشكلة الـ Dead Iframe Context
        if (pdoc._gemini_click_handler) {
            try {
                pdoc.removeEventListener('click', pdoc._gemini_click_handler, true);
            } catch(err) {}
        }

        pdoc._gemini_click_handler = function(e) {
            // 1. زر النسخ المباشر
            const copyBtn = e.target.closest('.gemini-copy-btn');
            if (copyBtn) {
                e.preventDefault();
                e.stopPropagation();
                const text = copyBtn.getAttribute('data-text');
                if (!text) return;

                function showDone() {
                    const orig = copyBtn.innerHTML;
                    copyBtn.innerHTML = '<span style="color:#6dd58c; font-size:12px; font-weight:bold; font-family:Cairo,sans-serif;">تم النسخ ✓</span>';
                    setTimeout(() => { copyBtn.innerHTML = orig; }, 1400);
                }

                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text).then(showDone).catch(fallback);
                } else {
                    fallback();
                }

                function fallback() {
                    const ta = pdoc.createElement('textarea');
                    ta.value = text;
                    ta.style.position = 'fixed';
                    ta.style.opacity = '0';
                    pdoc.body.appendChild(ta);
                    ta.select();
                    try { pdoc.execCommand('copy'); showDone(); } catch(err) {}
                    pdoc.body.removeChild(ta);
                }
                return;
            }

            // 2. زر تحرير السؤال الفوري في مكانه
            const editBtn = e.target.closest('.gemini-edit-btn');
            if (editBtn) {
                e.preventDefault();
                e.stopPropagation();
                const msgId = editBtn.getAttribute('data-id');
                const pill = pdoc.getElementById('user_pill_' + msgId);
                if (!pill || pill.querySelector('textarea')) return;

                const originalText = pill.innerText.trim();
                const safeOriginal = originalText.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

                pill.innerHTML = `
                    <div style="width: 100%; direction: rtl; text-align: right; margin-top: 4px;">
                        <textarea id="inline_edit_ta_${msgId}" style="width: 100%; min-height: 65px; background: #1e1f20; color: #e3e3e3; border: 1.5px solid #a8c7fa; border-radius: 14px; padding: 10px 14px; font-family: 'Cairo', sans-serif; font-size: 14.5px; outline: none; resize: vertical; box-sizing: border-box; line-height: 1.6;">${safeOriginal}</textarea>
                        <div style="display: flex; gap: 8px; justify-content: flex-end; margin-top: 8px;">
                            <button id="cancel_edit_btn_${msgId}" type="button" style="background: transparent; border: 1px solid rgba(255,255,255,0.2); color: #c4c7c5; padding: 5px 14px; border-radius: 18px; font-size: 12.5px; cursor: pointer; font-family: 'Cairo', sans-serif;">إلغاء</button>
                            <button id="save_edit_btn_${msgId}" type="button" style="background: #a8c7fa; border: none; color: #040e1e; padding: 5px 16px; border-radius: 18px; font-size: 12.5px; font-weight: 700; cursor: pointer; font-family: 'Cairo', sans-serif;">حفظ وإرسال ✦</button>
                        </div>
                    </div>
                `;

                const ta = pill.querySelector('#inline_edit_ta_' + msgId);
                if (ta) {
                    ta.focus();
                    ta.setSelectionRange(ta.value.length, ta.value.length);
                }

                const cancelBtn = pill.querySelector('#cancel_edit_btn_' + msgId);
                if (cancelBtn) {
                    cancelBtn.onclick = (ev) => {
                        ev.preventDefault();
                        ev.stopPropagation();
                        pill.innerText = originalText;
                    };
                }

                const saveBtn = pill.querySelector('#save_edit_btn_' + msgId);
                if (saveBtn) {
                    saveBtn.onclick = (ev) => {
                        ev.preventDefault();
                        ev.stopPropagation();
                        const newQuery = ta ? ta.value.trim() : '';
                        if (!newQuery) return;
                        pill.innerText = newQuery;
                        sendQueryToStreamlit(newQuery);
                    };
                }
                return;
            }

            // 3. زر إعادة توليد الرد الفوري
            const regenBtn = e.target.closest('.gemini-regen-btn');
            if (regenBtn) {
                e.preventDefault();
                e.stopPropagation();
                const query = regenBtn.getAttribute('data-query');
                if (query) {
                    const orig = regenBtn.innerHTML;
                    regenBtn.innerHTML = '<span style="color:#a8c7fa; font-size:11px; font-family:Cairo,sans-serif;">جارٍ التوليد...</span>';
                    setTimeout(() => { regenBtn.innerHTML = orig; }, 2500);
                    sendQueryToStreamlit(query);
                }
                return;
            }
        };

        pdoc.addEventListener('click', pdoc._gemini_click_handler, true);

        function sendQueryToStreamlit(textToSend) {
            const textarea = pdoc.querySelector('textarea[data-testid="stChatInputTextArea"]') ||
                             pdoc.querySelector('[data-testid="stChatInput"] textarea') ||
                             pdoc.querySelector('.stChatInput textarea') ||
                             pdoc.querySelector('textarea');
            if (!textarea) return;

            textarea.focus();
            const proto = window.parent.HTMLTextAreaElement ? window.parent.HTMLTextAreaElement.prototype : HTMLTextAreaElement.prototype;
            const nativeSetter = Object.getOwnPropertyDescriptor(proto, "value").set;
            if (nativeSetter) {
                nativeSetter.call(textarea, textToSend);
            } else {
                textarea.value = textToSend;
            }

            if (textarea._valueTracker) {
                textarea._valueTracker.setValue("");
            }

            textarea.dispatchEvent(new Event('input', { bubbles: true }));
            textarea.dispatchEvent(new Event('change', { bubbles: true }));

            setTimeout(() => {
                const sendBtn = pdoc.querySelector('button[data-testid="stChatInputSubmitButton"]') ||
                                pdoc.querySelector('[data-testid="stChatInput"] button');

                if (sendBtn && !sendBtn.disabled) {
                    sendBtn.click();
                } else {
                    textarea.dispatchEvent(new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true
                    }));
                }
            }, 180);
        }
    }

    initGeminiEngine();
    if (document.readyState !== 'complete') {
        window.addEventListener('load', initGeminiEngine);
    }
})();
</script>
"""
components.html(interactive_engine, height=0)

# ----------------- استقبال وتوليد الأسئلة -----------------
user_input = st.chat_input(placeholder="اسأل Gemini عن أي معلومة في بياناتك ✦")

if user_input:
    current_time_str = datetime.now().strftime("%I:%M %p").replace("AM", "ص").replace("PM", "م")
    
    st.session_state.messages.append({
        "id": len(st.session_state.messages),
        "role": "user",
        "content": user_input,
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
            "raw_query": user_input
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

سؤال المستخدم: "{user_input}"

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
                    "raw_query": user_input
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
                    "raw_query": user_input
                })

        st.rerun()
