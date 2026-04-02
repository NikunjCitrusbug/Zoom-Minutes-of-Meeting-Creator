import os
import tempfile
from datetime import date
from pathlib import Path

import requests
import streamlit as st
from pydub import AudioSegment

DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"
MOM_PROMPT_PATH = Path(__file__).with_name("MOM_PROMPT")
SUPPORTED_AUDIO_TYPES = ["m4a", "mp3", "wav", "mp4"]


def convert_audio_to_mp3(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="mp3")
    return output_path


def load_mom_template():
    if MOM_PROMPT_PATH.exists():
        return MOM_PROMPT_PATH.read_text(encoding="utf-8").strip()

    return (
        "Minutes of Meeting\n"
        "Date: [Date provided]\n"
        "Updates\n\n"
        "Discussion Points\n\n"
        "Action Points"
    )


def build_mom_prompt(meeting_date, transcript):
    prompt_template = load_mom_template()
    return (
        f"{prompt_template}\n\n"
        f"Meeting date: {meeting_date}\n"
        "Full meeting transcription:\n"
        f"{transcript}"
    )


def transcribe_audio(audio_file_path, api_key):
    if not api_key:
        raise RuntimeError("Missing Deepgram API key.")

    headers = {"Authorization": f"Token {api_key}"}
    params = {
        "model": "nova-2",
        "smart_format": "true",
        "punctuate": "true",
        "diarize": "true",
    }

    with open(audio_file_path, "rb") as audio_file:
        response = requests.post(
            DEEPGRAM_URL,
            headers=headers,
            params=params,
            files={"file": audio_file},
            timeout=300,
        )

    if response.ok:
        return (
            response.json()
            .get("results", {})
            .get("channels", [{}])[0]
            .get("alternatives", [{}])[0]
            .get("transcript", "")
            .strip()
        )

    try:
        error_details = response.json()
    except ValueError:
        error_details = response.text

    raise RuntimeError(f"Deepgram transcription failed: {error_details}")


def process_uploaded_audio(uploaded_file, api_key):
    temp_paths = []

    try:
        file_suffix = Path(uploaded_file.name).suffix.lower() or ".m4a"
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as source_file:
            source_file.write(uploaded_file.getbuffer())
            source_path = source_file.name
        temp_paths.append(source_path)

        mp3_path = source_path
        if file_suffix != ".mp3":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as target_file:
                mp3_path = target_file.name
            temp_paths.append(mp3_path)
            convert_audio_to_mp3(source_path, mp3_path)

        return transcribe_audio(mp3_path, api_key)
    finally:
        for temp_path in temp_paths:
            try:
                os.remove(temp_path)
            except OSError:
                pass


def render_sidebar():
    with st.sidebar:
        st.header("Deepgram")
        api_key = st.text_input(
            "API key",
            type="password",
            placeholder="Enter your Deepgram API key",
            help="Used only for this active session. It is not written to disk by the app.",
        )
        st.caption("Your API key is only used at runtime and is not stored in the project.")

        st.divider()
        st.header("MOM Drawer")

        if st.session_state.mom_prompt:
            st.caption("Copy this prompt into your preferred AI tool to create the MOM.")
            st.text_area(
                "MOM prompt",
                value=st.session_state.mom_prompt,
                height=420,
            )
            st.download_button(
                "Download MOM prompt",
                data=st.session_state.mom_prompt,
                file_name="mom_prompt.txt",
                mime="text/plain",
            )
        else:
            st.info("Generate a transcription to populate the MOM drawer.")

    return api_key


def main():
    st.set_page_config(
        page_title="Zoom Minutes of Meeting Creator",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "transcript" not in st.session_state:
        st.session_state.transcript = ""
    if "mom_prompt" not in st.session_state:
        st.session_state.mom_prompt = ""

    st.title("Zoom Minutes of Meeting Creator")
    st.write(
        "Upload meeting audio, transcribe it with Deepgram, and use the sidebar drawer "
        "to copy a MOM-ready prompt."
    )

    api_key = render_sidebar()

    with st.form("transcription_form"):
        meeting_date = st.date_input("Meeting date", value=date.today())
        uploaded_file = st.file_uploader(
            "Upload meeting audio",
            type=SUPPORTED_AUDIO_TYPES,
            accept_multiple_files=False,
            help="Supported formats: .m4a, .mp3, .wav, .mp4. Upload one file at a time.",
        )
        submitted = st.form_submit_button("Generate transcription")

    if submitted:
        if not uploaded_file:
            st.error("Please upload an audio file first.")
        elif not api_key:
            st.error("Please enter your Deepgram API key in the sidebar.")
        else:
            with st.spinner("Converting audio and generating transcription..."):
                try:
                    transcript = process_uploaded_audio(uploaded_file, api_key)
                except Exception as exc:
                    st.error(str(exc))
                else:
                    if not transcript:
                        st.warning("Deepgram returned an empty transcript.")
                    else:
                        st.session_state.transcript = transcript
                        st.session_state.mom_prompt = build_mom_prompt(
                            meeting_date.strftime("%Y-%m-%d"),
                            transcript,
                        )
                        st.success("Transcription generated. The MOM drawer is now ready.")
                        st.rerun()

    if st.session_state.transcript:
        st.subheader("Transcript")
        st.text_area(
            "Generated transcription",
            value=st.session_state.transcript,
            height=420,
        )
        st.download_button(
            "Download transcript",
            data=st.session_state.transcript,
            file_name="transcript.txt",
            mime="text/plain",
        )


if __name__ == "__main__":
    main()
