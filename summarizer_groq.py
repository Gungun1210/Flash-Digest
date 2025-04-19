import os
import requests
import newspaper
from db.database import SessionLocal  # Assuming you're using SQLAlchemy with a session
from models import Summary  # Assuming your Summary model is imported from models.py

# Load your Groq API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Ensure it's set in your .env file
API_URL = "https://api.groq.com/openai/v1/chat/completions"  # Correct endpoint for Groq's chat API

def fetch_news_content(url):
    """
    Fetches and parses text from a news article.
    """
    try:
        article = newspaper.Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        raise Exception(f"Error fetching news article from {url}: {e}")

def summarize_text(text):
    """
    Summarizes the given text using Groq's LLM API.
    """
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

def save_summary_to_db(source, content, summary):
    """
    Function to save the summary to the database with a fixed "NEUTRAL" sentiment.
    """
    # Create a new Summary instance
    db_session = SessionLocal()  # Initialize the database session
    summary_entry = Summary(
        source=source,
        content=content,
        summary=summary,
        sentiment="NEUTRAL"  # Always set the sentiment as 'NEUTRAL'
    )
    # Add to the session and commit
    db_session.add(summary_entry)
    db_session.commit()
    db_session.close()  # Close the session to prevent memory leaks

def summarize_url(url: str):
    """
    Summary interface function for main.py.
    """
    content = fetch_news_content(url)
    summary = summarize_text(content)
    save_summary_to_db(url, content, summary)  # Save summary to DB with "NEUTRAL" sentiment
    return summary

def process_user_request(url=None, text=None):
    """
    Unified interface for summarizing either a URL or raw text.
    """
    if url:
        content = fetch_news_content(url)
    elif text:
        content = text
    else:
        raise Exception("No content provided for summarization.")
    
    summary = summarize_text(content)
    save_summary_to_db("User Input", content, summary)  # Save user input summary to DB with "NEUTRAL" sentiment
    return summary

def fetch_sources(youtube_urls=None, news_urls=None, raw_texts=None):
    """
    Fetches and processes audio + summarization based on various sources.
    """
    audio_files = []
    summaries = []

    # Assuming get_youtube_audio is defined somewhere
    if youtube_urls:
        if isinstance(youtube_urls, list) and all(isinstance(url, str) for url in youtube_urls):
            audio_files = get_youtube_audio(youtube_urls)
        else:
            print("Error: youtube_urls is not a valid list of strings.")

    if news_urls:
        for news_url in news_urls:
            try:
                text = fetch_news_content(news_url)
                summary = summarize_text(text)
                save_summary_to_db(news_url, text, summary)  # Save summary to DB with "NEUTRAL" sentiment
                summaries.append(summary)
            except Exception as e:
                print(f"Error summarizing news article {news_url}: {e}")
                summaries.append(None)

    if raw_texts:
        for raw_text in raw_texts:
            try:
                summary = summarize_text(raw_text)
                save_summary_to_db("Raw Text", raw_text, summary)  # Save raw text summary to DB with "NEUTRAL" sentiment
                summaries.append(summary)
            except Exception as e:
                print(f"Error summarizing raw text: {e}")
                summaries.append(None)

    return {
        'audio_files': audio_files,
        'summaries': summaries
    }
