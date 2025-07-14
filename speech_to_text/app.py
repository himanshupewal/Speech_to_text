import streamlit as st
from audiorecorder import audiorecorder
from pydub import AudioSegment
import io
import whisper
import os
import base64



# Load Whisper model (cache to avoid reloading)
@st.cache_resource
def load_model(model_size):
    return whisper.load_model(model_size)

# Function to encode image to base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Record & playback function
def record_and_playback(start_label="🎙️ Start Recording", stop_label="⏹️ Stop Recording"):
    audio = audiorecorder(start_label, stop_label)
    if len(audio) > 0:
        st.success(f"✅ Recorded {audio.duration_seconds:.2f} seconds")

        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)

        st.audio(wav_io, format="audio/wav")
        return audio, wav_io
    else:
        return None, None

# Transcription function
def transcribe_audio(wav_io, model, language):
    temp_path = "audio/temp_audio.wav"
    os.makedirs("audio", exist_ok=True)

    data, samplerate = sf.read(wav_io)
    sf.write(temp_path, data, samplerate)

    with st.spinner("🔍 Transcribing..."):
        options = {"language": language} if language != "auto" else {}
        result = model.transcribe(temp_path, **options)

    return result["text"]

# Streamlit config
st.set_page_config(page_title="🎙️ Speech-to-Text", layout="centered")


# Custom CSS for button styling
st.markdown("""
    <style>
    .stButton>button {
        background-color: #ff4c4c;
        color: #ffffff;
        border: none;
        border-radius: 30px;
        padding: 0.75em 2em;
        font-size: 18px;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(255, 76, 76, 0.3);
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.6em;
        margin-top: 1.5em;
    }

    .stButton>button:hover {
        background-color: #ff1c1c;
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(255, 28, 28, 0.45);
    }

    .center-button {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)



# Title and intro text
st.title("🎙️ Speech-to-Text Transcriber")
st.markdown("Press **Start Recording** to capture your audio. Then **stop it** to listen and transcribe.")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    model_size = st.selectbox("Select Whisper Model Size", ["tiny", "base", "small", "medium"], index=1)
    language = st.selectbox("Select Language", ["auto", "en", "hi", "fr", "de", "es", "zh"], index=0)

# Load Whisper model
model = load_model(model_size)

# Audio recording
audio, wav_io = record_and_playback()

# Transcription button
if audio:
    if st.button("Transcribe"):
        transcription = transcribe_audio(wav_io, model, language)
        st.subheader("Transcription Result:")
        st.markdown(f"<p style='font-size:20px;'>{transcription}</p>", unsafe_allow_html=True)
