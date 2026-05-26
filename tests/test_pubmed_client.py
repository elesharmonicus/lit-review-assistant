import pandas as pd
import tempfile, os
from src.fetch.pubmed_client import save_results

def test_save_results_creates_csv():
    data = [{"pubmed_id": "123", "title": "Test", "abstract": "x",
             "year": "2024", "authors": [], "journal": "J", "doi": ""}]
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name
    save_results(data, path)
    df = pd.read_csv(path)
    assert len(df) == 1
    assert df["title"][0] == "Test"
    os.unlink(path)