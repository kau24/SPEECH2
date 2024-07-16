import streamlit as st
import sounddevice as sd
import wavio
import os
import pandas as pd
from datetime import datetime

# Create main directory
main_directory = "Speech"
if not os.path.exists(main_directory):
    os.makedirs(main_directory)

# Create subdirectories for passage one and two
passage_one_dir = os.path.join(main_directory, "passage_one")
passage_two_dir = os.path.join(main_directory, "passage_two")
if not os.path.exists(passage_one_dir):
    os.makedirs(passage_one_dir)
if not os.path.exists(passage_two_dir):
    os.makedirs(passage_two_dir)

# Passages
passages = {
    "Passage 1": "في يوم مشمس، قرر علي أن يذهب في رحلة إلى الغابة. كانت الأشجار عالية والأوراق خضراء تلمع تحت أشعة الشمس. بينما كان يسير، سمع تغريد الطيور وشعر بنسيم خفيف يلامس وجهه. فجأة، رأى أرنبًا صغيرًا يقفز بين الأعشاب. حاول علي الاقتراب بهدوء لكي لا يخيفه، ولكن الأرنب كان سريعًا واختفى بين الأشجار. واصل علي المشي حتى وصل إلى نهر جارٍ، فجلس قربه ليستريح ويستمتع بجمال الطبيعة.",
    "Passage 2": "في يوم مشمس من أيام الصيف، قرر سالم أن يذهب في نزهة إلى الحديقة. كانت الأشجار عالية والأوراق خضراء تلمع تحت أشعة الشمس. بينما كان يسير، سمع زقزقة العصافير وشعر بنسيم خفيف يلامس وجهه. فجأة، رأى طائرًا صغيرًا يطير بين الأغصان. حاول سالم الاقتراب بهدوء لكي لا يخيفه، ولكن الطائر كان سريعًا واختفى بين الأشجار. واصل سالم المشي حتى وصل إلى بحيرة صافية، فجلس قربها ليستريح ويستمتع بجمال الطبيعة. رأى السماء زرقاء صافية، والماء يعكس صورة الغيوم البيضاء. شعر بالراحة والسكينة، وتمنى لو أن الوقت يتوقف ليستمتع بهذه اللحظة للأبد."
}

# Initialize session state variables
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'audio_fs' not in st.session_state:
    st.session_state.audio_fs = None

# Function to start recording
def start_recording(duration=30, fs=44100):
    st.session_state.recording = True
    st.write("Recording...")
    st.session_state.audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    st.session_state.audio_fs = fs

# Function to stop recording
def stop_recording():
    if st.session_state.recording:
        sd.stop()
        st.session_state.recording = False
        st.write("Recording stopped.")

# Function to save audio
def save_audio(filename):
    if st.session_state.audio_data is not None and st.session_state.audio_fs is not None:
        wavio.write(filename, st.session_state.audio_data, st.session_state.audio_fs, sampwidth=2)
        st.write("Recording saved.")

# Function to save survey results
def save_survey_results(data, passage_dir, student_id):
    csv_file = os.path.join(passage_dir, f"{student_id}_survey.csv")
    df = pd.DataFrame([data])
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_file, index=False)

# Streamlit app
st.markdown(
    """
    <div style="background-color: lightgreen; padding: 10px; border-radius: 5px;">
        <h1 style="text-align: center; font-size: 40px;">اداة تسجيل النصوص</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Student ID input
student_id = st.text_input("أدخل رقم الجامعة الخاص بك:")

if student_id:
    passage = st.selectbox("اختر النص للقراءة:", list(passages.keys()))

    if passage:
        st.markdown(f"<div style='text-align: right; direction: rtl; font-size: 18px;'>{passages[passage]}</div>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col2:
            if st.button("بدء التسجيل"):
                start_recording()

        with col3:
            if st.button("إيقاف التسجيل"):
                stop_recording()

        if passage == "Passage 1":
            with col2:
                if st.button("حفظ التسجيل في مجلد النص الأول"):
                    filename = os.path.join(passage_one_dir, f"{student_id}.wav")
                    save_audio(filename)

        if passage == "Passage 2":
            with col3:
                if st.button("حفظ التسجيل في مجلد النص الثاني"):
                    filename = os.path.join(passage_two_dir, f"{student_id}.wav")
                    save_audio(filename)

        st.write("يرجى ملء الاستبيان لتسجيلك:")

        # Survey questions
        survey_data = {
            "student_id": student_id,
            "passage": passage,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "speech_rate": st.select_slider("تحدثت بسرعة مريحة.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "pauses_hesitations": st.select_slider("نادراً ما توقفت أو ترددت أثناء التحدث.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "intonation": st.select_slider("كان لحديثي تنوع في النبرة وكان مناسباً.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "phoneme_usage": st.select_slider("نطقت الأصوات بوضوح وصحة.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "fluency_disruptions": st.select_slider("لم أستخدم كلمات مثل 'أم', 'آه', أو 'تعرف' كثيراً.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "self_corrections": st.select_slider("نادراً ما كنت بحاجة لتكرار أو تصحيح نفسي أثناء التحدث.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "volume_loudness": st.select_slider("تحدثت بصوت مناسب طوال النص.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "speech_errors": st.select_slider("لم أرتكب أخطاء كثيرة أثناء التحدث.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "discourse_markers": st.select_slider("لم أستخدم العلامات الخطابية مثل 'أم', 'آه', أو 'تعرف' بشكل مفرط.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "articulation_rate": st.select_slider("حافظت على معدل نطق متسق.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "duration_speech_segments": st.select_slider("كان طول مقاطع حديثي طبيعياً.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "pitch_variation": st.select_slider("كان لحديثي تنوع مناسب في النبرة.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "loudness_range": st.select_slider("حافظت على نطاق صوت مناسب.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "breathiness": st.select_slider("لم يبدو حديثي متقطعاً.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "speech_intelligibility": st.select_slider("كان حديثي واضحاً ومفهوماً.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
        }

        if st.button("إرسال الاستبيان"):
            passage_dir = passage_one_dir if passage == "Passage 1" else passage_two_dir
            save_survey_results(survey_data, passage_dir, student_id)
            st.write("تم حفظ نتائج الاستبيان.")

        st.write("يرجى الانتقال إلى النص التالي بعد الانتهاء من هذا النص.")
