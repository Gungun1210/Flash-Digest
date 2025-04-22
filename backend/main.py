from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from summarizer_groq import summarize_text  # Function for summarization
from transcription import transcribe_audio  # Function for transcription
import os
from fetch_sources import get_youtube_audio, fetch_news_content
from db.db_insert import save_summary_to_db
from db.database import get_db

app = FastAPI()

# CORS middleware to allow cross-origin requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # You can restrict this to your frontend URL in production, e.g., ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

class ProcessRequest(BaseModel):
    url: str
    mode: str  # 'summarize' or 'transcribe'

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
        return {"error": f"Failed to initialize DB session: {e}"}

    try:
        if mode == "summarize":
            print(f"📰 Summarizing news article: {url}")
            content = fetch_news_content(url)
            summary = summarize_text(content)
            # Save summary to DB
            save_summary_to_db(db, source=url, content=content, summary=summary)
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
            
            # Save summary to DB
            save_summary_to_db(db, source=url, content=transcript, summary=summary)
            db.commit()  # Commit the changes
            return summary

        else:
            raise ValueError(f"❌ Invalid mode '{mode}'. Choose 'summarize' or 'transcribe'.")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Pipeline failed with error:\n{e}")
        return {"error": f"An error occurred: {str(e)}"}

    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Welcome to the API!"}

@app.post("/process")
async def process_request(data: ProcessRequest):
    try:
        if data.mode not in ["summarize", "transcribe"]:
            raise HTTPException(status_code=400, detail="Invalid mode selected. Choose either 'summarize' or 'transcribe'.")

        # Call the pipeline function based on mode
        result = run_pipeline(mode=data.mode, url=data.url)

        # Return result to the user
        return {"result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

