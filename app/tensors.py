from pathlib import Path
import pandas as pd
import torch
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_PATH = Path(__file__).parent.parent / "data" / "pubmed_results.csv"
MAX_FEATURES = 1000
TOP_N = 5


def build_similarity_matrix(abstracts: list[str]) -> torch.Tensor:
    """Vectorize abstracts and compute a dot-product similarity matrix using torch."""
    vectorizer = TfidfVectorizer(stop_words="english", max_features=MAX_FEATURES)
    X = vectorizer.fit_transform(abstracts)
    # Convert to float tensor: shape (num_papers, vocab_size)
    X_tensor = torch.tensor(X.toarray(), dtype=torch.float32)
    # Normalise rows so dot product equals cosine similarity
    norms = X_tensor.norm(dim=1, keepdim=True).clamp(min=1e-8)
    X_norm = X_tensor / norms
    return X_norm @ X_norm.T  # shape (num_papers, num_papers)


def find_similar_papers(similarity_matrix: torch.Tensor, paper_index: int, top_n: int = TOP_N) -> torch.Tensor:
    """Return indices of the top_n most similar papers to paper_index (excluding itself)."""
    similarities = similarity_matrix[paper_index]
    # torch.argsort descending — no [::-1] needed (torch doesn't support negative steps)
    sorted_indices = torch.argsort(similarities, descending=True)
    return sorted_indices[1 : top_n + 1]  # skip index 0 (self)


def main(input_file: str, query: str) -> None:
    df = pd.read_csv(input_file)
    abstracts = df["abstract"].fillna("").tolist()

    sim_matrix = build_similarity_matrix(abstracts)

    paper_index = int(input("Enter paper index: "))
    similar_indices = find_similar_papers(sim_matrix, paper_index)

    print(f"Top {TOP_N} papers similar to paper {paper_index} ({df['title'][paper_index]}):")
    for idx in similar_indices.tolist():
        print(f"  [{idx}] {df['title'][idx]} (similarity: {sim_matrix[paper_index][idx]:.4f})")

