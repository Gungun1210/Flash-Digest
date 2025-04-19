import os
import whisper
from pytube import YouTube
from pydub import AudioSegment  # For converting to mp3 if needed

# Load the Whisper model globally (use "base", "small", etc. depending on performance needs)
model = whisper.load_model("base")

def convert_to_mp3(input_path: str, output_path: str):
    """
    Convert any audio file to mp3 format using pydub.
    """
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="mp3")
    return output_path

def transcribe_audio(audio_path):
    """
    Transcribe audio to text using Whisper.
    """
    try:
        abs_path = os.path.abspath(audio_path)
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"File not found: {abs_path}")

        result = model.transcribe(abs_path)
        print(f"Transcription successful for: {audio_path}")
        return result["text"]

    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        raise

def cleanup_file(file_path: str):
    """
    Delete the temporary file after processing.
    """
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"Deleted temporary file: {file_path}")

def download_audio_from_youtube(url: str, output_path: str = "temp_audio.mp3") -> str:
    """
    Downloads the audio from a YouTube URL and saves it as an MP3.
    
    Args:
        url (str): The YouTube video URL.
        output_path (str): Local path to save the audio file.

    Returns:
        str: Path to the downloaded audio file.
    """
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        downloaded_file = audio_stream.download(filename=output_path)
        
        # If the file isn't mp3, convert it to mp3
        if not downloaded_file.endswith(".mp3"):
            mp3_file = downloaded_file.replace(".webm", ".mp3")  # Adjust according to the format
            convert_to_mp3(downloaded_file, mp3_file)
            os.remove(downloaded_file)  # Remove the original non-mp3 file
            print(f"Converted audio to mp3: {mp3_file}")
            return mp3_file
        
        print(f"Downloaded audio to: {downloaded_file}")
        return downloaded_file

    except Exception as e:
        raise Exception(f"Failed to download audio from YouTube: {e}")

def transcribe_url(url: str) -> str:
    """
    Downloads and transcribes audio from a given URL (YouTube link).
    
    Args:
        url (str): YouTube URL.

    Returns:
        str: Transcribed text.
    """
    try:
        audio_file_path = download_audio_from_youtube(url)
        transcription_result = transcribe_audio(audio_file_path)
        cleanup_file(audio_file_path)  # Clean up the downloaded audio file
        return transcription_result
    except Exception as e:
        raise Exception(f"Error during URL transcription: {e}")
