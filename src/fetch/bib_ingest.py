import bibtexparser
import pandas as pd
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from src.fetch.crossref_client import fetch_abstract_crossref, fetch_abstract_by_title
from src.models import Paper
import logging
logger = logging.getLogger(__name__)

def _short(title: str, n: int = 55) -> str:
    """Truncate title for log output."""
    return title if len(title) <= n else title[:n].rstrip() + "…"


def load_bib(bib_file: str) -> list[Paper]:
    """Parse a .bib file and return a list of normalised Paper objects.

    For entries without an abstract, attempts to fetch one from CrossRef
    using the DOI (preferred) or title search (fallback).
    """
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    with open(bib_file) as f:
        bib_data = bibtexparser.load(f, parser=parser)

    papers = []
    fetched, missing = 0, []

    for entry in bib_data.entries:
        paper = {
            "title": entry.get("title", ""),
            "abstract": entry.get("abstract", ""),
            "authors": entry.get("author", ""),
            "year": entry.get("year", ""),
            "journal": entry.get("journal", ""),
            "doi": entry.get("doi", ""),
        }
        if not paper["abstract"]:
            short = _short(paper["title"])
            if paper["doi"]:
                logger.info("  [DOI]   %s", short)
                paper["abstract"] = fetch_abstract_crossref(paper["doi"])
            elif paper["title"]:
                logger.info("  [title] %s", short)
                paper["abstract"] = fetch_abstract_by_title(paper["title"])

            if paper["abstract"]:
                fetched += 1
            else:
                missing.append(paper["title"])
    
        papers.append(Paper.from_dict(paper))

    logger.info("Abstract fetch complete — %d fetched, %d missing", fetched, len(missing))
    for t in missing:
        logger.warning("  No abstract: %s", _short(t))

    return papers


def main(bib_path: str, output_file: str) -> None:
    """Load .bib file and save as CSV."""
    papers = load_bib(bib_path)
    df = pd.DataFrame([paper.__dict__ for paper in papers], columns=['title', 'abstract', 'authors', 'year', 'journal', 'doi'])
    df.to_csv(output_file, index=False)