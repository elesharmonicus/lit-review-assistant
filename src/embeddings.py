from pathlib import Path
import pandas as pd
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from src.config import load_config
from src.config import DATA_DIR

DATA_PATH = DATA_DIR / "pubmed_results.csv"
TOP_N = 5

def build_similarity_matrix(abstracts: list[str]) -> torch.Tensor:
    """Vectorize abstracts and compute a dot-product similarity matrix using torch."""
    config = load_config()
    max_features = config.get('embeddings', {}).get('max_features', 1000)
    vectorizer = TfidfVectorizer(stop_words="english", max_features=max_features, norm='l2')
    X = vectorizer.fit_transform(abstracts)
    # Convert to float tensor: shape (num_papers, vocab_size)
    X_tensor = torch.tensor(X.toarray(), dtype=torch.float32)
    return X_tensor @ X_tensor.T  # shape (num_papers, num_papers)


def build_embedding_similarity_matrix(abstracts: list[str]) -> torch.Tensor:
    """Compute similarity matrix from SentenceTransformer embeddings."""
    config = load_config()
    model_name = config.get('embeddings', {}).get('model', 'all-MiniLM-L6-v2')
    model = SentenceTransformer(model_name)
    emb = torch.tensor(model.encode(abstracts))
    norms = emb.norm(dim=1, keepdim=True).clamp(min=1e-8)
    emb_norm = emb / norms
    emb_sim = emb_norm @ emb_norm.T
    return emb_sim

def find_similar_papers(similarity_matrix: torch.Tensor, paper_index: int, top_n: int = TOP_N) -> torch.Tensor:
    """Return indices of the top_n most similar papers to paper_index (excluding itself)."""
    similarities = similarity_matrix[paper_index]
    # torch.argsort descending — no [::-1] needed (torch doesn't support negative steps)
    sorted_indices = torch.argsort(similarities, descending=True)
    return sorted_indices[1 : top_n + 1]  # skip index 0 (self)


def print_paper_titles(titles: list[str], query: str) -> None:
    """Print paper titles with indices, highlighting those that match the query."""
    print("Papers:")
    for i, title in enumerate(titles):
        if query.lower() in title.lower():
            print(f"  [{i}] {title}")

def main(input_file: str, query: str) -> None:
    df = pd.read_csv(input_file)
    abstracts = df["abstract"].fillna("").tolist()
    titles = df["title"].fillna("").tolist()

    sim_matrix = build_embedding_similarity_matrix(abstracts)

    print_paper_titles(titles, query)

    paper_index = int(input("Enter paper index: "))
    similar_indices = find_similar_papers(sim_matrix, paper_index)

    print(f"Top {TOP_N} papers similar to paper {paper_index} ({df['title'][paper_index]}):")
    for idx in similar_indices.tolist():
        print(f"  [{idx}] {df['title'][idx]} (similarity: {sim_matrix[paper_index][idx]:.4f})")

