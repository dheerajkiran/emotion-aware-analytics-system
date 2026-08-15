from pydantic import BaseModel


class StorylineOut(BaseModel):
    headline: str
    summary: str
    subreddit: str
    dominant_emotion: str
    emotion_scores: dict[str, float]
    valence: float
    arousal: float
    engagement_velocity: float
    priority: float
    post_count: int
    sample_urls: list[str]


class LandscapeResponse(BaseModel):
    generated_at: str
    subreddits: list[str]
    post_count: int
    storyline_count: int
    storylines: list[StorylineOut]
