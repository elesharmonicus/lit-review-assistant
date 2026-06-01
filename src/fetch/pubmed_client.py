# Search PubMed for a query term
# Return the first PubMed ID, title and abstract of the first result
import requests
import xml.etree.ElementTree as ET
import time
import pandas as pd
import logging
from src.constants import PUBMED_BASE_URL, RATE_LIMIT_SLEEP
from src.models import Paper

logger = logging.getLogger(__name__)

def search_pubmed(query: str, max_results: int, sort_mode: str) -> list[Paper]:
    """Search PubMed for a query term and return a list of results with PubMed ID, title, abstract, year, authors, journal, and DOI."""
    results = []
    url = f"{PUBMED_BASE_URL}/esearch.fcgi?db=pubmed&term={query}&sort={sort_mode}&retmax={max_results}&retmode=json"
    try:
        response = requests.get(url)
    except requests.RequestException as e:
        logger.warning("Request error during PubMed search: %s", e)
        return results
    data = response.json()
    if 'esearchresult' in data and 'idlist' in data['esearchresult'] and len(data['esearchresult']['idlist']) > 0:
        for pubmed_id in data['esearchresult']['idlist'][:max_results]:
            logger.info("Fetching %s...", pubmed_id)
            url = f"{PUBMED_BASE_URL}/efetch.fcgi?db=pubmed&id={pubmed_id}&rettype=abstract&retmode=xml"
            try:
                response = requests.get(url)
            except requests.RequestException as e:
                logger.warning("Request error for ID %s: %s, skipping.", pubmed_id, e)
                continue
            time.sleep(RATE_LIMIT_SLEEP)  # stay within NCBI's 3 requests/sec limit
            if not response.content.strip().startswith(b'<'):
                logger.warning("Unexpected response for ID %s, skipping.", pubmed_id)
                continue
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError as e:
                logger.warning("XML parse error for ID %s: %s, skipping.", pubmed_id, e)
                continue
            title_parts = []
            for el in root.findall('.//ArticleTitle'):
                title_parts.append(''.join(el.itertext()).strip())
            title = ' '.join(title_parts)
            abstract_parts = []
            for el in root.findall('.//AbstractText'):
                label = el.get('Label')
                text = ''.join(el.itertext()).strip()
                if text:
                    abstract_parts.append(f"{label}: {text}" if label else text)
            abstract = ' '.join(abstract_parts)
            year_text = root.findtext('.//PubDate/Year', '')
            year = int(year_text) if year_text.isdigit() else None
            authors = [author.findtext('LastName', '') + " " + author.findtext('ForeName', '') for author in root.findall('.//Author')]
            journal = root.findtext('.//Journal/Title', '')
            doi = root.findtext('.//ELocationID[@EIdType="doi"]', '')
            results.append(Paper(title=title, abstract=abstract, authors=authors, year=year, doi=doi, journal=journal))
    return results

def save_results(results: list[Paper], directory: str) -> None:
    """Save results to a CSV file."""
    df = pd.DataFrame([paper.__dict__ for paper in results], columns=['title', 'abstract', 'authors', 'year', 'doi', 'journal'])
    df.to_csv(directory, index=False)

def print_results(results: list[Paper]) -> None:
    """Print results to the console."""
    for result in results:
        print(f"Title: {result.title}")
        print(f"Abstract: {result.abstract}")
        print(f"Year: {result.year}")
        print(f"Authors: {', '.join(result.authors)}")
        print(f"Journal: {result.journal}")
        print(f"DOI: {result.doi}")
        print()

def main(query: str, max_results: int, sort_mode: str, directory: str) -> None:
    """Run the PubMed search and save results."""
    results = search_pubmed(query, max_results, sort_mode)
    print_results(results[0:5])  # print first 5 results
    save_results(results, directory)
