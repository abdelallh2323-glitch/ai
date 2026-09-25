import streamlit as st
import pandas as pd
import json
import os
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go

# إعداد الصفحة لتكون متوافقة تماماً مع شاشات الهواتف والكمبيوتر
st.set_page_config(
    page_title="المساعد الذكي لبيانات الإكسل",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تصميم عصري ومريح للعين (Dark Glassmorphism) بدون مشتتات ودعم كامل للعربية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* خلفية وتصميم نقي ومريح */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    /* بطاقات عصرية نظيفة */
    .custom-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* بطاقة البطل الترحيبية */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 20px;
    }

    /* إخفاء عناصر شريط الأدوات الزائدة لتفادي التشتيت */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* أزرار عصرية */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: 700;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        color: white;
    }
    
    /* تخصيص صناديق الإدخال */
    .stTextInput>div>div>input {
        background-color: #1e293b;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 1.05rem;
    }
    .stTextInput>div>div>input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- إدارة الـ API والمكتبة الذكية -----------------
def get_gemini_client(api_key):
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"خطأ في تهيئة عميل الذكاء الاصطناعي: {e}")
        return None

# محاولة استدعاء المفتاح إما من إعدادات السحابة السرية (Secrets) أو من المدخلات
api_key = st.secrets.get("GEMINI_API_KEY", "")

# ----------------- القائمة الجانبية (Sidebar) -----------------
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات والبيانات")
    
    if not api_key:
        api_key = st.text_input(
            "مفتاح Google Gemini API Key:",
            type="password",
            help="احصل عليه مجاناً في دقيقة من aistudio.google.com"
        )
        if not api_key:
            st.info("💡 [اضغط هنا للحصول على مفتاح API مجاناً من Google](https://aistudio.google.com/app/apikey)")
    else:
        st.success("✅ مفتاح الـ API مفعل وجاهز")

    st.markdown("---")
    st.markdown("### 📁 ملف البيانات")
    uploaded_file = st.file_uploader("ارفع ملف Excel أو CSV:", type=["xlsx", "xls", "csv"])
    
    use_sample = False
    if not uploaded_file:
        use_sample = st.checkbox("تجربة ملف المبيعات التجريبي الجاهز", value=True)

# ----------------- تحميل وقراءة البيانات -----------------
df = None
sheet_name = None

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            excel_file = pd.ExcelFile(uploaded_file)
            if len(excel_file.sheet_names) > 1:
                sheet_name = st.sidebar.selectbox("اختر الورقة (Sheet):", excel_file.sheet_names)
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            else:
                df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
elif use_sample and os.path.exists("sample_data.csv"):
    df = pd.read_csv("sample_data.csv")

# ----------------- واجهة العرض الرئيسية -----------------
st.markdown("""
<div class="custom-card">
    <div class="hero-title">📊 المساعد الذكي لبيانات الإكسل</div>
    <div class="hero-subtitle">تحدث بصوتك أو اكتب سؤالك باللغة العربية، واستلم إجابات دقيقة، رسوماً بيانية تفاعلية، وخرائط ذهنية فورية.</div>
</div>
""", unsafe_allow_html=True)

