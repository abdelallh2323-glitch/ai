import streamlit as st
import pandas as pd
import json
import os
import streamlit.components.v1 as components
import plotly.express as px

# إعداد الصفحة
st.set_page_config(
    page_title="المساعد الذكي لبيانات الإكسل",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- تصميم عصري وأنيق بدون كسر أيقونات النظام -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

    /* تطبيق الخط فقط على النصوص دون المساس بأيقونات ستريمليت */
    body, p, h1, h2, h3, h4, h5, h6, .stMarkdown, .stTextInput, .stButton, .stSelectbox, .stAlert {
        font-family: 'Cairo', sans-serif !important;
    }

    /* خلفية داكنة مريحة للعين */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }

    /* بطاقة رئيسية عصرية */
    .app-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        direction: rtl;
        text-align: right;
    }

    .app-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 6px;
    }

    .app-desc {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* إجابة الذكاء الاصطناعي */
    .answer-box {
        background: #172554;
        border-right: 4px solid #3b82f6;
        border-radius: 10px;
        padding: 18px;
        margin: 15px 0;
        direction: rtl;
        text-align: right;
        font-size: 1.05rem;
        line-height: 1.8;
        color: #eff6ff;
    }

    /* جعل الأزرار جذابة وسهلة اللمس على الموبايل */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 700;
        font-size: 1rem;
        width: 100%;
        transition: 0.2s;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #4338ca 100%);
        color: white;
    }

    /* تصحيح اتجاه حقول الإدخال */
    .stTextInput input {
        direction: rtl !important;
        text-align: right !important;
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- دالة الاتصال بـ Google Gemini -----------------
def generate_ai_response(prompt_text, user_api_key):
    try:
        from google import genai
        client = genai.Client(api_key=user_api_key)
        
        # قائمة النماذج المعتمدة بالأولوية (Gemini 3.8 Flash هو الأساسي وفقاً لتعليمات Google)
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
            st.info("💡 [اضغط هنا للحصول على مفتاح API مجاناً](https://aistudio.google.com/app/apikey)")
    else:
        st.success("✅ مفتاح الـ API مسجل بنجاح")

    st.markdown("---")
    st.markdown("### 📁 ملف البيانات")
    uploaded_file = st.file_uploader("ارفع ملف Excel أو CSV:", type=["xlsx", "xls", "csv"])
    
    use_sample = False
    if not uploaded_file:
        use_sample = st.checkbox("استخدام ملف البيانات التجريبي", value=True)

# ----------------- قراءة ملف البيانات -----------------
df = None
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            excel_file = pd.ExcelFile(uploaded_file)
            if len(excel_file.sheet_names) > 1:
                selected_sheet = st.sidebar.selectbox("اختر الورقة (Sheet):", excel_file.sheet_names)
                df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
            else:
                df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"خطأ أثناء قراءة الملف: {e}")
elif use_sample and os.path.exists("sample_data.csv"):
    df = pd.read_csv("sample_data.csv")

# ----------------- الواجهة الرئيسية -----------------
st.markdown("""
<div class="app-card">
    <div class="app-title">📊 المساعد الذكي لبيانات الإكسل</div>
    <div class="app-desc">اسأل عن أي معلومة في بياناتك بالصوت أو الكتابة، واحصل على إجابات دقيقة، رسوم بيانية، وخرائط ذهنية فورية.</div>
</div>
""", unsafe_allow_html=True)

