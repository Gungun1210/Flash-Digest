import os
from fetch_sources import get_youtube_audio, fetch_news_content
from transcription import transcribe_audio
from summarizer_groq import summarize_text
from db.db_insert import save_summary_to_db
from db.database import get_db

def run_pipeline(mode: str, url: str):
    """
    Runs the summarization or transcription pipeline based on user input.

    Args:
        mode (str): Either 'summarize' or 'transcribe'
        url (str): URL of the news article or YouTube video
    """

    # Initialize database session
    try:
        db = next(get_db())
    except Exception as e:
        print(f"❌ Failed to initialize DB session: {e}")
        return

    try:
        if mode == "summarize":
            print(f"📰 Summarizing news article: {url}")
            content = fetch_news_content(url)
            summary = summarize_text(content)
            # Save summary without sentiment to DB
            save_summary_to_db(db, source=url, content=content, summary=summary)
            print("✅ Summarization completed.")
            db.commit()  # Commit the changes
            return summary

        elif mode == "transcribe":
            print(f"🎥 Transcribing YouTube video: {url}")
            audio_files = get_youtube_audio([url], base_filename="temp_audio")

            if not audio_files or not os.path.exists(audio_files[0]):
                raise FileNotFoundError("❌ Audio file not found after downloading.")

            # Perform transcription
            transcript = transcribe_audio(audio_files[0])
            summary = summarize_text(transcript)
            
            # Save summary without sentiment to DB
            save_summary_to_db(db, source=url, content=transcript, summary=summary)
            print("✅ Transcription & summarization completed.")
            
            db.commit()  # Commit the changes

            # Optional: clean up temp audio files
            try:
                os.remove(audio_files[0])
                print("✅ Temporary audio file deleted.")
            except Exception as e:
                print(f"⚠️ Failed to delete temporary audio file: {e}")

            return summary

        else:
            raise ValueError(f"❌ Invalid mode '{mode}'. Choose 'summarize' or 'transcribe'.")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Pipeline failed with error:\n{e}")
        return str(e)

    finally:
        db.close()

if __name__ == "__main__":
    # Ask user for mode and URL dynamically
    mode = input("Enter mode (summarize or transcribe): ").strip().lower()
    url = input("Enter URL: ").strip()

    # Ensure valid input for mode
    if mode not in ["summarize", "transcribe"]:
        print("❌ Invalid mode! Please choose 'summarize' or 'transcribe'.")
    else:
        summary = run_pipeline(mode=mode, url=url)
        print("\n📄 Final Output:\n", summary)
