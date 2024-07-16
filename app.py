import streamlit as st
import sounddevice as sd
import wavio
import pandas as pd
from datetime import datetime
import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from pydub import AudioSegment
from pydub.playback import play

# Example function to play an audio file
def play_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    play(audio)
    
# Function to set up Google Drive API
def get_gdrive_service():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

# Function to upload file to Google Drive
def upload_to_gdrive(service, file_name, folder_id):
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(open(file_name, 'rb').read()), mimetype='application/octet-stream')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# Google Drive folder IDs (replace with your own folder IDs)
FOLDER_ID_SPEECH2 = '1_vnY4oIPZZVA0Lr-u-n_muCOBP_nvSll'
FOLDER_ID_PASSAGE_ONE = '1yfL7G_GLVDgIdZwWeUgbHtiZZ-y-996S'
FOLDER_ID_PASSAGE_TWO = '1uiCCCevvzbI4blXGduZvj-51kNbWKzoo'
FOLDER_ID_PASSAGE_THREE = '1en222X8vur6r2y3ccvuRnDmMblamuium'

# Initialize Google Drive service
gdrive_service = get_gdrive_service()

# Passages
passages = {
    "Passage 1": "في يوم مشمس، قررتُ أن أخرج للتنزه في الحديقة المجاورة لمنزلي. كانت السماء زرقاء صافية، وكانت الشمس تضيء كل شيء بنورها الساطع. الطيور تغني في الأشجار، والأطفال يلعبون ويضحكون بسعادة. بينما كنت أسير على الممر المرصوف، شعرت بنسيم عليل يلامس وجهي بلطف، وكان هناك رائحة زهور الربيع تملأ الهواء. جلستُ على مقعد خشبي تحت شجرة كبيرة، واستمعت لصوت الرياح وهي تحرك الأغصان. كان كل شيء من حولي يبعث على الطمأنينة والراحة، وشعرت بالسعادة تغمر قلبي.",
    "Passage 2": "في ليلة هادئة، جلستُ بجانب النافذة أراقب النجوم في السماء. كانت النجوم تتلألأ مثل الألماس في الظلام، وكان القمر يضيء بنوره الفضي، ينير كل شيء من حوله. جلستُ أتأمل في الكون الواسع، وأفكر في عظمة خلق الله. سمعتُ الخنافس وهي تصدر أصواتها المتقطعة في الحديقة، وشعرت بنسيم الليل البارد يلامس وجهي. كانت لحظات من التأمل والهدوء، حيث شعرت بالسلام الداخلي والامتنان لكل النعم التي أمتلكها. في تلك اللحظة، أدركت أن السعادة تكمن في البساطة والتقدير للأشياء الصغيرة في الحياة.",
    "Passage 3": "ألخَيْـلُ وَاللّيْـلُ وَالبَيْـداءُ تَعرِفُنـي\nوَالسّيفُ وَالرّمحُ والقرْطاسُ وَالقَلَـمُ\nصَحِبْتُ فِي الفَلَواتِ الوَحشَ منفَـرِداً\nحتى تَعَجّبَ منـي القُـورُ وَالأكَـمُ"
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

# Function to save audio locally and upload to Google Drive
def save_audio(file_name, folder_id):
    if st.session_state.audio_data is not None and st.session_state.audio_fs is not None:
        wavio.write(file_name, st.session_state.audio_data, st.session_state.audio_fs, sampwidth=2)
        upload_to_gdrive(gdrive_service, file_name, folder_id)
        st.write("Recording saved and uploaded to Google Drive.")

# Function to save survey results to Google Drive
def save_survey_results(data, file_name, folder_id):
    df = pd.DataFrame([data])
    df.to_csv(file_name, index=False)
    upload_to_gdrive(gdrive_service, file_name, folder_id)

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
    st.write("يرجى ملء المعلومات التالية:")
    
    # Additional Information
    name = st.text_input("الإسم (اختياري):")
    special_needs = st.selectbox("هل انت من ذوي الاحتياجات الخاصة؟", ("نعم", "لا"))
    learning_disability = st.selectbox("هل تم تشخيصك على انك تعاني من صعوبات التعلم؟", ("نعم", "لا"))
    cognitive_disorder = st.selectbox("هل تعاني من مرض يؤثر على الإدراك الذهني؟", ("نعم", "لا"))
    education_level = st.selectbox("المرحلة الدراسية:", ("متوسط", "ثانوي", "جامعي"))

    passage = st.selectbox("اختر النص للقراءة:", list(passages.keys()))

    if passage:
        st.markdown(f"<div style='text-align: right; direction: rtl; font-size: 30px;'>{passages[passage]}</div>", unsafe_allow_html=True)

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
                    file_name = f"{student_id}_passage_one.wav"
                    save_audio(file_name, FOLDER_ID_PASSAGE_ONE)

        if passage == "Passage 2":
            with col3:
                if st.button("حفظ التسجيل في مجلد النص الثاني"):
                    file_name = f"{student_id}_passage_two.wav"
                    save_audio(file_name, FOLDER_ID_PASSAGE_TWO)

        if passage == "Passage 3":
            with col2:
                if st.button("حفظ التسجيل في مجلد النص الثالث"):
                    file_name = f"{student_id}_passage_three.wav"
                    save_audio(file_name, FOLDER_ID_PASSAGE_THREE)

        st.write("يرجى ملء الاستبيان لتسجيلك:")

        # Survey questions
        survey_data = {
            "student_id": student_id,
            "name": name,
            "special_needs": special_needs,
            "learning_disability": learning_disability,
            "cognitive_disorder": cognitive_disorder,
            "education_level": education_level,
            "passage": passage,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "speech_rate": st.select_slider("شعرتُ أنني تحدثت بسرعة مريحة.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "pauses_hesitations": st.select_slider("نادرًا ما توقفت أو ترددت أثناء التحدث.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "intonation": st.select_slider("كان لحديثي تنوع مناسب في استخدام طبقات الصوت.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "phoneme_usage": st.select_slider("نطقتُ الأصوات بوضوح ودقة.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "fluency_disruptions": st.select_slider("تجنبت استخدام كلمات مثل 'أم'، 'آه'، أو 'تعرف' بكثرة.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "self_corrections": st.select_slider("نادرًا ما كنت بحاجة لتكرار أو تصحيح نفسي أثناء التحدث.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "volume_loudness": st.select_slider("تحدثتُ بمستوى صوت مناسب طوال قراءة النص.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "speech_errors": st.select_slider("ارتكبتُ أخطاء قليلة أثناء التحدث.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "discourse_markers": st.select_slider("تجنبتُ الإفراط في استخدام علامات الخطاب مثل 'أم'، 'آه'، أو 'تعرف'.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "articulation_rate": st.select_slider("حافظتُ على معدل نطق متسق.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "duration_speech_segments": st.select_slider("كان طول مقاطع الحديث لدي طبيعيًا.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "pitch_variation": st.select_slider("كان لحديثي تنوع مناسب في النبرة.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "loudness_range": st.select_slider("حافظتُ على نطاق صوت مناسب.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "breathiness": st.select_slider("لم يبدو حديثي متقطعًا أو مضطربًا.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
            "speech_intelligibility": st.select_slider("كان حديثي واضحًا ومفهومًا.", options=["أعارض بشدة", "أعارض", "محايد", "أوافق", "أوافق بشدة"]),
        }

        if st.button("إرسال الاستبيان"):
            file_name = f"{student_id}_survey.csv"
            folder_id = FOLDER_ID_PASSAGE_ONE if passage == "Passage 1" else (FOLDER_ID_PASSAGE_TWO if passage == "Passage 2" else FOLDER_ID_PASSAGE_THREE)
            save_survey_results(survey_data, file_name, folder_id)
            st.write("تم حفظ نتائج الاستبيان.")

        st.write("يرجى الانتقال إلى النص التالي بعد الانتهاء من هذا النص.")
