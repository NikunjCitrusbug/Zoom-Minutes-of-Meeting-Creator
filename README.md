# Zoom Minutes of Meeting Creator

This project provides a Streamlit app that transcribes Zoom meeting audio with the Deepgram Speech-to-Text API and prepares a MOM prompt you can copy from the sidebar.

## Features

- Uploads Zoom meeting audio through a Streamlit UI
- Converts uploaded audio to `.mp3` when needed
- Sends audio to Deepgram for transcription
- Shows the transcript in the main view
- Shows a MOM-ready prompt in the sidebar drawer

## Prerequisites

- Python 3.7+
- A Deepgram API Key. You can sign up and generate an API key at [Deepgram Console](https://console.deepgram.com/).

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/zoom-meeting-minutes-creator.git
   cd zoom-meeting-minutes-creator


2. **Install Dependencies:**

   It is recommended to use a virtual environment.

   ```bash
   pip install -r requirements.txt
   ```

   **Required Packages:**

   * `requests`
   * `pydub`

3. **Install FFmpeg (Required for pydub):**

   * **macOS (Homebrew):** `brew install ffmpeg`
   * **Ubuntu/Debian:** `sudo apt install ffmpeg`
   * **Windows:** Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) and add to your system PATH

## Configuration

Enter your Deepgram API key directly in the Streamlit sidebar when you use the app.
The key is used only for the active session and is not written to the project files by the app.

## Usage

```bash
streamlit run app.py
```

### Output

* Upload a meeting recording in `.m4a`, `.mp3`, `.wav`, or `.mp4`
* Generate the transcript with Deepgram
* Review the transcript in the main panel
* Copy the MOM prompt from the sidebar drawer

## Notes

* Ensure the `.m4a` audio file is clear for optimal transcription results.
* The Deepgram free tier has usage limits. Refer to [Deepgram Pricing](https://deepgram.com/pricing) for more details.

## Author

* [Nikunj Parmar](https://github.com/NikunjCitrusbug)