if df is not None:
    with st.expander("👁️ استعراض عينة من البيانات المرفوعة", expanded=False):
        c1, c2 = st.columns(2)
        c1.metric("عدد الصفوف", f"{len(df):,}")
        c2.metric("عدد الأعمدة", len(df.columns))
        st.dataframe(df.head(5), use_container_width=True)

    # ----------------- ودجت الصوت النظيف -----------------
    voice_component = """
    <div style="direction: rtl; text-align: center; margin: 10px 0 20px 0;">
        <button id="micBtn" onclick="toggleVoice()" style="
            background: #dc2626;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 12px 24px;
            font-size: 16px;
            font-family: sans-serif;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
            transition: 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        ">
            <span>🎙️</span>
            <span id="btnText">اضغط للتحدث بالصوت</span>
        </button>
        <div id="micStatus" style="color: #94a3b8; font-size: 13px; margin-top: 8px;">
            تحدث بالعربية وسنقوم بنسخ سؤالك تلقائياً للصقه في خانة السؤال
        </div>
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
                document.getElementById('btnText').innerText = 'جاري الاستماع لصوتك...';
                document.getElementById('micBtn').style.background = '#16a34a';
                document.getElementById('micStatus').innerText = 'تحدث الآن، نستمع إليك...';
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
                document.getElementById('btnText').innerText = 'اضغط للتحدث بالصوت';
                document.getElementById('micBtn').style.background = '#dc2626';
                document.getElementById('micStatus').innerText = 'تعذر التقاط الصوت، يمكنك الكتابة مباشرة أدناه.';
                document.getElementById('micStatus').style.color = '#f87171';
            };

            recognition.onend = function() {
                isRecording = false;
                document.getElementById('btnText').innerText = 'اضغط للتحدث بالصوت';
                document.getElementById('micBtn').style.background = '#dc2626';
            };
        }

        function toggleVoice() {
            if (!recognition) {
                alert('المتصفح لا يدعم التسجيل الصوتي المباشر، يمكنك الكتابة في المربع.');
                return;
            }
            if (!isRecording) {
                recognition.start();
            } else {
                recognition.stop();
            }
        }
    </script>
    """
    components.html(voice_component, height=110)

    # خانة إدخال السؤال
    user_query = st.text_input(
        "سؤالك عن البيانات:",
        placeholder="مثال: من هو المنتج الأكثر مبيعاً؟ أو ضع خطة لتطوير المبيعات..."
    )

    if st.button("🚀 تحليل وإجابة"):
        if not user_query:
            st.warning("يرجى كتابة السؤال أو التحدث بالمايك أولاً.")
        elif not api_key:
            st.warning("⚠️ يُرجى إدخال مفتاح Gemini API Key في القائمة الجانبية.")
        else:
            with st.spinner("🧠 جاري تحليل البيانات وتوليد الإجابة..."):
                try:
                    # ملخص البيانات
                    summary_parts = [
                        f"الأعمدة: {list(df.columns)}",
                        f"عدد الصفوف: {len(df)}",
                        f"عينة بيانات:\n{df.head(10).to_string()}"
                    ]
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if numeric_cols:
                        summary_parts.append(f"إحصائيات الأرقام:\n{df[numeric_cols].describe().to_string()}")

                    data_summary = "\n\n".join(summary_parts)

                    prompt = f"""
أنت محلل بيانات ذكي ومحترف تجيب باللغة العربية بدقة ووضوح.
بيانات الإكسل:
{data_summary}

سؤال المستخدم: "{user_query}"

أجب حصراً بصيغة JSON نظيفة بدون أي نص إضافي بالشكل التالي:
{{
    "answer_arabic": "الإجابة التحليلية الواضحة والذكية باللغة العربية مع الأرقام والتفاصيل.",
    "speech_summary": "ملخص سريع في سطر واحد للقراءة الصوتية.",
    "chart": {{
        "has_chart": true or false,
        "type": "bar" | "line" | "pie",
        "title": "عنوان الرسم بالعربية",
        "x_col": "اسم العمود المناسب لمحور السينات",
        "y_col": "اسم العمود المناسب لمحور الصادات",
        "agg": "sum" | "mean" | "count"
    }},
    "mindmap": {{
        "has_mindmap": true or false,
        "mermaid_code": "graph TD\\n A[الهدف الرئيسي] --> B[خطوة 1]\\n A --> C[خطوة 2]"
    }}
}}
قواعد مهمة:
1. إذا طلب مقارنة أو إحصائيات بصرية اجعل has_chart = true.
2. إذا طلب خطة، استراتيجية، أو خريطة أفكار اجعل has_mindmap = true مع كود Mermaid صحيح.
"""

                    raw_response = generate_ai_response(prompt, api_key)
                    clean_json = raw_response.strip()
                    if clean_json.startswith("```json"):
                        clean_json = clean_json[7:]
                    if clean_json.endswith("```"):
                        clean_json = clean_json[:-3]
                    clean_json = clean_json.strip()

                    res_data = json.loads(clean_json)

                    # 1. عرض الإجابة
                    answer_text = res_data.get("answer_arabic", "")
                    speech_text = res_data.get("speech_summary", answer_text[:120])

                    st.markdown(f"""
                    <div class="answer-box">
                        <div style="font-weight: 700; color: #60a5fa; margin-bottom: 8px;">💡 نتيجة التحليل:</div>
                        <div>{answer_text}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # زر القراءة الصوتية
                    tts_code = f"""
                    <div style="direction: rtl; margin-bottom: 15px;">
                        <button onclick="speakText()" style="
                            background: #1e293b;
                            border: 1px solid #3b82f6;
                            color: #93c5fd;
                            padding: 8px 18px;
                            border-radius: 20px;
                            cursor: pointer;
                            font-size: 14px;
                            font-family: sans-serif;
                            font-weight: 600;
                        ">🔊 استمع للإجابة بالصوت</button>
                    </div>

                    <script>
                        function speakText() {{
                            if ('speechSynthesis' in window) {{
                                window.speechSynthesis.cancel();
                                const text = {json.dumps(speech_text)};
                                const utterance = new SpeechSynthesisUtterance(text);
                                utterance.lang = 'ar-SA';
                                utterance.rate = 1.0;
                                window.speechSynthesis.speak(utterance);
                            }}
                        }}
                    </script>
                    """
                    components.html(tts_code, height=50)

                    # 2. عرض الرسم البياني
                    chart_info = res_data.get("chart", {})
                    if chart_info.get("has_chart", False):
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

                            if c_type == "line":
                                fig = px.line(plot_df, x=x_col, y=y_col, title=title, template="plotly_dark")
                            elif c_type == "pie":
                                fig = px.pie(plot_df, names=x_col, values=y_col, title=title, template="plotly_dark")
                            else:
                                fig = px.bar(plot_df, x=x_col, y=y_col, title=title, template="plotly_dark")

                            fig.update_layout(
                                paper_bgcolor="#1e293b",
                                plot_bgcolor="#1e293b",
                                font=dict(family="Cairo", size=13),
                                margin=dict(l=15, r=15, t=40, b=15)
                            )
                            st.plotly_chart(fig, use_container_width=True)

                    # 3. عرض الخريطة الذهنية
                    mindmap_info = res_data.get("mindmap", {})
                    if mindmap_info.get("has_mindmap", False):
                        m_code = mindmap_info.get("mermaid_code", "")
                        if m_code:
                            st.markdown("### 🧠 الخريطة الذهنية ومخطط العمل")
                            mermaid_html = f"""
                            <div style="direction: ltr; background: #1e293b; border-radius: 12px; padding: 15px; border: 1px solid #334155; text-align: center;">
                                <pre class="mermaid" style="background: transparent;">
                                    {m_code}
                                </pre>
                            </div>
                            <script type="module">
                                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                                mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
                            </script>
                            """
                            components.html(mermaid_html, height=350, scrolling=True)

                except Exception as e:
                    st.error(f"حدث خطأ أثناء معالجة السؤال: {e}")

else:
    st.info("👆 يرجى رفع ملف إكسل أو تفعيل خيار الملف التجريبي من القائمة الجانبية للبدء.")
