import anthropic
from pydantic_ai import Agent
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from . import config
from .emotion_schema import EmotionClassification

SYSTEM_PROMPT = """\
You are an emotion-classification engine. Given a social media post, score it against \
Plutchik's eight primary emotions: joy, trust, fear, surprise, sadness, disgust, anger, \
anticipation. Score each emotion independently by how strongly it is present in the text, \
0 (absent) to 1 (extreme) - they are not mutually exclusive and do not need to sum to 1. \
Also give an overall valence (-1 very negative to 1 very positive) and arousal (0 calm to \
1 highly activated), the single most prominent emotion (or "neutral" if none is clear), and \
a neutral one-sentence summary (<=20 words) of what the text is about, not of its emotion. \
Base every score only on the text given - do not speculate about the author beyond what's written.\
"""

_RETRYABLE_ERRORS = (
    anthropic.RateLimitError,
    anthropic.APIConnectionError,
    anthropic.InternalServerError,
    anthropic.APITimeoutError,
    anthropic.OverloadedError,
)

_agent = Agent(
    model=f"anthropic:{config.CLAUDE_MODEL}",
    output_type=EmotionClassification,
    system_prompt=SYSTEM_PROMPT,
)


@retry(
    retry=retry_if_exception_type(_RETRYABLE_ERRORS),
    wait=wait_exponential(multiplier=1, min=1, max=20),
    stop=stop_after_attempt(4),
)
async def classify_text(text: str) -> EmotionClassification:
    result = await _agent.run(text[:4000])
    return result.output
