import bibtexparser
import pandas as pd
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

def load_bib(bib_file: str) -> list[dict]:
    """Parse a .bib file and return list of normalised paper dicts."""
    parser = BibTexParser()
    parser.customization = convert_to_unicode   
    with open(bib_file) as f:
        bib_data = bibtexparser.load(f, parser=parser)
    papers = []
    for entry in bib_data.entries:
        paper = {
            "title": entry.get("title", ""),
            "abstract": entry.get("abstract", ""),
            "authors": entry.get("author", ""),
            "year": entry.get("year", ""),
            "journal": entry.get("journal", ""),
            "doi": entry.get("doi", ""),
        }
        papers.append(paper)
    return papers


def main(bib_path: str, output_file: str) -> None:
    """Load .bib file and save as CSV."""
    papers = load_bib(bib_path)
    df = pd.DataFrame(papers, columns=['title', 'abstract', 'authors', 'year', 'journal', 'doi'])
    df.to_csv(output_file, index=False)