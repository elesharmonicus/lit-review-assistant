# Keyword frequency analysis of abstracts
from collections import Counter
import re
import nltk
import pandas as pd
import matplotlib.pyplot as plt
import ast
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from nltk.stem import WordNetLemmatizer
from src.config import DATA_DIR
import logging

logger = logging.getLogger(__name__)

nltk.download('wordnet', quiet=True)

DOMAIN_STOPWORDS = {
    "using", "used", "use", "based", "method", "methods",
    "study", "studies", "result", "results", "data",
    "high", "time", "new", "also", "may", "however"
}
STOPWORDS = set(ENGLISH_STOP_WORDS) | DOMAIN_STOPWORDS
TOP_N = 20
lemmatizer = WordNetLemmatizer()

def clean_and_tokenize(text):
    """Convert text into filtered word tokens."""

    words = re.findall(r"\b\w+\b", re.sub(r"[^a-z\s]", ' ', text.lower()))

    return [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in STOPWORDS and len(word) > 2 and not word.isnumeric()
    ]


def analyze_abstracts(abstracts):
    """Analyze abstracts to find the most common keywords."""
    word_freq = Counter()
    for abstract in abstracts:
        words = clean_and_tokenize(abstract)
        word_freq.update(words)
    return word_freq.most_common(TOP_N)  # Return top N most common words


def plot_publication_trends(df):
    """Plot the number of publications per year."""
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.replace("", pd.NA)
    df = df.dropna(subset=['year'])
    yearly_counts = df['year'].value_counts().sort_index()
    plt.figure(figsize=(10, 6))
    plt.plot(yearly_counts.index, yearly_counts.values, marker='o')
    plt.title('Number of Publications per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Publications')
    plt.grid()
    plt.tight_layout()
    plt.savefig(DATA_DIR / "year_trends.png")
    plt.close()


def analyze_authors(df):
    """Analyze authors to find the most prolific ones."""
    author_freq = Counter()
    for authors in df['authors'].dropna():
        if isinstance(authors, str):
            try:
                authors_list = ast.literal_eval(authors)
                author_freq.update(authors_list)
            except (ValueError, SyntaxError):
                continue
    return author_freq.most_common(TOP_N)  # Return top N most prolific authors

def main(input_file):
    df = pd.read_csv(input_file)
    logger.info(f"Loaded data from {input_file}")
    abstracts = df['abstract'].dropna().tolist()
    top_words = analyze_abstracts(abstracts)
    print(f"Top {TOP_N} most common words in abstracts:")
    for word, freq in top_words:
        print(f"{word}: {freq}")

    plot_publication_trends(df)
    top_authors = analyze_authors(df)
    print(f"\nTop {TOP_N} most prolific authors:")
    for author, freq in top_authors:
        print(f"{author}: {freq}")  
