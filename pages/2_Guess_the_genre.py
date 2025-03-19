import streamlit as st
import base64


# Custom CSS to change the text and background color globally
def apply_custom_styles():
    st.markdown("""
        <style>
        /* Change text color globally */
        * {
            color: #e38a78 !important;
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
            color: #e38a78 !important;
            border: 1px solid #e38a78 !important;
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


# ---------------------------------------------------

# Website Header
st.markdown("""
    <h1 style="text-align: center; color: #ecd4cf;">Guess The Genre</h1>
    <br>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])  # Adjusted columns to balance the layout

with col1:
    st.markdown("<br>" * 3, unsafe_allow_html=True)
    audio1 = st.audio("audios/nocturne_op9.mp3", format="audio/mp3")
    toggle1 = st.checkbox("Frédéric Chopin")
    if toggle1:
        st.write("Classical")
    else:
        st.write("")

    st.markdown("<br>" * 3, unsafe_allow_html=True)
    audio2 = st.audio("audios/purple_haze.mp3", format="audio/mp3")
    toggle2 = st.checkbox("Jimmy Henrix")
    if toggle2:
        st.write("Rock")
    else:
        st.write("")

    st.markdown("<br>" * 4, unsafe_allow_html=True)
    audio3 = st.audio("audios/mashrou_we_need.mp3", format="audio/mp3")
    toggle3 = st.checkbox("Mashrou Leila")
    if toggle3:
        st.write("We don't know either")
    else:
        st.write("")


with col2:
    st.image("images/chopinladieslisten.jpg", use_container_width=True)

    st.image("images/jimmy-henrix.png", use_container_width=True)

    st.image("images/mashrou_leila.jpeg", use_container_width=True)
