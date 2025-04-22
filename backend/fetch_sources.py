import os
import requests
import newspaper
import yt_dlp as youtube_dl
from pathlib import Path
from db.db_insert import save_summary_to_db  # Import your save function
from db.database import get_db  # Import the database session

# Load your Groq API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_youtube_audio(youtube_urls, base_filename="audio"):
    """
    Downloads the audio from the given YouTube URLs.

    Args:
        youtube_urls (list): A list of YouTube URLs to download audio from.
        base_filename (str): Base name for the saved audio files.

    Returns:
        list: A list of paths to the downloaded audio files.
    """
    Path("./downloads").mkdir(parents=True, exist_ok=True)
    audio_files = []

    for i, url in enumerate(youtube_urls):
        try:
            output_name = f"./downloads/{base_filename}_{i}.%(ext)s"
            
            # Updated ydl_opts with logging
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_name,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': False  # Set to False to see download progress
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_path = f"./downloads/{base_filename}_{i}.mp3"
                if os.path.exists(downloaded_path):
                    audio_files.append(downloaded_path)
                else:
                    print(f"❌ Audio not found at expected path: {downloaded_path}")
        except Exception as e:
            print(f"❌ Error downloading audio from {url}: {e}")

    return audio_files

def fetch_news_content(url):
    try:
        article = newspaper.Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        raise Exception(f"Error fetching news article from {url}: {e}")

def summarize_text(text):
    if not GROQ_API_KEY:
        raise Exception("Groq API key is not set in the environment variables.")
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a summarizer that gives concise and informative summaries of news content."},
            {"role": "user", "content": f"Summarize the following news content:\n\n{text}"}
        ],
        "temperature": 0.5
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error in API request: {str(e)}")
    except (KeyError, IndexError) as e:
        raise Exception(f"Unexpected response format from Groq API. Error: {str(e)}")

def process_user_request(url=None, text=None):
    if url:
        content = fetch_news_content(url)
    elif text:
        content = text
    else:
        raise Exception("No content provided for summarization.")
    
    return summarize_text(content)

def fetch_sources(youtube_urls=None, news_urls=None, raw_texts=None):
    """
    Fetches audio and text summaries from provided sources and saves them to the database.

    Returns:
        dict: A dictionary containing 'audio_files' and 'summaries' with status information.
    """
    audio_files = []
    summaries = []

    # Initialize the database session
    db = next(get_db())

    if youtube_urls:
        audio_files = get_youtube_audio(youtube_urls, base_filename="audio")

    if news_urls:
        for url in news_urls:
            try:
                article_text = fetch_news_content(url)
                summary = summarize_text(article_text)
                
                # Save the summary in the database with "NEUTRAL" sentiment
                save_summary_to_db(db, source=url, content=article_text, summary=summary, sentiment="NEUTRAL")

                summaries.append(summary)
            except Exception as e:
                print(f"❌ Error summarizing article {url}: {e}")
                summaries.append(None)

    if raw_texts:
        for text in raw_texts:
            try:
                summary = summarize_text(text)
                
                # Save the summary in the database with "NEUTRAL" sentiment
                save_summary_to_db(db, source="Raw Text", content=text, summary=summary, sentiment="NEUTRAL")

                summaries.append(summary)
            except Exception as e:
                print(f"❌ Error summarizing raw text: {e}")
                summaries.append(None)

    # Commit and close the session
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Error during commit to database: {e}")
    finally:
        db.close()

    return {
        "audio_files": audio_files,
        "summaries": summaries
    }
