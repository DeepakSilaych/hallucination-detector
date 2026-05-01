import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")

LLM_MODEL = "gemini-2.5-flash"
WEAK_LLM_MODEL = "gemma-3-27b-it"
EMBEDDING_MODEL = "models/gemini-embedding-001"

RETRIEVAL_TOP_K = 3

SCORE_SUPPORTED = 1.0
SCORE_CONTRADICTED = -1.0
SCORE_UNKNOWN = -0.3

THRESHOLD_ACCEPT = 0.75
