from db.database import engine
from models import Summary

# Create the Summaries table if it doesn't exist
Summary.__table__.create(bind=engine, checkfirst=True)

print("✅ Table checked/created successfully.")
