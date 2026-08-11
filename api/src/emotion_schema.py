from typing import Literal, get_args

from pydantic import BaseModel, Field

Emotion = Literal[
    "joy", "trust", "fear", "surprise",
    "sadness", "disgust", "anger", "anticipation",
]


class EmotionClassification(BaseModel):
    """Plutchik's eight primary emotions, scored independently, plus overall affect."""

    joy: float = Field(ge=0, le=1)
    trust: float = Field(ge=0, le=1)
    fear: float = Field(ge=0, le=1)
    surprise: float = Field(ge=0, le=1)
    sadness: float = Field(ge=0, le=1)
    disgust: float = Field(ge=0, le=1)
    anger: float = Field(ge=0, le=1)
    anticipation: float = Field(ge=0, le=1)

    valence: float = Field(ge=-1, le=1, description="Overall positivity/negativity")
    arousal: float = Field(ge=0, le=1, description="Overall activation/intensity")

    dominant_emotion: Emotion | Literal["neutral"]
    summary: str = Field(max_length=200, description="Neutral one-sentence summary of the text's subject")

    def scores(self) -> dict[str, float]:
        return {e: getattr(self, e) for e in get_args(Emotion)}