if df is not None:
    # بطاقة معلومات سريعة عن البيانات
    with st.expander("👁️ استعراض عينة من البيانات المرفوعة (اضغط للإظهار/الإخفاء)", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("عدد الصفوف", f"{len(df):,}")
        c2.metric("عدد الأعمدة", len(df.columns))
        c3.metric("نوع الملف", "CSV" if (uploaded_file and uploaded_file.name.endswith('.csv')) else "Excel")
        st.dataframe(df.head(6), use_container_width=True)

    # ----------------- ودجت الصوت المتقدم (Voice Widget) -----------------
    # مكون تفاعلي للمايكروفون والاستماع الصوتي مدمج بذكاء مع متصفح الهاتف
    voice_component_code = """
    <div style="direction: rtl; text-align: center; margin: 15px 0;">
        <button id="micBtn" onclick="toggleVoice()" style="
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            border: none;
            border-radius: 50%;
            width: 65px;
            height: 65px;
            font-size: 26px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
            transition: all 0.3s ease;
            outline: none;
        ">🎤</button>
        <div id="micStatus" style="color: #94a3b8; font-size: 13px; margin-top: 8px; font-family: 'Cairo', sans-serif;">
            اضغط وتحدث بصوتك مباشرة
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
            recognition.interimResults = false;

            recognition.onstart = function() {
                isRecording = true;
                const btn = document.getElementById('micBtn');
                btn.style.transform = 'scale(1.15)';
                btn.style.boxShadow = '0 0 25px rgba(239, 68, 68, 0.8)';
                document.getElementById('micStatus').innerText = '🎙️ جاري الاستماع لصوتك الآن...';
                document.getElementById('micStatus').style.color = '#ef4444';
            };

            recognition.onresult = function(event) {
                const text = event.results[0][0].transcript;
                // نسخ النص للحافظة أو إرساله تلقائياً
                navigator.clipboard.writeText(text).then(() => {
                    document.getElementById('micStatus').innerText = '✅ تم التعرف: "' + text + '" (تم نسخه للصقه أدناه)';
                    document.getElementById('micStatus').style.color = '#10b981';
                });
            };

            recognition.onerror = function(event) {
                isRecording = false;
                document.getElementById('micStatus').innerText = 'تنبيه: تعذر التقاط الصوت، يمكنك الكتابة في المربع أدناه.';
                document.getElementById('micStatus').style.color = '#f59e0b';
                document.getElementById('micBtn').style.transform = 'scale(1)';
            };

            recognition.onend = function() {
                isRecording = false;
                document.getElementById('micBtn').style.transform = 'scale(1)';
            };
        }

        function toggleVoice() {
            if (!recognition) {
                alert('المتصفح لا يدعم التسجيل الصوتي المباشر، يمكنك الكتابة في المربع أدناه.');
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
    components.html(voice_component_code, height=125)

    # خانة إدخال السؤال
    user_query = st.text_input(
        "سؤالك عن البيانات:",
        placeholder="مثال: من هو المنتج الأكثر مبيعاً؟ أو ارسم لي مخطط المبيعات حسب المدينة، أو ضع لي خطة تحسين..."
    )

    col_btn, _ = st.columns([1, 3])
    with col_btn:
        ask_pressed = st.button("🚀 تحليل وإجابة")

    # ----------------- معالجة السؤال بالذكاء الاصطناعي -----------------
    if ask_pressed and user_query:
        if not api_key:
            st.warning("⚠️ يُرجى إدخال مفتاح Gemini API Key في القائمة الجانبية أولاً.")
        else:
            with st.spinner("🧠 جاري قراءة البيانات وتحليل الإجابة وتجهيز المخططات..."):
                try:
                    client = get_gemini_client(api_key)
                    
                    # تلخيص هيكل وأرقام الجدول لإرساله بكفاءة للنموذج
                    buffer_info = []
                    buffer_info.append(f"الأعمدة: {list(df.columns)}")
                    buffer_info.append(f"عدد الصفوف الإجمالي: {len(df)}")
                    buffer_info.append(f"عينة من البيانات:\n{df.head(10).to_string()}")
                    
                    # إحصائيات سريعة للأعمدة الرقمية
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if numeric_cols:
                        buffer_info.append(f"ملخص الأرقام (Sums/Means):\n{df[numeric_cols].describe().to_string()}")

                    data_summary_text = "\n\n".join(buffer_info)

                    system_prompt = f"""
أنت خبير تحليل بيانات استراتيجي وعصري ومساعد ذكي يتحدث اللغة العربية بأسلوب راقٍ وواضح.
لديك البيانات التالية من ملف المستخدم:
{data_summary_text}

المطلوب منك:
الإجابة بدقة بالغة على سؤال المستخدم: "{user_query}" بناءً على البيانات أعلاه فقط.

يجب أن تعيد ردك بتنسيق JSON حصراً بالشكل التالي دون أي زوائد خارج كود JSON:
{{
    "answer_arabic": "الإجابة التحليلية الواضحة والذكية باللغة العربية مع الأرقام والاستنتاجات والتوصيات المهمة.",
    "speech_summary": "ملخص مقتضب باللغة العربية من جملة أو اثنتين مناسب للقراءة الصوتية بالصوت الناطق.",
    "chart": {{
        "has_chart": true or false,
        "type": "bar" | "line" | "pie" | "scatter",
        "title": "عنوان الرسم البياني بالعربية",
        "x_col": "اسم العمود المناسب لمحور السينات",
        "y_col": "اسم العمود المناسب لمحور الصادات",
        "agg": "sum" | "mean" | "count"
    }},
    "mindmap": {{
        "has_mindmap": true or false,
        "mermaid_code": "graph TD\\n A[الفكرة الرئيسية] --> B[نقطة فرعية]\\n A --> C[نقطة فرعية أخرى]"
    }}
}}

ملاحظات:
1. إذا كان السؤال يتضمن مقارنة أو توزيعاً عددياً، اجعل has_chart = true واختر أفضل الأعمدة ونوع الرسم.
2. إذا كان السؤال يطلب خطة، استراتيجية، تصنيف، هيكلة ذهنية، أو خطوات عمل، اجعل has_mindmap = true واكتب كود Mermaid سليم تماماً بدون رموز تكسر الكود.
3. التزم بالـ JSON فقط.
"""

                    # استدعاء النموذج
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=system_prompt,
                    )

                    response_text = response.text.strip()
                    # تنظيف الرد من علامات الـ markdown إذا وجدت
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    response_text = response_text.strip()

                    res_data = json.loads(response_text)

                    # ----------------- عرض النتيجة -----------------
                    st.markdown("---")
                    
                    # 1. الإجابة النصية مع قارئ الصوت
                    answer_text = res_data.get("answer_arabic", "")
                    speech_text = res_data.get("speech_summary", answer_text[:120])

                    st.markdown(f"""
                    <div class="custom-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <h3 style="margin: 0; color: #60a5fa;">💡 الإجابة والتحليل الذكي</h3>
                        </div>
                        <div style="font-size: 1.15rem; line-height: 1.8; color: #f8fafc;">
                            {answer_text}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # قارئ الصوت التفاعلي (Text-to-Speech)
                    tts_code = f"""
                    <div style="direction: rtl; margin-bottom: 20px;">
                        <button onclick="speakText()" style="
                            background: rgba(99, 102, 241, 0.2);
                            border: 1px solid #6366f1;
                            color: #a5b4fc;
                            padding: 8px 18px;
                            border-radius: 20px;
                            cursor: pointer;
                            font-size: 14px;
                            font-family: 'Cairo', sans-serif;
                            font-weight: 600;
                            display: inline-flex;
                            align-items: center;
                            gap: 8px;
                        ">🔊 استمع للرد الصوتي</button>
                    </div>

                    <script>
                        function speakText() {{
                            if ('speechSynthesis' in window) {{
                                window.speechSynthesis.cancel();
                                const text = {json.dumps(speech_text)};
                                const utterance = new SpeechSynthesisUtterance(text);
                                utterance.lang = 'ar-SA';
                                utterance.rate = 0.95;
                                window.speechSynthesis.speak(utterance);
                            }} else {{
                                alert('المتصفح لا يدعم القراءة الصوتية.');
                            }}
                        }}
                    </script>
                    """
                    components.html(tts_code, height=55)

                    # 2. عرض الرسم البياني إذا وجد
                    chart_info = res_data.get("chart", {})
                    if chart_info.get("has_chart", False):
                        st.markdown("### 📈 الرسم البياني")
                        x_col = chart_info.get("x_col")
                        y_col = chart_info.get("y_col")
                        chart_type = chart_info.get("type", "bar")
                        title = chart_info.get("title", "رسم بياني")

                        if x_col in df.columns and y_col in df.columns:
                            agg = chart_info.get("agg", "sum")
                            try:
                                if agg == "sum":
                                    plot_df = df.groupby(x_col)[y_col].sum().reset_index()
                                elif agg == "mean":
                                    plot_df = df.groupby(x_col)[y_col].mean().reset_index()
                                else:
                                    plot_df = df.groupby(x_col)[y_col].count().reset_index()

                                if chart_type == "bar":
                                    fig = px.bar(plot_df, x=x_col, y=y_col, title=title, template="plotly_dark", color_discrete_sequence=['#6366f1'])
                                elif chart_type == "line":
                                    fig = px.line(plot_df, x=x_col, y=y_col, title=title, template="plotly_dark", color_discrete_sequence=['#38bdf8'])
                                elif chart_type == "pie":
                                    fig = px.pie(plot_df, names=x_col, values=y_col, title=title, template="plotly_dark")
                                else:
                                    fig = px.bar(plot_df, x=x_col, y=y_col, title=title, template="plotly_dark")

                                fig.update_layout(
                                    paper_bgcolor="rgba(15, 23, 42, 0.6)",
                                    plot_bgcolor="rgba(15, 23, 42, 0.6)",
                                    font=dict(family="Cairo", size=13),
                                    margin=dict(l=20, r=20, t=50, b=20)
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception as plot_err:
                                st.info("لم نتمكن من توليد الرسم التلقائي لهذه الأعمدة، الإجابة التحليلية متوفرة في الأعلى.")

                    # 3. عرض الخريطة الذهنية إذا طلبت أو تم إنشاؤها
                    mindmap_info = res_data.get("mindmap", {})
                    if mindmap_info.get("has_mindmap", False):
                        mermaid_syntax = mindmap_info.get("mermaid_code", "")
                        if mermaid_syntax:
                            st.markdown("### 🧠 الخريطة الذهنية ومخطط العمل")
                            
                            # تضمين مكتبة Mermaid لعرض المخطط بدقة وانسيابية
                            mermaid_html = f"""
                            <div style="direction: ltr; background: rgba(30, 41, 59, 0.7); border-radius: 14px; padding: 20px; border: 1px solid rgba(255,255,255,0.08); text-align: center;">
                                <pre class="mermaid" style="background: transparent;">
                                    {mermaid_syntax}
                                </pre>
                            </div>
                            <script type="module">
                                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                                mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
                            </script>
                            """
                            components.html(mermaid_html, height=360, scrolling=True)

                except Exception as e:
                    st.error(f"حدث خطأ أثناء معالجة السؤال: {e}")

else:
    st.info("👆 يُرجى رفع ملف إكسل أو تفعيل خيار الملف التجريبي من القائمة الجانبية للبدء.")
