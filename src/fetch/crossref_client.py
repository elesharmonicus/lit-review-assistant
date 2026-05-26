import requests
import os
import re
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

TITLE_SIMILARITY_THRESHOLD = 0


def _strip_jats(text: str) -> str:
    """Remove JATS XML tags and leading 'Abstract' label from CrossRef text."""
    text = re.sub(r'<[^>]+>', '', text)   # strip tags first
    text = re.sub(r'^Abstract\s*', '', text.strip())  # then remove prefix
    return text.strip()


def _title_similarity(a: str, b: str) -> float:
    """Return normalised similarity ratio between two title strings (0–1)."""
    def normalise(s: str) -> str:
        s = s.lower()
        s = re.sub(r'[^\w\s]', '', s)  # remove punctuation
        return re.sub(r'\s+', ' ', s).strip()
    return SequenceMatcher(None, normalise(a), normalise(b)).ratio()


def fetch_abstract_crossref(doi: str) -> str:
    """Fetch abstract for a paper from CrossRef API using its DOI.
    Returns empty string if not found or on error."""
    email = os.getenv("CROSSREF_EMAIL", "")
    headers = {"User-Agent": f"lit-review-assistant/1.0 (mailto:{email})"}
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return _strip_jats(data['message'].get('abstract', ''))
    except (requests.RequestException, KeyError):
        return ""


def fetch_abstract_by_title(title: str) -> str:
    """Fetch abstract for a paper from CrossRef API using title search.

    Performs a fuzzy similarity check against the returned title to avoid
    returning an abstract for a different paper. Returns empty string if
    similarity is below TITLE_SIMILARITY_THRESHOLD or on any error.
    """
    email = os.getenv("CROSSREF_EMAIL", "")
    headers = {"User-Agent": f"lit-review-assistant/1.0 (mailto:{email})"}
    url = f"https://api.crossref.org/works?query.title={requests.utils.quote(title)}&rows=1"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data['message'].get('items', [])
        if not items:
            return ""
        fetched_title = items[0].get('title', [''])[0]
        similarity = _title_similarity(title, fetched_title)
        if similarity < TITLE_SIMILARITY_THRESHOLD:
            logger.debug(
                "Title match rejected (%.2f < %.2f): '%s' vs '%s'",
                similarity, TITLE_SIMILARITY_THRESHOLD,
                title[:60], fetched_title[:60],
            )
            return ""
        return _strip_jats(items[0].get('abstract', ''))
    except (requests.RequestException, KeyError):
        return ""