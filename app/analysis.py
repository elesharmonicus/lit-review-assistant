# Keyword frequency analysis of abstracts
from collections import Counter
import re
import pandas as pd

STOPWORDS = {
    "the",
    "and",
    "of",
    "in",
    "to",
    "with",
    "and",
    "for",
    "on",
    "is",
    "that",
    "as",
    "are",
    "by",
    "was",
    "be",
    "this",
    "which",
    "or",
    "from",
    "at",
    "it",
    "an",
    "we",
    "can",
    "not",
    "have",
    "has",
    "but",
    "all",
    "they",
    "their",
    "may",
    "a"
}


def clean_and_tokenize(text):
    """Convert text into filtered word tokens."""

    words = re.findall(r"\b\w+\b", text.lower())

    return [
        word
        for word in words
        if word not in STOPWORDS
    ]


def analyze_abstracts(abstracts):
    """Analyze abstracts to find the most common keywords."""
    word_freq = Counter()
    for abstract in abstracts:
        words = clean_and_tokenize(abstract)
        word_freq.update(words)
    return Counter(word_freq).most_common(20)  # Return top 20 most common words

def main():
    df = pd.read_csv('data/pubmed_results.csv')
    abstracts = df['abstract'].dropna().tolist()
    top_words = analyze_abstracts(abstracts)
    print("Top 20 most common words in abstracts:")
    for word, freq in top_words:
        print(f"{word}: {freq}")

if __name__ == "__main__":
    main()