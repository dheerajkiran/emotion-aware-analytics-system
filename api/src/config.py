import os

from dotenv import load_dotenv

load_dotenv()

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5")

REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "emotion-aware-analytics-system")
REDDIT_SUBREDDITS = [
    s.strip() for s in os.environ.get("REDDIT_SUBREDDITS", "news,worldnews,technology").split(",") if s.strip()
]
MIN_ENGAGEMENT_SCORE = int(os.environ.get("MIN_ENGAGEMENT_SCORE", "20"))

DATABASE_URL = os.environ.get("DATABASE_URL", "")

EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

PRIORITY_ENGAGEMENT_WEIGHT = float(os.environ.get("PRIORITY_ENGAGEMENT_WEIGHT", "0.5"))
PRIORITY_EMOTION_WEIGHT = float(os.environ.get("PRIORITY_EMOTION_WEIGHT", "0.5"))
CLASSIFICATION_FRESHNESS_HOURS = float(os.environ.get("CLASSIFICATION_FRESHNESS_HOURS", "6"))

CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
