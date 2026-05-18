import pandas as pd 
import torch
print(torch.__version__)

from sklearn.feature_extraction.text import CountVectorizer 
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv('data/pubmed_results.csv')
abstracts = df['abstract'].fillna("").tolist()

#Convert abstracts into count vectors with pytorch
vectorizer = CountVectorizer(stop_words="english",max_features=1000)

X = vectorizer.fit_transform(abstracts)
X_tensor = torch.tensor(X.toarray(), dtype=torch.float32) 

# Compute cosine similarity between abstracts
cosine_sim = cosine_similarity(X_tensor)

paper_index = 0
similarities = cosine_sim[paper_index]
similar_indices = similarities.argsort()[::-1][1:6]  # Get indices of top 5 similar papers (excluding itself)
print(f"Top 5 papers similar to paper {paper_index} ({df['title'][paper_index]}):")
for idx in similar_indices:
    print(f"Paper {idx}: {df['title'][idx]} (Similarity: {similarities[idx]:.4f})") 