# db_insert.py
from sqlalchemy.orm import Session
from models import Summary  # Assuming you're using a relative import for the Summary model

def save_summary_to_db(db: Session, source: str, content: str, summary: str):
    """
    Save a news summary with a neutral sentiment to the database.

    Args:
        db (Session): SQLAlchemy session object.
        source (str): URL or description of the source.
        content (str): Original content (article text or raw text).
        summary (str): AI-generated summary of the content.
    """
    # Sentiment is hardcoded as "NEUTRAL"
    new_summary = Summary(
        source=source,
        content=content,
        summary=summary,
        language="English",  # Assuming the content is always in English
        sentiment="NEUTRAL"  # Sentiment is now always neutral
    )

    try:
        db.add(new_summary)
        db.commit()  # Commit the new summary to the database
        db.refresh(new_summary)  # Refresh to get the latest changes
        print(f"✅ Summary from '{source}' saved successfully with sentiment: NEUTRAL")
    except Exception as e:
        db.rollback()  # Rollback in case of any errors
        print(f"❌ Error while saving summary: {e}")
        return False  # Return false indicating failure
    return True  # Return true indicating success
