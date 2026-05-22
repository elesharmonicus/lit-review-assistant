from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_OUTPUT_FILE = DATA_DIR / "pubmed_results.csv"
DEFAULT_MAX_RESULTS = 100
DEFAULT_SORT_MODE = "relevance"
