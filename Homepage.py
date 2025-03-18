import streamlit as st
import requests
import io
import numpy as np
import wave
import tempfile
from pydub import AudioSegment
import base64

# -------------------------------- STYLING -------------------------------------

# Custom CSS to change the text and background color globally
def apply_custom_styles():
    st.markdown("""
        <style>
        /* Change text color globally */
        * {
            color: #ecd4cf !important;
        }

        /* Dark background for file uploader and audio uploader */
        div.stFileUploader, div.stAudio {
            background-color: #2a2a2a !important;
            border-radius: 10px;
            padding: 10px;
        }

        /* Style the buttons inside uploaders */
        div.stFileUploader button, div.stAudio button {
            background-color: #444 !important;
            color: #ecd4cf !important;
            border: 1px solid #ecd4cf !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Apply the styles
apply_custom_styles()

# Background Image
# Function to encode image to Base64
def get_base64(file_path):
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.error("Background image not found. Make sure the file path is correct.")
        return ""

# Store background in session_state to persist across reruns -> It doesn't need to reload the photo every time
if "base64_bg" not in st.session_state:
    image_path = "images/music-8559592.jpg"
    st.session_state["base64_bg"] = get_base64(image_path)

# Apply CSS background
st.markdown(
    f"""
    <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{st.session_state['base64_bg']}");
            background-size: cover;
        }}
    </style>
    """,
    unsafe_allow_html=True
)


# ------------------------------------ API -------------------------------------


# API Endpoint
post_api = "https://kmeansklang-364885724897.europe-west1.run.app/predict"

# Website Header
st.markdown("""
    <h1 style="text-align: center; color: #ecd4cf;">K-Means-Klang</h1>
    <h4 style="text-align: center; color: #ecd4cf;">
    Welcome to the K-means-Klang Project.
    Give us a song, we'll give you its cluster.
    </h4><br>
""", unsafe_allow_html=True)

def load_image(path):
    with open(path, 'rb') as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    return encoded

# Callback function - gives info when audio is changed
def my_callback():
    st.write("Audio input has changed!")

# Function to send the audio to the API
def send_audio_to_api(audio_file_path):
    """Function to send recorded audio to the API."""
    with open(audio_file_path, "rb") as f:
        files = {"audio_file": ("audio.wav", f, "audio/wav")}

        response = requests.post(post_api, files=files)

        if response.status_code == 200:
            # st.success("Audio successfully sent for analysis!")
            try:
                result = response.json()
                prediction = result.get('predicted_cluster')
                st.markdown(f'<h4 style="text-align: center;">Predicted Cluster: {result.get("predicted_cluster")}</h1>', unsafe_allow_html=True)
                cluster_img_path = f"images/cluster_{prediction}.png"
                st.write(f'''
                    <div style="text-align: center;">
                        <img src="data:image/jpg;base64,{load_image(cluster_img_path)}" style="max-width: 500px; width: 100%; height: auto; display: inline-block;">
                    </div>
                ''', unsafe_allow_html=True)
                # st.write(f'''
                #     <div style="text-align: center;">
                #         <img src="data:image/jpg;base64,{load_image(cluster_img_path)}" style="width: 400px; height: 400px; display: inline-block;">
                #     </div>
                # ''', unsafe_allow_html=True)
            except ValueError:
                st.error("Error: Unable to parse response from the API.")
        else:
            st.error(f"Failed to send audio. Status code: {response.status_code} - {response.text}")


# Audio File Uploader
audio_file = st.file_uploader("Give me an audio file:",
                              type=["wav", "mp3", "flac"],
                              accept_multiple_files=False,
                              help="The type of the file must be .wav, .mp3, or .flac",
                              on_change=my_callback)


# If an audio file is uploaded
if audio_file:
    st.audio(audio_file.getvalue(), format="audio/wav")
    # st.write("File uploaded successfully!")

    # Read file as bytes
    audio_file_bytes = audio_file.getvalue()
    # st.write(f"File size: {len(audio_file_bytes) / 1024:.2f} KB")

    # Extract file type from extension (either mp3, flac, or wav)
    file_type = audio_file.name.split(".")[-1]

    # Convert audio to WAV if it's not already in WAV format
    if file_type != "wav":  # If not WAV, convert to WAV
        audio = AudioSegment.from_file(io.BytesIO(audio_file_bytes), format=file_type)
        audio_bytes = io.BytesIO()
        audio.export(audio_bytes, format="wav")
        audio_bytes.seek(0)
        # Save the audio as a temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            temp_wav.write(audio_bytes.read())
            temp_wav.close()
            send_audio_to_api(temp_wav.name)
    else:
        # If it's already a WAV file, just send it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            temp_wav.write(audio_file_bytes)
            temp_wav.close()
            send_audio_to_api(temp_wav.name)

# Streamlit UI - Record Audio (Second)
st.markdown('''<br>
            <h4 style="text-align: center;">Record your Voice</h4>''',
            unsafe_allow_html=True)

# Audio input with on_change callback
recording = st.audio_input("Let me hear your voice:", key="recording", on_change=my_callback)

# If audio has been recorded, we process it
if recording:
    st.write("Recording complete. Sending audio to the API...")

    # Convert the UploadedFile to bytes
    if isinstance(recording, st.runtime.uploaded_file_manager.UploadedFile):
        # Get the raw bytes from the UploadedFile object
        recording_data = recording.getvalue()
        # st.write("Recording is in bytes format.")

        try:
            # Create a wave file-like object from the byte data
            wav_file = io.BytesIO(recording_data)
            with wave.open(wav_file, 'rb') as wav:
                # Get properties of the audio file
                framerate = wav.getframerate()
                num_frames = wav.getnframes()
                audio_data = wav.readframes(num_frames)

                # Convert the audio byte data into numpy array
                audio_samples = np.frombuffer(audio_data, dtype=np.int16)

                # Ensure we have valid audio samples (must be an array of integers)
                # st.write(f"Audio data length: {len(audio_samples)} samples")

                # Save the numpy array as a .wav file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                    with wave.open(temp_wav, 'wb') as wav_out:
                        wav_out.setnchannels(1)  # Mono audio
                        wav_out.setsampwidth(2)  # 16-bit audio
                        wav_out.setframerate(framerate)
                        wav_out.writeframes(audio_samples.tobytes())

                    # Send the temporary .wav file to the API
                    send_audio_to_api(temp_wav.name)

        except Exception as e:
            st.error(f"Error processing audio: {e}")
    else:
        st.error("Error: Recorded audio is not in the expected format.")



# cluster_img_path = f"images/cluster_4.png"
# # "\\wsl.localhost\Ubuntu\home\kartseleni\code\kartseleni\k-means-klang-website\images\cluster_test.png"

# st.write(f'''
#     <div style="text-align: center;">
#         <img src="data:image/jpg;base64,{load_image(cluster_img_path)}" style="max-width: 500px; width: 100%; height: auto; display: inline-block;">
#     </div>
# ''', unsafe_allow_html=True)
